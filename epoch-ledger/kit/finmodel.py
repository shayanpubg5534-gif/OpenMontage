"""Epoch Ledger financial model: one source of truth for every figure an episode shows, and the validator that checks
the figures against it.

A scenario is a daily cash simulation of one business: an opening balance, one-off and recurring flows, loans with
their financing cost, and an optional overdraft limit. The bank balance never falls below the overdraft limit: a
payment that cannot be made becomes an *unpaid obligation* (the funding gap) and is settled, oldest first, when cash
arrives. This is how a real account behaves, and it keeps two different things apart on screen: a negative balance
(an overdraft, which costs money and must be arranged) and a shortfall (bills the business cannot pay).

    sc = Scenario.from_dict(json.load(open("finance.json")))
    model = simulate(sc)                       # daily balances, unpaid obligations, events
    model.metric("peak_shortfall")             # values for diagrams come from here
    issues = validate(sc, figures)             # list of Issue(rule, severity, message)

Rules (severity "error" fails the gate):
  FIN-FIGURE      a figure on screen differs from the model value it claims to show.
  FIN-ARITH       revenue − costs ≠ profit for a cycle.
  FIN-NEG-BALANCE a negative bank balance is shown without an overdraft that large: a funding gap drawn as a balance.
  FIN-RECURRING   the deal recurs (e.g. "a month") but the costs that recur during the payment delay are not modelled.
  FIN-LOAN-SIZE   a loan is smaller than the peak shortfall it is meant to cover.
  FIN-FIN-COST    a loan has no rate or fee and no stated reason for being free.
  FIN-COST-SHOWN  (warning) a loan with a financing cost appears, but no figure shows the cost.
Original implementation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

TOL = 1.0   # dollars


@dataclass
class Flow:
    day: int
    amount: float           # + in, − out
    label: str
    kind: str = "other"     # revenue | cost | financing | interest | other


@dataclass
class Recurring:
    label: str
    amount: float
    kind: str
    first_day: int
    every_days: int
    count: int

    def flows(self) -> list[Flow]:
        return [Flow(self.first_day + i * self.every_days, self.amount, f"{self.label} #{i + 1}", self.kind) for i in range(self.count)]


@dataclass
class Loan:
    label: str
    principal: float
    draw_day: int
    repay_day: int
    annual_rate: float | None = None
    fee: float = 0.0
    zero_cost_reason: str = ""

    @property
    def interest(self) -> float:
        r = self.annual_rate or 0.0
        return round(self.principal * r * (self.repay_day - self.draw_day) / 365 + self.fee, 2)

    def flows(self) -> list[Flow]:
        out = [Flow(self.draw_day, self.principal, f"{self.label} drawn", "financing"),
               Flow(self.repay_day, -self.principal, f"{self.label} repaid", "financing")]
        if self.interest:
            out.append(Flow(self.repay_day, -self.interest, f"{self.label} interest and fees", "interest"))
        return out


@dataclass
class Scenario:
    name: str
    opening_balance: float
    horizon_days: int
    overdraft_limit: float = 0.0
    deal_recurs: bool = False           # the narration describes a repeating deal ("a month", "every week")
    cycle_days: int = 30                # the deal's period when it recurs
    flows: list[Flow] = field(default_factory=list)
    recurring: list[Recurring] = field(default_factory=list)
    loans: list[Loan] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "Scenario":
        return cls(name=d["name"], opening_balance=d["opening_balance"], horizon_days=d["horizon_days"],
                   overdraft_limit=d.get("overdraft_limit", 0.0), deal_recurs=d.get("deal_recurs", False),
                   cycle_days=d.get("cycle_days", 30),
                   flows=[Flow(**f) for f in d.get("flows", [])],
                   recurring=[Recurring(**r) for r in d.get("recurring", [])],
                   loans=[Loan(**x) for x in d.get("loans", [])])

    def all_flows(self, financing: bool = True) -> list[Flow]:
        fl = list(self.flows) + [f for r in self.recurring for f in r.flows()]
        if financing:
            fl += [f for x in self.loans for f in x.flows()]
        # within a day: money in first, then payments (a same-day receipt can pay a same-day bill)
        return sorted((f for f in fl if 0 <= f.day <= self.horizon_days), key=lambda f: (f.day, -f.amount))


@dataclass
class Model:
    scenario: Scenario
    balance: list[float]                # end-of-day bank balance, day 0..horizon
    unpaid: list[float]                 # end-of-day unpaid obligations (the funding gap)
    events: list[tuple[int, str, float, float, float]]   # (day, label, amount, balance after, unpaid after)

    def metric(self, key: str, day: int | None = None) -> float:
        sc = self.scenario
        if key == "opening_balance":
            return sc.opening_balance
        if key == "revenue_per_cycle":
            return _per_cycle(sc, "revenue")
        if key == "cost_per_cycle":
            return -_per_cycle(sc, "cost")
        if key == "profit_per_cycle":
            return _per_cycle(sc, "revenue") + _per_cycle(sc, "cost")
        if key == "peak_shortfall":
            return max(self.unpaid)
        if key == "balance":
            return self.balance[day]
        if key == "unpaid":
            return self.unpaid[day]
        if key == "interest_total":
            return sum(x.interest for x in sc.loans)
        if key == "loan_principal":
            return sum(x.principal for x in sc.loans)
        raise KeyError(key)


def _per_cycle(sc: Scenario, kind: str) -> float:
    """The amount of one cycle of a kind: a recurring stream's amount, or the sum of one-off flows of that kind."""
    rec = [r for r in sc.recurring if r.kind == kind]
    if rec:
        return sum(r.amount for r in rec)
    return sum(f.amount for f in sc.flows if f.kind == kind)


def simulate(sc: Scenario, financing: bool = True) -> Model:
    bal, unpaid, ev = float(sc.opening_balance), [], []     # unpaid: FIFO list of [label, amount]
    floor = -abs(sc.overdraft_limit)
    flows = sc.all_flows(financing)
    by_day: dict[int, list[Flow]] = {}
    for f in flows:
        by_day.setdefault(f.day, []).append(f)
    balances, gaps = [], []
    for d in range(sc.horizon_days + 1):
        for f in by_day.get(d, []):
            if f.amount >= 0:
                bal += f.amount
                while unpaid and bal - unpaid[0][1] >= floor - 1e-9:      # settle old bills, oldest first
                    bal -= unpaid.pop(0)[1]
                if unpaid and bal > floor:                                 # partly settle the oldest
                    part = bal - floor
                    unpaid[0][1] -= part
                    bal = floor
            else:
                need = -f.amount
                pay = max(0.0, min(need, bal - floor))
                bal -= pay
                if need - pay > 1e-9:
                    unpaid.append([f.label, need - pay])
            ev.append((d, f.label, f.amount, round(bal, 2), round(sum(u[1] for u in unpaid), 2)))
        balances.append(round(bal, 2))
        gaps.append(round(sum(u[1] for u in unpaid), 2))
    return Model(sc, balances, gaps, ev)


@dataclass
class Issue:
    rule: str
    severity: str
    message: str

    def __str__(self) -> str:
        return f"{self.severity.upper():7} {self.rule:16} {self.message}"


def validate(sc: Scenario, figures: list[dict]) -> list[Issue]:
    """figures: what the episode shows, e.g. {"id": "short", "shows": "peak_shortfall", "value": 18000} or
    {"id": "bal", "shows": "balance", "day": 0, "value": -18000, "financing": false}. `shows` names a model metric."""
    issues: list[Issue] = []
    with_fin, without_fin = simulate(sc, True), simulate(sc, False)
    usd = lambda v: ("−" if v < 0 else "") + f"${abs(v):,.0f}"

    # arithmetic of one cycle
    rev, cost, prof = with_fin.metric("revenue_per_cycle"), with_fin.metric("cost_per_cycle"), with_fin.metric("profit_per_cycle")
    shown = {f.get("shows"): f for f in figures}
    if "profit_per_cycle" in shown and abs(shown["profit_per_cycle"]["value"] - (rev - cost)) > TOL:
        issues.append(Issue("FIN-ARITH", "error", f"profit shown {usd(shown['profit_per_cycle']['value'])} ≠ revenue {usd(rev)} − costs {usd(cost)}"))

    # recurring deal: costs must recur through the payment delay
    if sc.deal_recurs:
        if not any(r.kind == "cost" for r in sc.recurring):
            issues.append(Issue("FIN-RECURRING", "error", "the deal recurs but its costs are modelled once"))
        if not any(r.kind == "revenue" for r in sc.recurring):
            issues.append(Issue("FIN-RECURRING", "error", "the deal recurs but its revenue is modelled once"))

    # figures against the model
    for f in figures:
        key = f.get("shows")
        model = with_fin if f.get("financing", True) else without_fin
        try:
            want = model.metric(key, f.get("day"))
        except (KeyError, IndexError, TypeError):
            issues.append(Issue("FIN-FIGURE", "error", f"{f['id']}: unknown metric {key!r}"))
            continue
        if key == "balance" and f["value"] < -TOL and -f["value"] > abs(sc.overdraft_limit) + TOL:
            issues.append(Issue("FIN-NEG-BALANCE", "error",
                                f"{f['id']}: shows a bank balance of {usd(f['value'])} with an overdraft limit of {usd(sc.overdraft_limit)}; "
                                f"the balance stops at {usd(-abs(sc.overdraft_limit))} and the rest is unpaid bills (a shortfall)"))
            continue
        if abs(f["value"] - want) > TOL:
            extra = ""
            if key in ("peak_shortfall", "balance", "unpaid") and sc.deal_recurs:
                extra = " (the recurring costs that fall due before the first payment are included in the model)"
            issues.append(Issue("FIN-FIGURE", "error", f"{f['id']}: shows {usd(f['value'])}, model says {usd(want)}{extra}"))

    # loans
    gap = without_fin.metric("peak_shortfall")
    for x in sc.loans:
        if x.principal + abs(sc.overdraft_limit) < gap - TOL:
            issues.append(Issue("FIN-LOAN-SIZE", "error", f"{x.label}: {usd(x.principal)} does not cover the peak shortfall of {usd(gap)}"))
        if not x.annual_rate and not x.fee and not x.zero_cost_reason:
            issues.append(Issue("FIN-FIN-COST", "error", f"{x.label}: no interest rate or fee, and no reason given for a free loan"))
        elif x.interest and "interest_total" not in shown:
            issues.append(Issue("FIN-COST-SHOWN", "warning", f"{x.label}: costs {usd(x.interest)} in interest and fees, but no figure shows it"))
    return issues


def check_file(path: str) -> tuple[Scenario, list[dict], list[Issue]]:
    """Load a finance.json ({"scenario": {...}, "figures": [...]}) and validate it."""
    import json
    d = json.loads(open(path, encoding="utf-8").read())
    sc = Scenario.from_dict(d["scenario"])
    return sc, d.get("figures", []), validate(sc, d.get("figures", []))


if __name__ == "__main__":
    import sys
    sc, figs, issues = check_file(sys.argv[1])
    m = simulate(sc)
    print(f"{sc.name}: peak shortfall {m.metric('peak_shortfall'):,.0f} with financing, "
          f"{simulate(sc, False).metric('peak_shortfall'):,.0f} without; lowest balance {min(m.balance):,.0f}")
    for i in issues:
        print(i)
    sys.exit(1 if any(i.severity == "error" for i in issues) else 0)

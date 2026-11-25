"""One source of truth for every financial figure a sequence shows (cash piles, counters, charts, runway).

Illustrative figures for a fictional company are fine — but they must agree with each other on every screen.
Build a Ledger once per sequence, then draw *every* indicator from it; tests assert the arithmetic.

    led = Ledger(start=13, unit=1.0, currency="$", scale="M")
    led.spend({"ADVERTISING": 2, "PAYROLL": 1, "SERVERS": 1}); led.earn({"REVENUE": 1})
    led.monthly_burn          # 3.0      (spending - revenue)
    led.balance               # 10.0     (after one month)
    led.runway_months         # 3.33
    led.fmt(10)               # "$10M"
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Ledger:
    start: float
    unit: float = 1.0                 # value of one bundle / pile unit (for physical cash piles)
    currency: str = "$"
    scale: str = "M"
    spending: dict = field(default_factory=dict)
    income: dict = field(default_factory=dict)
    events: list = field(default_factory=list)     # (label, delta) after the first month — e.g. funding received

    def spend(self, items: dict) -> "Ledger":
        self.spending.update(items); return self

    def earn(self, items: dict) -> "Ledger":
        self.income.update(items); return self

    @property
    def total_spending(self) -> float: return sum(self.spending.values())
    @property
    def total_income(self) -> float: return sum(self.income.values())
    @property
    def monthly_burn(self) -> float: return self.total_spending - self.total_income
    @property
    def balance(self) -> float: return self.start - self.total_spending + self.total_income
    @property
    def runway_months(self) -> float: return self.balance / self.monthly_burn if self.monthly_burn > 0 else float("inf")

    def balance_after(self, months: float, injections: dict | None = None) -> float:
        """Cash after `months` more months of burn from the end of month one, with {month: amount} injections."""
        b = self.balance
        for m in range(int(months)):
            b -= self.monthly_burn
            b += (injections or {}).get(m + 1, 0)
        return b

    def curve(self, months: int, injections: dict | None = None) -> list[tuple[float, float]]:
        """(month, balance) points from month 0 (= after the first month), floored at 0, for line charts."""
        pts, b = [(0.0, self.balance)], self.balance
        for m in range(1, months + 1):
            b -= self.monthly_burn
            if injections and m in injections:
                pts.append((float(m), max(0.0, b)))
                b += injections[m]
            pts.append((float(m), max(0.0, b)))
        return pts

    def units(self, value: float) -> int:
        return int(round(value / self.unit))

    def fmt(self, v: float, signed: bool = False) -> str:
        s = "-" if v < 0 else ("+" if signed and v > 0 else "")
        a = abs(v)
        n = f"{a:.1f}".rstrip("0").rstrip(".")
        return f"{s}{self.currency}{n}{self.scale}"

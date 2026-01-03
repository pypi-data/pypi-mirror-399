from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class ModelRow:
    model: str
    type: str
    accuracy_mean: float
    accuracy_std: float
    f1: float
    sensitivity: float
    specificity: float
    n_over_80: int
    n_total: int = 109

    @property
    def acc_str(self) -> str:
        return f"{self.accuracy_mean:.2f} ± {self.accuracy_std:.2f}"

    @property
    def n80_str(self) -> str:
        return f"{self.n_over_80}/{self.n_total}"


def render_ascii_table(title: str, rows: Iterable[ModelRow]) -> str:
    rows = list(rows)

    headers = ["Model", "Type", "Accuracy (%)", "F1 Score", "Sensitivity", "Specificity", "N>80%"]

    data: List[List[str]] = []
    for r in rows:
        data.append([
            r.model,
            r.type,
            r.acc_str,
            f"{r.f1:.4f}",
            f"{r.sensitivity:.4f}",
            f"{r.specificity:.4f}",
            r.n80_str,
        ])

    col_widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    def fmt_row(cells: List[str]) -> str:
        return "  ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(cells))

    header_line = fmt_row(headers)
    sep_line = "=" * len(header_line)

    lines = []
    lines.append(f"TABLE :  {title}")
    lines.append(sep_line)
    lines.append(header_line)
    lines.append("-" * len(header_line))
    for row in data:
        lines.append(fmt_row(row))
    lines.append(sep_line)
    return "\n".join(lines)


def print_fair_model_comparison(rows: Iterable[ModelRow], title: str = "Fair Model Comparison") -> None:
    print(render_ascii_table(title=title, rows=rows))


def eegsignal(rows, title: str = "EEG Signal Model Comparison") -> None:
    """
    User-friendly alias for printing EEG model comparison tables.
    """
    print_fair_model_comparison(rows, title=title)





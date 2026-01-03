from dataclasses import dataclass


@dataclass
class Step:
    value: int
    technique: str
    explanation: str
    cells: list[tuple[int, int]] | None = None

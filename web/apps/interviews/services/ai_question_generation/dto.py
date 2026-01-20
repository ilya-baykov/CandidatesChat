from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedQuestion:
    text: str
    order: int
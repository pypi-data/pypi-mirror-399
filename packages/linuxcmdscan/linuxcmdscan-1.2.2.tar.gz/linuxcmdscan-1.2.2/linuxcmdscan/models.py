from dataclasses import dataclass

@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    command: str
    detected_command: str
    category: str
    severity: str
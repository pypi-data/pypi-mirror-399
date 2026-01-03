import re
from dataclasses import dataclass

@dataclass(frozen=True)
class CommandRule:
    name: str
    pattern: re.Pattern
    category: str
    severity: str

def _r(expr):
    return re.compile(expr, re.IGNORECASE | re.VERBOSE)

COMMAND_REGISTRY = [
    CommandRule("terraform", _r(r"(?<![\w])terraform\s+(init|plan|apply|destroy|validate|fmt|state|import)\b"), "infra", "critical"),
    CommandRule("kubectl", _r(r"(?<![\w])kubectl(\s+\S+)+"), "infra", "high"),
    CommandRule("helm", _r(r"(?<![\w])helm(\s+\S+)+"), "infra", "high"),
    CommandRule("ansible", _r(r"(?<![\w])ansible(-playbook)?(\s+\S+)+"), "infra", "high"),
    CommandRule("ssh", _r(r"(?<![\w])ssh\s+\S+@\S+"), "network", "high"),
    CommandRule("scp", _r(r"(?<![\w])scp\s+\S+"), "network", "high"),
    CommandRule("rsync", _r(r"(?<![\w])rsync\s+\S+"), "network", "high"),
    CommandRule("curl", _r(r"(?<![\w])curl\s+https?://\S+"), "network", "medium"),
    CommandRule("wget", _r(r"(?<![\w])wget\s+https?://\S+"), "network", "medium"),
    CommandRule("mkdir", _r(r"(?<![\w])mkdir(\s+-[a-zA-Z]+)*\s+\S+"), "filesystem", "low"),
    CommandRule("cp", _r(r"(?<![\w])cp(\s+-[a-zA-Z]+)*\s+\S+"), "filesystem", "low"),
    CommandRule("mv", _r(r"(?<![\w])mv\s+\S+"), "filesystem", "medium"),
    CommandRule("rm", _r(r"(?<![\w])rm(\s+-[rf]+)*\s+\S+"), "filesystem", "critical"),
]
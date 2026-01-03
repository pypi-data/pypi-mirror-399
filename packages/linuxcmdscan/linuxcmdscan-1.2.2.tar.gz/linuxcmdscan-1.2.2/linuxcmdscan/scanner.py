import os
from .registry import COMMAND_REGISTRY
from .models import Finding

SKIP_DIRS = {".git",".terraform","node_modules","dist","build","__pycache__", ".venv","venv"}
ALLOWED_EXTENSIONS = {".sh",".bash",".yaml",".yml",".tf",".tfvars",".md",".txt",".cfg",".ini",".py",".js",".ts"}

class RepositoryScanner:
    def scan(self, root, excluded=set()):
        findings=[]
        for r,d,f in os.walk(root):
            d[:] = [x for x in d if x not in SKIP_DIRS and os.path.join(r,x) not in excluded]
            for name in f:
                if os.path.splitext(name)[1].lower() in ALLOWED_EXTENSIONS:
                    p=os.path.join(r,name)
                    try:
                        with open(p,"r",encoding="utf-8",errors="ignore") as fh:
                            for ln,line in enumerate(fh,1):
                                s=line.strip()
                                if not s: continue
                                for rule in COMMAND_REGISTRY:
                                    if rule.pattern.search(s):
                                        findings.append(Finding(p,ln,s,rule.name,rule.category,rule.severity))
                                        break
                    except Exception:
                        pass
        return findings
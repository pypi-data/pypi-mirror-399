from dataclasses import dataclass

@dataclass
class Config:
    max_crumbs: int = 5000
    on_crash: str = "stderr"   # stderr | file | none | callable
    output_file: str = "statecrumbs.json"
    include_timestamp: bool = True
    include_thread: bool = True

config = Config()

from pathlib import Path

CACHE_FILE = Path(Path.home() / ".cache" / "shadowScanner" / "cache.json")
CHECKPOINT_FILE = Path(Path.home() / ".cache" / "shadowScanner" / "checkpoint.json")
TARGETS_FILE = Path(Path.home() / ".cache" / "shadowScanner" / "targets.json")
FINDINGS_FILE = Path(Path.home() / ".cache" / "shadowScanner" / "findings.json")
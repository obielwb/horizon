import json
from pathlib import Path
from typing import List, Dict, Any

class StartupDB:
    """A simple JSON-based database for storing and retrieving startups."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        if not self.db_path.exists():
            self.db_path.write_text(json.dumps([]))

    def load_startups(self) -> List[str]:
        """Load all startup names from the database."""
        with open(self.db_path, 'r') as f:
            return json.load(f)

    def save_startups(self, startups: List[str]) -> None:
        """Save a list of startup names to the database."""
        with open(self.db_path, 'w') as f:
            json.dump(startups, f, indent=2)

    def add_startups(self, new_startups: List[Dict[str, Any]]) -> None:
        """Add new startups to the database, avoiding duplicates."""
        existing_startups = self.load_startups()
        added_startups = False
        for startup in new_startups:
            name = startup.get("name", "").lower().strip()
            if name and name not in existing_startups:
                existing_startups.append(name)
                added_startups = True
        
        if added_startups:
            self.save_startups(existing_startups)

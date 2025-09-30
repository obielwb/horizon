# Updated database.py
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List
class StartupDB:
    """A proper JSON-based database for storing and retrieving full startup data."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        if not self.db_path.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.db_path.write_text(json.dumps([], indent=2))

    def load_startups(self) -> List[Dict[str, Any]]:
        """Load all startups from the database."""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_startups(self, startups: List[Dict[str, Any]]) -> None:
        """Save startups to the database."""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(startups, f, indent=2, ensure_ascii=False)

    def add_startups(self, new_startups: List[Dict[str, Any]]) -> int:
        """Add new startups to the database, avoiding duplicates."""
        existing_startups = self.load_startups()
        existing_names = {s.get('name', '').lower().strip() for s in existing_startups}
        
        added_count = 0
        for startup in new_startups:
            name = startup.get('name', '').lower().strip()
            if name and name not in existing_names:
                # Standardize the startup data structure
                standardized_startup = self._standardize_startup_data(startup)
                existing_startups.append(standardized_startup)
                existing_names.add(name)
                added_count += 1
        
        if added_count > 0:
            self.save_startups(existing_startups)
        
        return added_count

    def _standardize_startup_data(self, startup: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize startup data structure."""
        standardized = {
            'name': startup.get('name', startup.get('Company Name', '')),
            'website': startup.get('website', startup.get('Website', '')),
            'description': startup.get('description', startup.get('Description', '')),
            'location': startup.get('location', startup.get('Location', '')),
            'country': startup.get('country', ''),
            'technology': startup.get('technology', startup.get('AI Technology Focus', '')),
            'market': startup.get('market', startup.get('Target Market', '')),
            'founded': startup.get('founded', startup.get('Founding Year', '')),
            'milestones': startup.get('milestones', startup.get('Key Milestones', '')),
            'source_url': startup.get('source_url', startup.get('Source URL', '')),
            'discovery_date': startup.get('discovery_date', datetime.now().isoformat())
        }
        # Remove empty values
        return {k: v for k, v in standardized.items() if v}
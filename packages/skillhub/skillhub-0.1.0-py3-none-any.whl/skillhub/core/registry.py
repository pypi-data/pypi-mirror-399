"""Registry interaction module."""
import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Optional

class Registry:
    """Handles interaction with the SkillHub registry."""

    def __init__(self, config):
        self.config = config
        self.index_url = config.get('index_url')
        self.raw_url = config.get('registry_raw_url')
        self.cache_dir = config.get_cache_dir()
        self.cache_ttl = config.get('cache_ttl', 3600)
        self._index = None

    def fetch_index(self, force_refresh=False):
        """Fetch the skills index from registry."""
        cache_file = self.cache_dir / 'index.json'

        # Check cache
        if cache_file.exists() and not force_refresh:
            # Check if cache is still valid
            cache_age = time.time() - cache_file.stat().st_mtime
            if cache_age < self.cache_ttl:
                try:
                    with open(cache_file, 'r') as f:
                        self._index = json.load(f)
                    return self._index
                except Exception as e:
                    print(f"Warning: Failed to load cache: {e}")

        # Fetch from remote
        try:
            response = requests.get(self.index_url, timeout=30)
            response.raise_for_status()
            self._index = response.json()

            # Cache it
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'w') as f:
                json.dump(self._index, f, indent=2)

            return self._index

        except requests.exceptions.RequestException as e:
            # If fetch fails, try to use cached version even if expired
            if cache_file.exists():
                print(f"Warning: Failed to fetch index, using cached version: {e}")
                with open(cache_file, 'r') as f:
                    self._index = json.load(f)
                return self._index
            else:
                raise Exception(f"Failed to fetch index and no cache available: {e}")

    def search(self, query: str) -> List[Dict]:
        """Search skills by query."""
        if not self._index:
            self.fetch_index()

        query_lower = query.lower()
        results = []

        for skill in self._index.get('skills', []):
            # Search in name, description, tags, category
            matches = (
                query_lower in skill.get('name', '').lower() or
                query_lower in skill.get('description', '').lower() or
                query_lower in skill.get('category', '').lower() or
                any(query_lower in tag.lower() for tag in skill.get('tags', []))
            )

            if matches:
                results.append(skill)

        return results

    def get_skill(self, skill_name: str) -> Optional[Dict]:
        """Get skill by exact name."""
        if not self._index:
            self.fetch_index()

        for skill in self._index.get('skills', []):
            if skill.get('name') == skill_name:
                return skill

        return None

    def list_all(self) -> List[Dict]:
        """Get all skills."""
        if not self._index:
            self.fetch_index()

        return self._index.get('skills', [])

    def list_categories(self) -> Dict[str, List[Dict]]:
        """Get skills grouped by category."""
        skills = self.list_all()

        categories = {}
        for skill in skills:
            category = skill.get('category', 'uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(skill)

        return categories

    def download_skill(self, skill_name: str, destination: str) -> Path:
        """Download skill content to destination."""
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found in registry")

        # Download from raw URL
        skill_url = skill.get('url')
        if not skill_url:
            raise ValueError(f"No URL found for skill '{skill_name}'")

        try:
            response = requests.get(skill_url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download skill: {e}")

        # Save to destination
        dest_path = Path(destination)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(response.text)

        return dest_path

    def get_stats(self) -> Dict:
        """Get registry statistics."""
        if not self._index:
            self.fetch_index()

        skills = self._index.get('skills', [])
        categories = self.list_categories()

        return {
            'total_skills': len(skills),
            'total_categories': len(categories),
            'categories': {cat: len(skills) for cat, skills in categories.items()},
            'version': self._index.get('version', 'unknown'),
            'generated': self._index.get('generated', 'unknown'),
        }

"""Configuration management for SkillHub CLI."""
import os
import json
from pathlib import Path

# Default configuration values
DEFAULT_CONFIG = {
    'registry_url': 'https://github.com/v1k22/skillhub-registry',
    'registry_raw_url': 'https://raw.githubusercontent.com/v1k22/skillhub-registry/main',
    'cache_dir': str(Path.home() / '.skillhub' / 'cache'),
    'skills_dir': str(Path.home() / '.skillhub' / 'skills'),
    'index_url': 'https://raw.githubusercontent.com/v1k22/skillhub-registry/main/index.json',
    'cache_ttl': 3600,  # Cache TTL in seconds (1 hour)
}

class Config:
    """Configuration manager for SkillHub CLI."""

    def __init__(self):
        self.config_dir = Path.home() / '.skillhub'
        self.config_file = self.config_dir / 'config.json'
        self.config = self.load()

    def load(self):
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults (in case new keys were added)
                return {**DEFAULT_CONFIG, **config}
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
                return DEFAULT_CONFIG.copy()
        else:
            # Create config directory and file
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.save(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

    def save(self, config=None):
        """Save configuration to file."""
        if config is None:
            config = self.config

        self.config_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config: {e}")

    def get(self, key, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value and save."""
        self.config[key] = value
        self.save(self.config)

    def reset(self):
        """Reset configuration to defaults."""
        self.config = DEFAULT_CONFIG.copy()
        self.save(self.config)

    def get_cache_dir(self):
        """Get cache directory path."""
        cache_dir = Path(self.get('cache_dir'))
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def get_skills_dir(self):
        """Get skills directory path."""
        skills_dir = Path(self.get('skills_dir'))
        skills_dir.mkdir(parents=True, exist_ok=True)
        return skills_dir

"""Skill validation logic."""
import yaml
import re
from pathlib import Path
from typing import Tuple, List

# Required fields in metadata
REQUIRED_FIELDS = ['name', 'version', 'description', 'category', 'tags', 'author']

# Required sections in skill body
REQUIRED_SECTIONS = [
    '## Overview',
    '## Task Description',
    '## Steps',
    '## Expected Output',
    '## Success Criteria'
]

def validate_skill(skill_path: str) -> Tuple[List[str], List[str]]:
    """
    Validate a skill file and return list of errors and warnings.

    Args:
        skill_path: Path to the skill markdown file

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []

    skill_path = Path(skill_path)

    # Check file exists
    if not skill_path.exists():
        errors.append(f"File not found: {skill_path}")
        return errors, warnings

    # Read file
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        errors.append(f"Failed to read file: {e}")
        return errors, warnings

    # Check frontmatter exists
    if not content.startswith('---'):
        errors.append("Missing YAML frontmatter")
        return errors, warnings

    # Parse frontmatter
    try:
        parts = content.split('---', 2)
        if len(parts) < 3:
            errors.append("Invalid YAML frontmatter structure")
            return errors, warnings

        frontmatter = parts[1]
        body = parts[2]

        data = yaml.safe_load(frontmatter)
        if not data:
            errors.append("Empty YAML frontmatter")
            return errors, warnings

        metadata = data.get('metadata', {})
        if not metadata:
            errors.append("Missing 'metadata' section")
            return errors, warnings

    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML syntax: {e}")
        return errors, warnings
    except Exception as e:
        errors.append(f"Failed to parse frontmatter: {e}")
        return errors, warnings

    # Validate required metadata fields
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            errors.append(f"Missing required field: '{field}'")
        elif not metadata[field]:
            errors.append(f"Empty required field: '{field}'")

    # Validate name format (kebab-case)
    if 'name' in metadata:
        name = metadata['name']
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            errors.append(f"Name must be kebab-case: '{name}'")

    # Validate version format (semver)
    if 'version' in metadata:
        version = metadata['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"Version must be semver (X.Y.Z): '{version}'")

    # Validate description length
    if 'description' in metadata:
        desc_len = len(metadata['description'])
        if desc_len < 50:
            warnings.append(f"Description too short ({desc_len} chars)")
        elif desc_len > 200:
            warnings.append(f"Description too long ({desc_len} chars)")

    # Validate tags
    if 'tags' in metadata:
        tags = metadata['tags']
        if not isinstance(tags, list):
            errors.append("Tags must be a list")
        elif len(tags) < 3:
            warnings.append(f"Should have at least 3 tags")
        elif len(tags) > 10:
            warnings.append(f"Should have at most 10 tags")

    # Validate required sections
    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"Missing required section: '{section}'")

    return errors, warnings

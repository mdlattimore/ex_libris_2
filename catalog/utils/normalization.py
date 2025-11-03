import re

def normalize_sort_title(title: str) -> str:
    """Lowercase and strip leading articles ('a', 'an', 'the') for sorting."""
    if not title:
        return ""
    return re.sub(r'^(the|an|a)\s+', '', title.strip(), flags=re.I).lower()

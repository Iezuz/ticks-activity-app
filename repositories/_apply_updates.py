from typing import Any, Dict, List, Optional


def _apply_updates(obj: Any, updates: Dict[str, Any], exclude: Optional[List[str]] = None):

    exclude = exclude or []
    for k, v in updates.items():
        if k in exclude:
            continue
        if not hasattr(obj, k):
            continue
        setattr(obj, k, v)

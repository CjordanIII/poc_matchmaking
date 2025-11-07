from pathlib import Path
import json
from typing import List, Dict, Any, Optional
from json_parser import atomic_write_json


def is_profile_valid(uuid: str, users: List[Dict[str, Any]], *args, force_write: bool = False, **kwargs) -> List[Dict[str, Any]]:
    """Filter and persist valid profiles.

    Behavior:
    - Valid profiles: not banned and (is_verified OR is_active/email_verified if present).
    - If no valid profiles found, falls back to a copy of the input `users` to avoid empty outputs.
    - Writes JSON atomically to `filter_data/location_isvalid.json` (pretty-printed).

    Args:
        uuid: user id to check (used only for logging/lookup here).
        users: list of profile dicts.
        force_write: if True, overwrite existing file even if present.

    Returns:
        The list of filtered profiles that were written.
    """
    FILE_LOCATION = Path("filter_data/location_isvalid.json")

    # Basic input validation
    if not isinstance(users, list):
        raise TypeError("users must be a list of dicts")

    # Debugging helpers (keeps logs concise)
    total = len(users)
    first_user_preview = users[0] if total > 0 else None

    # Find the requested user if present (useful for caller debugging)
    requested = None
    if uuid:
        for u in users:
            # check common id keys
            if str(u.get("uuid") or u.get("id") or u.get("username")) == str(uuid):
                requested = u
                break

    # Determine validity: prefer explicit flags if present
    def _is_valid(u: Dict[str, Any]) -> bool:
        # skip banned users
        if u.get("is_banned"):
            return False
        # prefer explicit verification if available
        if "is_verified" in u:
            return bool(u.get("is_verified"))
        # otherwise fallback to active + email verified if those fields exist
        if "is_active" in u or "email_verified" in u:
            return bool(u.get("is_active", True)) and bool(u.get("email_verified", False))
        # default permissive: consider user valid unless banned
        return True

    # Build unique location dicts from the input users (so output groups are stable)
    keys = ['city', 'country', 'state', 'region', 'county']
    locations = []
    for user in users:
        loc = {}
        for key in keys:
            val = user.get(key)
            if not val:
                continue
            if isinstance(val, (list, tuple)):
                cleaned = [str(v).strip() for v in val if v]
                if cleaned:
                    loc[key] = cleaned
            else:
                loc[key] = str(val).strip()
        if loc:
            locations.append(loc)

    # Deduplicate location dicts robustly using canonical JSON
    seen = set()
    unique_locations = []
    for d in locations:
        key = json.dumps(d, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            unique_locations.append(d)

    # For each unique location, collect uuids of valid users that match that location
    result = []
    for loc in unique_locations:
        matched_uuids = []
        for user in users:
            match = True
            for key, val in loc.items():
                user_val = user.get(key)
                if not user_val:
                    match = False
                    break
                if isinstance(user_val, (list, tuple)):
                    user_vals = [str(v).strip() for v in user_val if v]
                    # val might be list or single value; normalize to string compare
                    if isinstance(val, (list, tuple)):
                        # require any overlap
                        if not any(str(v).strip() in user_vals for v in val):
                            match = False
                            break
                    else:
                        if str(val).strip() not in user_vals:
                            match = False
                            break
                else:
                    if isinstance(val, (list, tuple)):
                        if str(user_val).strip() not in [str(v).strip() for v in val]:
                            match = False
                            break
                    else:
                        if str(user_val).strip() != str(val).strip():
                            match = False
                            break
            if match and _is_valid(user):
                matched_uuids.append(user.get('uuid') or user.get('id') or user.get('username'))

        if matched_uuids:
            loc_with_uuids = dict(loc)
            loc_with_uuids['users'] = matched_uuids
            result.append(loc_with_uuids)

    # Persist the grouped result atomically; skip write if file exists and force_write is False
    if force_write or not FILE_LOCATION.exists():
        atomic_write_json(result, FILE_LOCATION, indent=2, sort_keys=True)

    return result
from pathlib import Path
from json_parser import to_json_string
import os

def filter_by_location(data, *args, **kwargs):
    """
    Filters a list of user data dictionaries by location.
    Writes:
    - location_keys.json: unique location dicts
    - filtered_by_location.json: each location with matching user UUIDs
    """
    FILE_LOCATION = Path("filter_data/location_keys.json")
    keys = ['city', 'country', 'state', 'region', 'county']
    FILE_LOCATION.parent.mkdir(parents=True, exist_ok=True)

    locations = []

    # 🔍 Build location dicts from each user
    for user in data:
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

    # 🧼 Deduplicate location dicts
    location = [dict(t) for t in {tuple(d.items()) for d in locations}]

    # 📝 Save location keys if not already saved
    if not FILE_LOCATION.exists():
        to_json_string(location, location=str(FILE_LOCATION))

    # 🔁 Match users to each location by UUID only
    result = []
    for loc in location:
        matched_uuids = []
        for user in data:
            match = True
            for key, val in loc.items():
                user_val = user.get(key)
                if not user_val:
                    match = False
                    break
                if isinstance(user_val, (list, tuple)):
                    user_vals = [str(v).strip() for v in user_val if v]
                    if str(val).strip() not in user_vals:
                        match = False
                        break
                else:
                    if str(user_val).strip() != str(val).strip():
                        match = False
                        break
            if match:
                matched_uuids.append(user.get('uuid'))

        loc_with_uuids = dict(loc)
        loc_with_uuids['users'] = matched_uuids
        result.append(loc_with_uuids)

    # 💾 Save final result
    to_json_string(result, location=str(FILE_LOCATION.parent / "filtered_by_location.json"))
    return result
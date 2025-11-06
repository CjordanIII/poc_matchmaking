
from pathlib import Path
from json_parser import to_json_string
import os 

def filter_by_location(data,*args, **kwargs):
    """
    Filters a list of user data dictionaries by location.
    """
    FILE_LOCATION = Path("filter_data/location_keys.json")
    keys = ['city','country','state','region','county']
    FILE_LOCATION.parent.mkdir(parents=True, exist_ok=True)

    locations = []
    # build one dict per user containing any available location fields
    for user in data:
        loc = {}
        for key in keys:
            val = user.get(key)
            if not val:
                continue
            # normalize lists and single values; keep as list if it's a list
            if isinstance(val, (list, tuple)):
                # remove empty items and normalize strings
                cleaned = [str(v).strip() for v in val if v]
                if cleaned:
                    loc[key] = cleaned
            else:
                loc[key] = str(val).strip()
        if loc:
            
            locations.append(loc)
# remove duplicate location dicts
    location = [dict(t) for t in {tuple(d.items()) for d in locations}]
    # write file only if it does not already exist
    if not FILE_LOCATION.exists():
        to_json_string(location, location=str(FILE_LOCATION))

    # return the list of location dicts for further use
    return location
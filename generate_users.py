"""
Generator script for synthetic dating-app users and questions.
Writes:
 - data/questions.json
 - data/users.json

Run with: python generate_users.py
"""
import json
import random
import uuid
from datetime import datetime, timedelta, timezone

# Config
NUM_USERS = 1000
NUM_QUESTIONS = 150
OUTPUT_USERS = "data/users.json"
OUTPUT_QUESTIONS = "data/questions.json"
SEED = 42
random.seed(SEED)

# Small helper pools
first_names = [
    "Alex","Taylor","Jordan","Casey","Riley","Jamie","Morgan","Sam","Chris","Drew",
    "Pat","Cameron","Quinn","Avery","Skyler","Blake","Dakota","Devin","Emerson","Elliot"
]
last_names = [
    "Nguyen","Patel","Garcia","Smith","Johnson","Brown","Davis","Miller","Wilson","Moore",
    "Taylor","Anderson","Thomas","Jackson","White","Harris","Martin","Thompson","Lee","Perez"
]
interests_pool = [
    "hiking","cooking","reading","traveling","yoga","gaming","music","movies","fitness","running",
    "photography","dancing","painting","gardening","cycling","tech","startups","coffee","board games","crafts",
    "meditation","languages","history","politics","art","volunteering","camping","climbing","sailing","tennis",
    "basketball","soccer","fishing","skiing","snowboarding","surfing","baking","coding","brewing","theater"
]

# Cities/clusters to create location clusters (lat, lon approximate)
cities = [
    {"city":"San Francisco","state":"CA","country":"USA","lat":37.7749,"lon":-122.4194},
    {"city":"New York","state":"NY","country":"USA","lat":40.7128,"lon":-74.0060},
    {"city":"Austin","state":"TX","country":"USA","lat":30.2672,"lon":-97.7431},
    {"city":"Seattle","state":"WA","country":"USA","lat":47.6062,"lon":-122.3321},
    {"city":"Miami","state":"FL","country":"USA","lat":25.7617,"lon":-80.1918},
    {"city":"Chicago","state":"IL","country":"USA","lat":41.8781,"lon":-87.6298},
    {"city":"Denver","state":"CO","country":"USA","lat":39.7392,"lon":-104.9903},
    {"city":"Los Angeles","state":"CA","country":"USA","lat":34.0522,"lon":-118.2437},
    {"city":"London","state":"","country":"UK","lat":51.5074,"lon":-0.1278},
    {"city":"Toronto","state":"ON","country":"Canada","lat":43.6532,"lon":-79.3832}
]

# Use single-letter codes to match Django model choices: M, F, O (other), N (prefer not / any)
genders = ["M", "F", "O"]
preference_options = ["M", "F", "O", "N"]

# Generate a varied question list programmatically (mix of binary, scale, multi-choice, free text)
binary_templates = [
    "Do you enjoy outdoor activities?",
    "Are you a morning person?",
    "Do you like pets?",
    "Do you smoke?",
    "Do you drink alcohol socially?",
    "Do you want kids someday?",
    "Do you enjoy traveling internationally?",
    "Do you work remotely?",
    "Do you enjoy cooking at home?",
    "Do you exercise at least 3x/week?"
]
scale_templates = [
    "How important is religion/spirituality in your life (1-5)?",
    "How social are you on a scale of 1-5?",
    "How much do you enjoy trying new foods (1-5)?",
    "How adventurous are you (1-5)?",
    "How much do you value financial stability (1-5)?",
    "How important are politics to your dating decisions (1-5)?",
    "How tidy are you on average (1-5)?",
    "How often do you go to concerts (1-5)?",
    "How much do you like pets (1-5)?",
    "How much do you value personal space (1-5)?"
]
mc_templates = [
    ("Favorite weekend activity", ["Hiking","Going to a cafe","Watching movies","Attending events","Sleeping in","Party/Clubbing","Visiting museums","Board games"]),
    ("Preferred vacation style", ["Backpacking","Beach resort","City sightseeing","Road trip","Cruise","Staycation"]),
    ("Favorite music genre", ["Pop","Rock","Hip-hop","EDM","Classical","Jazz","Country","Indie"]),
    ("Diet preference", ["Omnivore","Vegetarian","Vegan","Pescatarian","Keto","No preference"]),
    ("Living situation", ["Living alone","Roommates","With partner","With family","Student housing"]) 
]
free_templates = [
    "Write a one-sentence bio about yourself.",
    "What are you looking for in a partner? (short answer)",
    "Describe your perfect weekend.",
    "What's a fun fact about you?",
    "What's an embarrassing moment you can laugh about now?"
]

questions = []
qid = 1
# Add binary questions
for t in binary_templates:
    questions.append({"id": qid, "key": f"q{qid}", "text": t, "type": "binary"})
    qid += 1
# Add scale questions
for t in scale_templates:
    questions.append({"id": qid, "key": f"q{qid}", "text": t, "type": "scale", "scale_min": 1, "scale_max": 5})
    qid += 1
# Add multi-choice
for t, opts in mc_templates:
    questions.append({"id": qid, "key": f"q{qid}", "text": t, "type": "multi-choice", "options": opts})
    qid += 1
# Add free text
for t in free_templates:
    questions.append({"id": qid, "key": f"q{qid}", "text": t, "type": "free-text"})
    qid += 1

# If we need more to reach NUM_QUESTIONS, create paraphrased lifestyle/opinion questions
extra_templates = [
    "Do you enjoy attending live sporting events?",
    "Do you prefer nights out or nights in?",
    "Are you open to long-distance relationships?",
    "Would you relocate for a partner?",
    "Do you enjoy spontaneous trips?",
    "How do you feel about a partner's exes?",
    "Do you like sharing passwords with partner?",
    "Do you prefer texting or calling?",
    "Do you like debating ideas?",
    "Would you date someone with children?",
]
while qid <= NUM_QUESTIONS:
    t = random.choice(extra_templates)
    qtype = random.choice(["binary","scale","multi-choice","free-text"])
    if qtype == "binary":
        questions.append({"id": qid, "key": f"q{qid}", "text": t, "type": "binary"})
    elif qtype == "scale":
        questions.append({"id": qid, "key": f"q{qid}", "text": t + " (1-5)", "type": "scale", "scale_min": 1, "scale_max": 5})
    elif qtype == "multi-choice":
        opts = random.choice([opt for _, opt in mc_templates])
        questions.append({"id": qid, "key": f"q{qid}", "text": t, "type": "multi-choice", "options": opts})
    else:
        questions.append({"id": qid, "key": f"q{qid}", "text": t + " (short answer)", "type": "free-text"})
    qid += 1

# Save questions
with open(OUTPUT_QUESTIONS, "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

# Helper to random jitter lat/lon
def jitter(lat, lon, km=10):
    # crude jitter: ~0.01 degrees ~ 1.1km. We'll scale accordingly
    scale = km / 100.0
    return lat + random.uniform(-scale, scale), lon + random.uniform(-scale, scale)

# Answer generator based on question type
def answer_for_question(q):
    t = q["type"]
    if t == "binary":
        return random.choice([True, False])
    if t == "scale":
        return random.randint(q.get("scale_min",1), q.get("scale_max",5))
    if t == "multi-choice":
        return random.choice(q.get("options",[]))
    if t == "free-text":
        # short templated answers for variety
        samples = [
            "Love exploring new things.",
            "Looking for someone kind and funny.",
            "I work hard and play harder.",
            "I value honesty and communication.",
            "Big on traveling and food adventures.",
            "Just here to meet new people and see what happens.",
        ]
        return random.choice(samples)
    return None

# Generate users clustered by city to create similar/different groups
users = []
for i in range(NUM_USERS):
    uid = str(uuid.uuid4())
    first = random.choice(first_names)
    last = random.choice(last_names)
    username = f"{first.lower()}.{last.lower()}{random.randint(1,9999)}"
    age = random.randint(18, 65)
    # gender uses single-letter codes to match Django choices
    gender = random.choices(genders, weights=[0.45,0.45,0.1])[0]
    pref = random.choices(preference_options, weights=[0.45,0.45,0.05,0.05])[0]
    city = random.choices(cities, weights=[1.2,1.5,0.7,0.8,0.6,0.9,0.5,1.1,0.4,0.4])[0]
    lat, lon = jitter(city["lat"], city["lon"], km=random.uniform(0.5,12.0))
    is_verified = random.random() < 0.25
    is_banned = random.random() < 0.01
    credits = random.randint(0, 500)
    min_age = max(18, age - random.randint(2,8))
    max_age = min(70, age + random.randint(2,8))
    # interests and tags: some users share heavy overlap (to create "similar" clusters)
    # create cluster bias: people in same city more likely to share interests
    interest_count = random.randint(4,10)
    # bias: pick one or two dominant interests per city
    city_bias = []
    # deterministic bias per city name
    bias_seed = sum(ord(c) for c in city['city']) % len(interests_pool)
    city_bias = [interests_pool[bias_seed % len(interests_pool)], interests_pool[(bias_seed+3) % len(interests_pool)]]
    # build interests
    interests = set(random.sample(interests_pool, 2))
    if random.random() < 0.7:
        interests.update(city_bias)
    while len(interests) < interest_count:
        interests.add(random.choice(interests_pool))
    interests = list(interests)

    # answers: produce mapping of question id -> answer
    # map answers by question key (e.g. "q1") to make them easier to reference
    answers = {}
    for q in questions:
        # small probability of leaving blank
        if random.random() < 0.02:
            continue
        answers[q['key']] = answer_for_question(q)

    # small set of photos placeholders
    photo_count = random.randint(1,5)
    photos = [f"https://example.com/photos/{uid}/{n}.jpg" for n in range(1,photo_count+1)]

    user = {
        # match Django model field names where possible
        "uuid": uid,
        "username": username,
        "display_name": f"{first} {last}",
        "email": f"{username}@example.com",
        "is_verified": is_verified,
        "is_banned": is_banned,
        "credits": credits,
        "gender": gender,
        "preference_gender": pref,
        "age": age,
        "minage_preference": min_age,
        "maxage_preference": max_age,
        "identity_ref": None if not is_verified else f"idprov_{random.randint(100000,999999)}",
        "city": city['city'],
        "state": city['state'],
        "region": city.get('state',''),
        "country": city['country'],
        "lat": round(lat,6),
        "lon": round(lon,6),
        "bio": random.choice([
            "Love good coffee and better conversations.",
            "Startup person, weekend hiker.",
            "Bookworm who also loves rock climbing.",
            "I take travel photos and try new recipes.",
            "Dog person. Seeking someone to share tacos with.",
            "Musician, gym-goer, and occasional baker.",
        ]),
        "interests": interests,
        "answers": answers,
        "photos": photos,
        # use timezone-aware timestamps to align with Django timezone usage
        "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(0,1000))).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "last_login": (datetime.now(timezone.utc) - timedelta(minutes=random.randint(0,60*24))).isoformat(),
        "language": random.choice(["en","es","fr","de","pt","it"]),
        "timezone": random.choice(["America/Los_Angeles","America/New_York","Europe/London","America/Chicago","America/Denver","America/Toronto"]) 
    }
    users.append(user)

# Add a few intentionally similar "test users" for algorithm debugging
for t in [
    {"username":"alice.sf","city":"San Francisco","age":28,"gender":"F","pref":"M"},
    {"username":"bob.sf","city":"San Francisco","age":30,"gender":"M","pref":"F"},
    {"username":"carol.ny","city":"New York","age":27,"gender":"F","pref":"M"}
]:
    uid = str(uuid.uuid4())
    city = next((c for c in cities if c['city'] == t['city']), random.choice(cities))
    lat, lon = jitter(city['lat'], city['lon'])
    user = {
        "uuid": uid,
        "username": t['username'],
        "display_name": t['username'].split('.')[0].capitalize(),
        "email": f"{t['username']}@example.com",
        "is_verified": True,
        "is_banned": False,
        "credits": 100,
        "gender": t['gender'],
        "preference_gender": t['pref'],
        "age": t['age'],
        "minage_preference": max(18, t['age']-3),
        "maxage_preference": t['age']+3,
        "identity_ref": f"idprov_{random.randint(100000,999999)}",
        "city": city['city'],
        "state": city['state'],
        "region": city.get('state',''),
        "country": city['country'],
        "lat": round(lat,6),
        "lon": round(lon,6),
        "bio": "Test account for matching",
        "interests": ["hiking","coffee","music"],
        "answers": {"q1": True, "q2": 4},
        "photos": [f"https://example.com/photos/{uid}/1.jpg"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "last_login": datetime.now(timezone.utc).isoformat(),
        "language": "en",
        "timezone": "America/Los_Angeles"
    }
    users.append(user)

# Save users
with open(OUTPUT_USERS, "w", encoding="utf-8") as f:
    json.dump(users, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(users)} users to {OUTPUT_USERS}")
print(f"Wrote {len(questions)} questions to {OUTPUT_QUESTIONS}")

import re
import random

# Clean text: lowercasing + removing punctuation
def clean_text(text):
    return re.sub(r"[^\w\s]", "", text.lower())

# Simulated Named Entity Recognition
def extract_entities(text):
    mock_entities = {
        "aditya-l1": "Mission",
        "gaganyaan": "Mission",
        "pslv": "Vehicle",
        "mars": "Planet",
        "velocity": "Physics",
        "chandrayaan": "Mission"
    }
    found = []
    for k, v in mock_entities.items():
        if k in text.lower():
            found.append((k, v, round(random.uniform(0.88, 0.99), 2)))
    return found

# Simulated intent detection
def detect_intent(text):
    intents = {
        "compute": ["what is", "calculate", "speed of", "mass of"],
        "mission_info": ["mission", "launch", "spacecraft", "objective"],
        "vehicle_query": ["vehicle", "launched", "used by", "rocket"]
    }
    for intent, keywords in intents.items():
        if any(k in text.lower() for k in keywords):
            return intent
    return "general"

# Smart routing
def decide_engine(intent):
    if intent == "compute":
        return "wolfram"
    elif intent == "vehicle_query":
        return "kg"
    else:
        return "rag"
import json
import random
from datetime import datetime, timedelta

# Configuration
NUM_ACTIVITIES = 150
START_DATE = datetime(2023, 10, 1)
END_DATE = datetime(2023, 12, 31)
ALL_DATES = [START_DATE + timedelta(days=x) for x in range((END_DATE - START_DATE).days + 1)]

# Sample data templates
ACTIVITY_TYPES = [
    "Fitness routine/exercise",
    "Food consumption",
    "Medication consumption",
    "Therapy",
    "Consultation"
]

FREQUENCIES = [
    "daily",
    "3 times a week",
    "twice a week", 
    "once a week",
    "twice a month",
    "once a month"
]

EQUIPMENT = [
    "Running Shoes", "Yoga Mat", "Dumbbells", "Resistance Bands",
    "Blood Pressure Monitor", "Sauna", "Ice Bath Tub", "Stationary Bike",
    "Weight Scale", "Food Scale", "Pill Organizer"
]

SPECIALISTS = [
    "Personal Trainer", "Nutritionist", "Physical Therapist",
    "Yoga Instructor", "Health Coach", "Therapy Specialist",
    "General Practitioner"
]

ALLIED_HEALTH = [
    "Physiotherapist", "Occupational Therapist", "Dietitian",
    "Speech Therapist"
]

LOCATIONS = [
    "Home", "Local Park", "Gym", "Clinic", "Virtual",
    "Spa Center", "Rehabilitation Center"
]

def generate_activities(num_activities):
    activities = []
    activity_descriptions = set()
    
    for i in range(1, num_activities+1):
        activity_type = random.choice(ACTIVITY_TYPES)
        description = generate_description(activity_type, i)
        
        # Ensure unique descriptions
        while description in activity_descriptions:
            description = generate_description(activity_type, i)
        activity_descriptions.add(description)
        
        activity = {
            "id": i,
            "activity_type": activity_type,
            "description": description,
            "frequency": random.choice(FREQUENCIES),
            "details": generate_details(activity_type),
            "facilitator": random.choice(SPECIALISTS),
            "location": random.choice(LOCATIONS),
            "remote_possible": random.choice([True, False]),
            "prep_needed": generate_prep_needs(activity_type),
            "backup_activities": generate_backups(activity_type),
            "adjustments": generate_adjustment(activity_type),
            "metrics": generate_metrics(activity_type),
            "required_equipment": generate_equipment(activity_type),
            "required_specialists": [random.choice(SPECIALISTS)],
            "required_allied_health": random.choices(ALLIED_HEALTH, k=random.randint(0,1))
        }
        activities.append(activity)
    return activities

def generate_description(activity_type, idx):
    descriptors = {
        "Fitness routine/exercise": ["Morning", "Evening", "Cardio", "Strength", "Recovery"],
        "Food consumption": ["Breakfast", "Lunch", "Dinner", "Snack", "Supplement"],
        "Medication consumption": ["Vitamin", "Prescription", "Supplement", "Dose"],
        "Therapy": ["Sauna", "Ice Bath", "Physical", "Respiratory", "Occupational"],
        "Consultation": ["Nutrition", "Progress", "Therapy", "Medication"]
    }
    base = random.choice(descriptors[activity_type]) + " " + random.choice(["Session", "Routine", "Check", "Plan"])
    return f"{base} #{idx}"

def generate_details(activity_type):
    details = {
        "Fitness routine/exercise": "Maintain HR between {} bpm".format(random.randint(100, 160)),
        "Food consumption": "Ensure {} intake".format(random.choice(["protein", "fiber", "vitamins"])),
        "Medication consumption": "Take {} tablet(s)".format(random.randint(1, 3)),
        "Therapy": "Session duration: {} minutes".format(random.randint(15, 60)),
        "Consultation": "Discuss progress and next steps"
    }
    return details[activity_type]

def generate_availability(items, date_list, available_prob=0.7, is_equipment=True):
    availability = []
    for item in items:
        available_dates = [
            d.strftime("%Y-%m-%d") 
            for d in date_list 
            if random.random() < available_prob
        ]
        availability.append({
            "equipment" if is_equipment else "specialist": item,
            "available_dates": available_dates
        })
    return availability

def generate_prep_needs(activity_type):
    preps = {
        "Fitness routine/exercise": ["Proper attire", "Water bottle"],
        "Food consumption": ["Meal prepped", "Supplements ready"],
        "Medication consumption": ["Pill organizer filled"],
        "Therapy": ["Towels", "Water"],
        "Consultation": ["Questions prepared"]
    }
    return random.choice(preps[activity_type])

def generate_backups(activity_type):
    backups = {
        "Fitness routine/exercise": ["Walking", "Bodyweight exercises"],
        "Food consumption": ["Meal replacement shake", "Pre-packaged healthy meal", "Nutritional smoothie"],
        "Medication consumption": ["Liquid alternative", "Alternative dosage form (e.g., chewable)", "Delayed administration with doctor's approval"],
        "Therapy": ["Stretching routine", "Guided meditation session", "Self-massage routine"],
        "Consultation": ["Email follow-up", "Phone consultation", "Text message update"]
    }
    return random.sample(backups[activity_type], k=random.randint(1,2))

def generate_adjustment(activity_type):
    return f"Reschedule within {random.randint(1,3)} days if missed"

def generate_metrics(activity_type):
    metrics = {
        "Fitness routine/exercise": ["Heart rate", "Duration"],
        "Food consumption": ["Calories", "Macronutrients"],
        "Medication consumption": ["Dosage", "Timing"],
        "Therapy": ["Recovery rate", "Perceived exertion"],
        "Consultation": ["Progress notes", "Next steps"]
    }
    return ", ".join(random.sample(metrics[activity_type], k=2))

def generate_equipment(activity_type):
    equipment_map = {
        "Fitness routine/exercise": ["Running Shoes", "Yoga Mat", "Dumbbells"],
        "Therapy": ["Sauna", "Ice Bath Tub"],
        "Consultation": []
    }
    return random.choices(
        equipment_map.get(activity_type, []), 
        k=random.randint(0,1 if activity_type == "Therapy" else 0)
    )

def generate_travel_plans():
    return {
        "client_id": 1,
        "travel_dates": random.sample(
            [d.strftime("%Y-%m-%d") for d in ALL_DATES],
            k=random.randint(5, 10)
        )
    }

# Generate and save data
if __name__ == "__main__":
    print("Generating sample data...")
    
    # Generate activities
    activities = generate_activities(NUM_ACTIVITIES)
    with open('activities.json', 'w') as f:
        json.dump(activities, f, indent=2)
    
    # Generate equipment availability
    equipment_availability = generate_availability(EQUIPMENT, ALL_DATES)
    equip_total = []
    for item in equipment_availability: equip_total.extend(item['available_dates']) 
    equip_total = set(equip_total)
    with open('equipment_availability.json', 'w') as f:
        json.dump(equipment_availability, f, indent=2)
    
    # Generate specialist availability
    specialist_availability = generate_availability(SPECIALISTS, ALL_DATES, is_equipment=False)
    sp_total = []
    for item in specialist_availability: sp_total.extend(item['available_dates']) 
    sp_total = set(sp_total)
    with open('specialists_availability.json', 'w') as f:
        json.dump(specialist_availability, f, indent=2)
    
    # Generate travel plans
    travel_plans = generate_travel_plans()
    with open('travel_plans.json', 'w') as f:
        json.dump(travel_plans, f, indent=2)

    metadata = {
        'NUM_ACTIVITIES': NUM_ACTIVITIES,
        'ACTIVITY_TYPES': ACTIVITY_TYPES,
        'EQUIPMENT': EQUIPMENT,
        'SPECIALISTS': SPECIALISTS,
        'equip_total': len(equip_total),
        'sp_total': len(sp_total),
        'travel_total': len(travel_plans['travel_dates']),
    }

    with open('metadata_.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("Data generation complete!")
    print(f"Generated files: activities.json ({NUM_ACTIVITIES} activities)")
    print(f"Equipment availability: {len(equip_total)} total item availability")
    print(f"Specialist availability: {len(sp_total)} total professional availability")
    print(f"Travel plans: {len(travel_plans['travel_dates'])} dates")
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
import random

def load_data():
    with open('activities.json') as f:
        activities = json.load(f)
    with open('equipment_availability.json') as f:
        equipment = json.load(f)
    with open('specialists_availability.json') as f:
        specialists = json.load(f)
    with open('travel_plans.json') as f:
        travel = json.load(f)
    return activities, equipment, specialists, travel

def preprocess_availability(equipment, specialists):
    equipment_avail = {item['equipment']: set(item['available_dates']) for item in equipment}
    specialists_avail = {item['specialist']: set(item['available_dates']) for item in specialists}
    return equipment_avail, specialists_avail

def parse_frequency(frequency):
    freq_map = {
        'daily': 7,
        '3 times a week': 3,
        'twice a week': 2,
        'once a week': 1,
        'twice a month': 0.5,
        'once a month': 0.25
    }
    return freq_map.get(frequency, 0)

def get_weekly_target(frequency, weeks_remaining):
    if frequency >= 1:
        return int(frequency)
    # For fractional frequencies, decide if we should schedule the activity in this week.
    return 1 if (frequency * weeks_remaining) % 1 >= 0.5 else 0

def create_entry(activity, date, is_backup=False, is_travel=False, is_adjustment=False):
    entry = {
        'date': date,
        'activity': activity['description'],
        'type': activity['activity_type'],
        'original_activity': activity['description'],
        'is_backup': is_backup,
        'is_travel': is_travel,
        'is_adjustment': is_adjustment,
        'details': activity['adjustments'] if is_adjustment or is_travel else activity['details'],
        'facilitator': "N/A" if is_adjustment or is_travel else activity['facilitator'],
        'location': "Travel" if is_travel else ("N/A" if is_adjustment else activity['location'])
    }
    return entry

def check_availability(activity, date_str, equipment_avail, specialists_avail, is_backup=False):
    # Skip availability checks for backup activities
    if is_backup:
        return True
        
    for eq in activity['required_equipment']:
        if date_str not in equipment_avail.get(eq, set()):
            return False
    for spec in activity['required_specialists']:
        if date_str not in specialists_avail.get(spec, set()):
            return False
    return True

def schedule_week(activity, week_dates, equipment_avail, specialists_avail, travel_dates, backup_queue, activity_map, calendar, weekly_target):
    scheduled = []
    targets_remaining = weekly_target
    # Shuffle the week dates randomly to avoid always picking the first day
    shuffled_dates = deque(sorted(week_dates, key=lambda x: random.random()))
    
    while shuffled_dates and targets_remaining > 0:
        date_obj = shuffled_dates.popleft()
        date_str = date_obj.strftime('%Y-%m-%d')
        
        # Check daily limit: skip if already reached max activities for that day.
        if len(calendar[date_str]) >= 5:
            continue

        # If the date is a travel day, mark it accordingly.
        if date_str in travel_dates:
            entry = create_entry(activity, date_str, is_travel=True)
            scheduled.append(entry)
            backup_queue.append(date_str)
            targets_remaining -= 1
            continue
            
        if check_availability(activity, date_str, equipment_avail, specialists_avail):
            entry = create_entry(activity, date_str)
            scheduled.append(entry)
            targets_remaining -= 1
        else:
            backup_found = False
            for backup_desc in activity['backup_activities']:
                backup_activity = activity_map.get(backup_desc.strip(), None)
                if backup_activity:
                    # Skip availability check for backups
                    entry = create_entry(backup_activity, date_str, is_backup=True)
                    scheduled.append(entry)
                    targets_remaining -= 1
                    backup_found = True
                    break
            if not backup_found:
                backup_queue.append(date_str)
    
    return scheduled

def schedule_activities(activities, equipment_avail, specialists_avail, travel_dates, start_date, end_date):
    calendar = defaultdict(list)
    activity_map = {act['description']: act for act in activities}
    backup_queue = deque()
    
    current_date = start_date
    while current_date <= end_date:
        week_end = current_date + timedelta(days=6)
        week_end = min(week_end, end_date)
        week_dates = [current_date + timedelta(days=i) for i in range((week_end - current_date).days + 1)]
        
        for activity in activities:
            freq = parse_frequency(activity['frequency'])
            weeks_remaining = ((end_date - current_date).days // 7) + 1
            weekly_target = get_weekly_target(freq, weeks_remaining)
            # Only schedule if the weekly target is at least 1.
            if weekly_target < 1:
                continue
            
            week_schedule = schedule_week(
                activity, 
                week_dates, 
                equipment_avail, 
                specialists_avail, 
                travel_dates,
                backup_queue,
                activity_map,
                calendar,     # pass current calendar for daily count check
                weekly_target # schedule the intended number of occurrences for the week
            )
            
            for entry in week_schedule:
                calendar[entry['date']].append(entry)
        
        current_date = week_end + timedelta(days=1)
    
    return calendar

def main():
    start_date = datetime(2023, 10, 1)
    end_date = datetime(2023, 12, 31)
    activities, equipment, specialists, travel = load_data()
    equipment_avail, specialists_avail = preprocess_availability(equipment, specialists)
    travel_dates = list(set(travel['travel_dates']))
    
    calendar = schedule_activities(activities, equipment_avail, specialists_avail, travel_dates, start_date, end_date)

    with open('calender.json', 'w') as f:
        json.dump(calendar, f, indent=2)
    
    print("Personalized Weekly Schedule (showing one sample day):")
    # Print one sample day with its scheduled activities
    for date in sorted(calendar.keys()):
        print("#" * len("Showing the first entry for example"))
        print("Showing the first entry for example")
        print("#" * len("Showing the first entry for example"))
        print(f"\nDate: {date}")
        for idx, entry in enumerate(calendar[date], 1):
            tags = []
            if entry['is_backup']: tags.append("Backup")
            if entry['is_travel']: tags.append("Travel")
            if entry['is_adjustment']: tags.append("Adjustment")
            
            print(f"Activity {idx}: {entry['activity']} ({entry['type']})")
            print(f"Status: {', '.join(tags) if tags else 'Scheduled'}")
            print(f"Facilitator: {entry['facilitator']}")
            print(f"Details: {entry['details']}")
            print(f"Location: {entry['location']}")
            print("-" * 80)
        break

if __name__ == "__main__":
    main()

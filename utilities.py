import json
import os
from datetime import datetime, timedelta

def load_dishes():
    try:
        with open(os.getenv("DATA_FILE"), "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_dishes(dishes):
    with open(os.getenv("DATA_FILE"), "w") as file:
        json.dump(dishes, file, indent=4)

# Scheduler data functions
def load_schedule():
    """Load schedule data from schedule.json"""
    schedule_file = os.path.join(os.path.dirname(os.getenv("DATA_FILE")), "schedule.json")
    try:
        with open(schedule_file, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"schedule": {}}

def save_schedule(schedule_data):
    """Save schedule data to schedule.json"""
    schedule_file = os.path.join(os.path.dirname(os.getenv("DATA_FILE")), "schedule.json")
    with open(schedule_file, "w") as file:
        json.dump(schedule_data, file, indent=4)

def load_ingredient_tracking():
    """Load ingredient tracking data from ingredient_tracking.json"""
    tracking_file = os.path.join(os.path.dirname(os.getenv("DATA_FILE")), "ingredient_tracking.json")
    try:
        with open(tracking_file, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"ingredient_acquisitions": []}

def save_ingredient_tracking(tracking_data):
    """Save ingredient tracking data to ingredient_tracking.json"""
    tracking_file = os.path.join(os.path.dirname(os.getenv("DATA_FILE")), "ingredient_tracking.json")
    with open(tracking_file, "w") as file:
        json.dump(tracking_data, file, indent=4)

def get_dish_ingredients(dish_name):
    """Extract ingredients list from dishes.json for a specific dish"""
    dishes = load_dishes()
    for dish in dishes:
        if dish['name'] == dish_name:
            return dish.get('ingredients', [])
    return []

def cleanup_old_ingredient_data():
    """Remove ingredient tracking records older than 1 month"""
    tracking_data = load_ingredient_tracking()
    one_month_ago = datetime.now() - timedelta(days=30)
    
    # Filter out old acquisitions
    filtered_acquisitions = []
    for acquisition in tracking_data.get("ingredient_acquisitions", []):
        try:
            cooking_date = datetime.strptime(acquisition["planned_cooking_date"], "%Y-%m-%d")
            if cooking_date >= one_month_ago:
                filtered_acquisitions.append(acquisition)
        except (ValueError, KeyError):
            # Keep malformed entries for now
            filtered_acquisitions.append(acquisition)
    
    tracking_data["ingredient_acquisitions"] = filtered_acquisitions
    save_ingredient_tracking(tracking_data)

def get_upcoming_dishes():
    """Find dishes planned for today/tomorrow with incomplete ingredients"""
    schedule_data = load_schedule()
    tracking_data = load_ingredient_tracking()
    
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    upcoming_dishes = []
    
    for date in [today, tomorrow]:
        if date in schedule_data.get("schedule", {}):
            day_schedule = schedule_data["schedule"][date]
            for meal_type, meal_info in day_schedule.items():
                if meal_info.get("type") == "cook":
                    dish_name = meal_info.get("dish_name")
                    if dish_name:
                        # Check if this dish has incomplete ingredients
                        has_incomplete_ingredients = True
                        
                        # Find tracking record for this dish/date
                        for acquisition in tracking_data.get("ingredient_acquisitions", []):
                            if (acquisition.get("dish_name") == dish_name and 
                                acquisition.get("planned_cooking_date") == date):
                                # Check if all ingredients are obtained
                                ingredients = acquisition.get("ingredients", {})
                                has_incomplete_ingredients = any(
                                    not ing_info.get("obtained", False) 
                                    for ing_info in ingredients.values()
                                )
                                break
                        
                        if has_incomplete_ingredients:
                            upcoming_dishes.append({
                                "dish_name": dish_name,
                                "date": date,
                                "meal_type": meal_type
                            })
    
    return upcoming_dishes

def find_leftover_chain(schedule_data, leftover_id):
    """Find all leftover meals associated with a specific cooked dish"""
    leftover_meals = []
    
    if "schedule" not in schedule_data:
        return leftover_meals
        
    for date, meals in schedule_data["schedule"].items():
        for meal_type, meal_data in meals.items():
            if (meal_data.get("type") == "leftovers" and 
                meal_data.get("leftover_id") == leftover_id):
                leftover_meals.append({
                    "date": date,
                    "meal_type": meal_type,
                    "meal_data": meal_data
                })
    
    # Sort by date and meal type (lunch before dinner)
    def sort_key(meal):
        date = meal["date"]
        meal_type_order = {"lunch": 0, "dinner": 1}
        return (date, meal_type_order.get(meal["meal_type"], 2))
    
    return sorted(leftover_meals, key=sort_key)

def remove_leftover_chain(schedule_data, leftover_id):
    """Remove all leftover meals associated with a specific leftover_id"""
    removed_count = 0
    
    if "schedule" not in schedule_data:
        return removed_count
        
    # Find and remove all leftovers with this ID
    dates_to_check = list(schedule_data["schedule"].keys())
    for date in dates_to_check:
        meal_types_to_check = list(schedule_data["schedule"][date].keys())
        for meal_type in meal_types_to_check:
            meal_data = schedule_data["schedule"][date][meal_type]
            if (meal_data.get("type") == "leftovers" and 
                meal_data.get("leftover_id") == leftover_id):
                del schedule_data["schedule"][date][meal_type]
                removed_count += 1
                
        # Clean up empty date entries
        if not schedule_data["schedule"][date]:
            del schedule_data["schedule"][date]
    
    return removed_count

def find_next_available_slots(schedule_data, start_date, meal_type, count):
    """Find next available meal slots for rescheduling leftovers"""
    available_slots = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    meal_types = ["lunch", "dinner"]
    
    # Start from the next meal slot
    current_meal_index = meal_types.index(meal_type)
    if current_meal_index < len(meal_types) - 1:
        next_meal_type = meal_types[current_meal_index + 1]
    else:
        current_date += timedelta(days=1)
        next_meal_type = meal_types[0]
    
    # Look for available slots within 2 weeks
    max_date = current_date + timedelta(days=14)
    
    while len(available_slots) < count and current_date <= max_date:
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Check if slot is available
        is_available = True
        if "schedule" in schedule_data and date_str in schedule_data["schedule"]:
            if next_meal_type in schedule_data["schedule"][date_str]:
                is_available = False
        
        if is_available:
            available_slots.append({
                "date": date_str,
                "meal_type": next_meal_type
            })
        
        # Move to next slot
        if next_meal_type == "lunch":
            next_meal_type = "dinner"
        else:
            next_meal_type = "lunch"
            current_date += timedelta(days=1)
    
    return available_slots
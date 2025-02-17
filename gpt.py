import datetime
import math
from collections import namedtuple

# A simple Workout namedtuple for clarity.
Workout = namedtuple('Workout', ['type', 'dist'])

##############################################
# Data Gathering Functions (your original code)
##############################################
def start_plan_form():
    run_length, num_runs, mileage = get_mileage()
    target_dist, end_date, weeks_till_end = get_target_dist_date(run_length, mileage)
    pace = get_pace(target_dist)
    workout_types = get_workout_types()
    # Create the plan using the gathered data.
    plan = create_run_plan(weeks_till_end, num_runs, mileage, target_dist, workout_types, ratio=1.75)
    # Print the plan.
    print("\nGenerated Running Plan:")
    for week, data in plan.items():
        phase = data["phase"].capitalize()
        print(f"{week} [{phase} Phase] - Total Mileage: {data['weekly_mileage']} km")
        print(f"  Long Run: {data['long_run']} km, Other Runs: {data['easy_run']} km")
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            workout = data["daily_workouts"].get(day, "Rest")
            if isinstance(workout, str):
                print(f"  {day}: {workout}")
            else:
                print(f"  {day}: {workout.type.capitalize()} run of {workout.dist} km")
        print("  (Add additional recovery or cross-training days as needed.)\n")

def get_mileage():
    already_run = input("Do you currently run? ")
    if already_run.lower() not in ["yes", "y"]:
        run_length = 2.5
        num_runs = 4
    else:
        run_length = float(input('Average running distance (km): '))
        num_runs = int(input('Number of runs per week: '))
    mileage = run_length * num_runs
    print(f'Do you want to continue with {num_runs} training sessions per week?')
    confirm_num = input("Type yes or the number you want to change to: ")
    if confirm_num.lower() not in ['y', 'yes']:
        num_runs = int(confirm_num)
    return run_length, num_runs, mileage

def get_pace(target_dist):
    current_paces = [float('inf'), 0]
    running = True
    while running:
        print("Let us know a recent pace record")
        dist = float(input('Distance (km): '))
        pace = float(input("Pace (km/h): "))
        if abs(dist - target_dist) < abs(current_paces[0] - target_dist):
            current_paces = [dist, pace]
        else:
            print("That was further from your desired distance than your previous entry")
        if abs(dist - target_dist) < target_dist / 2:
            running = False
        else:
            have_longer = input("Do you have any paces for runs closer to your desired distance? ")
            if have_longer.lower() not in ["y", "yes"]:
                running = False
    return current_paces

def get_target_dist_date(run_length, mileage):
    target_dist = float(input("Target distance (km): "))
    weeks_till_end, recom_end_date = get_target_date(run_length, mileage, target_dist)
    running = True
    while running:
        end_date_str = input(f"Target date (recommended soonest {recom_end_date.strftime('%d.%m.%Y')}): ")
        end_date = datetime.datetime.strptime(end_date_str, "%d.%m.%Y").date()
        if end_date > recom_end_date:
            running = False
        else:
            user_weeks = (end_date - datetime.date.today()).days / 7
            percent_increase = (target_dist / (mileage * 0.25)) ** (1 / user_weeks) * 100 - 100
            print(f"Our recommended maximum mileage increase per week is 10%, your selected date results in an increase of {percent_increase:.1f}%")
            should_cont = input("Are you sure you want to continue with this date? ")
            if should_cont.lower() in ["y", "yes"]:
                running = False
    return target_dist, end_date, weeks_till_end

def get_target_date(run_length, mileage, target_dist):
    num_weeks = (math.log(target_dist) - math.log(mileage * 0.25)) / math.log(1.1)
    end_date = datetime.date.today() + datetime.timedelta(days=round(num_weeks * 7))
    return math.floor(num_weeks), end_date

def get_workout_types():
    print("Please select desired workout types to be included in your plan.")
    print("e: easy run (strongly recommended), l: long run (recommended), t: tempo run (recommended), i: interval training, s: swim")
    user_selection = input("Enter choices with space between: ").split()
    selection_dict = {'l': 'long', 't': 'tempo', 'e': 'easy', 'i': 'interval', 's': 'swim'}
    parsed_selection = set()
    for selection in user_selection:
        try:
            parsed_selection.add(selection_dict[selection])
        except KeyError:
            print(f'You selected {selection}, which is not an available workout type.')
    return parsed_selection

##############################################
# Helper: Get Predetermined Schedule Pattern
##############################################
def get_schedule_pattern(num_runs):
    patterns = {
        2: ["Wednesday", "Saturday"],
        3: ["Monday", "Thursday", "Saturday"],
        4: ["Monday", "Wednesday", "Friday", "Saturday"],
        5: ["Monday", "Tuesday", "Thursday", "Friday", "Saturday"],
        6: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        7: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    }
    return patterns.get(num_runs, ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][:num_runs])

##############################################
# Revised create_run_plan Function (Linear Progression, Taper, & Scheduled Rest)
##############################################
def create_run_plan(total_weeks, num_runs, initial_mileage, target_dist, workout_types, ratio=1.75):
    """
    Generates a running plan with linear progression over (build + taper) weeks.
    
    Parameters:
      total_weeks (int): Total plan weeks.
      num_runs (int): Running days per week.
      initial_mileage (float): Starting weekly mileage (km).
      target_dist (float): Target race distance (km); final build week's long run is at least target_dist,
                           and can progress up to 30% above target_dist.
      workout_types (set or list): Desired workout types; must include "long" and "easy". Extra types cycle over build weeks.
      ratio (float): Desired multiplier so that Long Run = ratio * Easy Run.
    
    The plan is built in two phases:
      1. Build Phase: Linear progression from initial_mileage to a final weekly mileage computed from the desired final long run.
         Define final_long_run = target_dist if build_weeks < 8, else target_dist * 1.3.
         Then, final_weekly_mileage = final_long_run * (1 + (num_runs - 1)/ratio).
      2. Taper Phase: For target_dist <= 20 km, taper_weeks = round(target_dist/10) (min 1); else taper_weeks = 2.
         Taper weeks use gentle reduction factors.
    
    Additionally, running workouts are assigned onto a fixed 7-day schedule using a predetermined pattern so that:
      - The long run always falls on Saturday.
      - The remaining days in the pattern are used for running, and days not in the pattern are "Rest".
    
    Returns:
      plan: A dictionary mapping week labels (e.g. "Week 1") to weekly plan details.
    """
    # Ensure required workout types.
    if "long" not in workout_types:
        workout_types.add("long")
    if "easy" not in workout_types:
        workout_types.add("easy")
    
    required = ["long", "easy"]
    optional = [w for w in workout_types if w not in required]
    
    if target_dist <= 20:
        taper_weeks = max(1, round(target_dist / 10))
    else:
        taper_weeks = 2
    build_weeks = total_weeks - taper_weeks
    if build_weeks < 1:
        raise ValueError("Total weeks must exceed the taper weeks.")
    
    if build_weeks >= 8:
        final_long_run = target_dist * 1.3
    else:
        final_long_run = target_dist
    
    # Define a minimum easy-run distance: at least 3 km or 50% of target, whichever is higher.
    min_easy_run = max(3, 0.5 * target_dist)
    final_weekly_mileage = final_long_run * (1 + (num_runs - 1) / ratio)
    
    if build_weeks > 1:
        weekly_increment = (final_weekly_mileage - initial_mileage) / (build_weeks - 1)
    else:
        weekly_increment = 0
    
    plan = {}
    full_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # --- Build Phase ---
    for week in range(1, build_weeks + 1):
        weekly_mileage = initial_mileage + (week - 1) * weekly_increment
        weekly_mileage = round(weekly_mileage, 1)
        ideal_easy = weekly_mileage / ((num_runs - 1) + ratio)
        ideal_long = ratio * ideal_easy
        if week == build_weeks:
            long_run = max(ideal_long, target_dist)
        else:
            long_run = ideal_long
        long_run = min(long_run, final_long_run)
        easy_run = (weekly_mileage - long_run) / (num_runs - 1) if num_runs > 1 else 0
        long_run = round(long_run, 1)
        easy_run = round(easy_run, 1)
        
        computed_workouts = [Workout("long", long_run), Workout("easy", easy_run)]
        for i in range(num_runs - 2):
            workout_type = optional[i % len(optional)] if optional else "easy"
            computed_workouts.append(Workout(workout_type, easy_run))
        
        pattern = get_schedule_pattern(num_runs)
        assigned = {}
        for idx, day in enumerate(pattern):
            assigned[day] = computed_workouts[idx]
        # Ensure the long run is on Saturday.
        if "Saturday" in pattern:
            sat_index = pattern.index("Saturday")
            if assigned["Saturday"].type != "long":
                long_idx = None
                for j, w in enumerate(computed_workouts):
                    if w.type == "long":
                        long_idx = j
                        break
                if long_idx is not None:
                    # Swap the workouts.
                    assigned[pattern[sat_index]], computed_workouts[long_idx] = computed_workouts[long_idx], assigned[pattern[sat_index]]
        
        weekly_schedule = {}
        for day in full_week:
            if day in assigned:
                weekly_schedule[day] = assigned[day]
            else:
                weekly_schedule[day] = "Rest"
        
        plan[f"Week {week}"] = {
            "phase": "build",
            "weekly_mileage": weekly_mileage,
            "long_run": long_run,
            "easy_run": easy_run,
            "daily_workouts": weekly_schedule
        }
    
    build_last_mileage = initial_mileage + (build_weeks - 1) * weekly_increment
    
    # --- Taper Phase ---
    taper_factors = [0.90, 0.80] if taper_weeks >= 2 else [0.90]
    for t in range(1, taper_weeks + 1):
        week = build_weeks + t
        weekly_mileage_taper = round(build_last_mileage * taper_factors[t - 1], 1)
        ideal_easy = weekly_mileage_taper / ((num_runs - 1) + ratio)
        ideal_long = ratio * ideal_easy
        if t == 1:
            long_run = max(min(ideal_long, build_last_mileage * 0.95), target_dist)
        else:
            long_run = ideal_long
        long_run = min(long_run, final_long_run)
        easy_run = (weekly_mileage_taper - long_run) / (num_runs - 1) if num_runs > 1 else 0
        long_run = round(long_run, 1)
        easy_run = round(easy_run, 1)
        
        computed_workouts = [Workout("long", long_run), Workout("easy", easy_run)]
        for i in range(num_runs - 2):
            computed_workouts.append(Workout("easy", easy_run))
        
        pattern = get_schedule_pattern(num_runs)
        assigned = {}
        for idx, day in enumerate(pattern):
            assigned[day] = computed_workouts[idx]
        if "Saturday" in pattern:
            sat_index = pattern.index("Saturday")
            if assigned["Saturday"].type != "long":
                long_idx = None
                for j, w in enumerate(computed_workouts):
                    if w.type == "long":
                        long_idx = j
                        break
                if long_idx is not None:
                    assigned[pattern[sat_index]], computed_workouts[long_idx] = computed_workouts[long_idx], assigned[pattern[sat_index]]
        
        weekly_schedule = {}
        for day in full_week:
            if day in assigned:
                weekly_schedule[day] = assigned[day]
            else:
                weekly_schedule[day] = "Rest"
        
        plan[f"Week {week}"] = {
            "phase": "taper",
            "weekly_mileage": weekly_mileage_taper,
            "long_run": long_run,
            "easy_run": easy_run,
            "daily_workouts": weekly_schedule
        }
    
    return plan

##############################################
# End of create_run_plan
##############################################

# Use your data-gathering functions to build and display the plan.
start_plan_form()

import datetime
import math
from collections import namedtuple


# class Workout:
#     def __init__(self, type, dist, pace=False, ):
#         self.type = type
#         self.dist = dist
#         self.pace = pace

def start_plan_form():
    run_length, num_runs, mileage = get_mileage()
    target_dist, end_date, weeks_till_end = get_target_dist_date(run_length, mileage)
    pace = get_pace(target_dist)
    workout_types = get_workout_types()
    create_workouts(weeks_till_end, num_runs, mileage, target_dist, workout_types)


def get_mileage():
    already_run = input("Do you currently run? ")
    if already_run.lower() not in ["yes", "y"]:
        run_length = 2.5
        num_runs = 4
    else:
        run_length = float(input('Average running distance(km): '))
        num_runs = int(input('Number of runs per week: '))

    mileage = run_length * num_runs
    #potentially print mileage and ask for confirmation

    print(f'Do you want to continue with {num_runs} training sessions per week?')
    confirm_num = input("Type yes or number you want to change to: ")
    if confirm_num.lower() not in ['y', 'yes']:
        num_runs = confirm_num


    return run_length, num_runs, mileage


def get_pace(target_dist):
    current_paces = [float('-inf'), 0]
    running = True

    # Find most useful distance combo
    # Most recent or longest? Maybe another question
    while running:
        print("Let us know a recent pace record")
        dist = float(input('Distance(km): '))
        pace = input("Pace(km/h): ")

        if abs(dist - target_dist) < abs(current_paces[0] - target_dist):
            current_paces = [dist, pace]
        elif current_paces[0] != 0:
            print("That was further from your desired distance than your previous entry")

        if abs(dist - target_dist) < target_dist / 2:
            running = False
        else:
            have_longer = input("Do you have any paces for runs closer to your desired distance?")
            if not have_longer.lower() in ["y", "yes"]:
                running = False


    return current_paces

def get_target_dist_date(run_length, mileage):
    target_dist = float(input("Target distance(km): "))
    weeks_till_end, recom_end_date = get_target_date(run_length, mileage, target_dist)

    #rename running?
    running = True
    while running:
        end_date = datetime.datetime.strptime(input(f"Target date (recommended soonest {recom_end_date}): "), "%d.%m.%Y").date()                     

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
    print("e: easy run (strongly recommended) l: long run (recommended), t:tempo run (recommended), i:interval training, s:swim")
    user_selection = input("Enter choices with space between: ").split()
    selection_dict = {'l': 'long', 't':'tempo', 'e':'easy', 'i':'interval', 's': 'swim'}
    parsed_selection = set()
    for selection in user_selection:
        try:
            parsed_selection.add(selection_dict[selection])
        except KeyError:
            print(f'You selected {selection}, which is not an available workout type.')
    return parsed_selection

# def create_workouts(num_weeks, num_runs, mileage, targer_dist, workout_types):
#     weeks_per_cycle = math.ceil(len(workout_types / num_runs))
#     num_cycles = math.floor(num_weeks / weeks_per_cycle)
    
#     plan = {}

#     for cycle in range(1, weeks_per_cycle + 1):



# Define a simple Workout namedtuple for clarity.
Workout = namedtuple('Workout', ['type', 'dist'])

def create_run_plan(total_weeks, num_runs, initial_mileage, target_dist, workout_types=None, ratio=1.75):
    """
    Generates a running plan over a total number of weeks.
    
    Parameters:
      total_weeks (int): Total weeks in the plan (build + taper).
      num_runs (int): Number of running days per week.
      initial_mileage (float): Starting weekly mileage (in km).
      target_dist (float): Target race distance (in km). The final build week's long run 
                           will be at least this value.
      workout_types (list of str): List of desired workout types (e.g. ["long", "easy", "tempo", "interval", "hill"]).
                                   Must include at least "long" and "easy". Extra types will cycle over build weeks.
      ratio (float): Desired multiplier such that ideally Long Run = ratio × Easy Run.
                     (Default: 1.75)
                     
    Notes on the algorithm:
      - Weekly mileage increases ~10% per week (except every 4th week is a recovery week at 80%).
      - In the final build week, if the computed mileage is less than a desired minimum, it is bumped up.
        The minimum is defined as:
            desired_final_weekly = target_dist + (num_runs - 1)*min_easy_run,
        where min_easy_run = max(3, 0.5 * target_dist).
      - The ideal distribution is computed as:
            E = weekly_mileage / ((num_runs - 1) + ratio)   and L = ratio * E.
      - The long run is capped at 1.3 × target_dist.
      - The taper phase (last 1 or 2 weeks) reduces weekly mileage to allow recovery.
    
    Returns:
      A dictionary mapping week numbers to weekly plan details.
    """
    # Default workout types if none provided.
    if workout_types is None:
        workout_types = ["long", "easy", "tempo", "interval", "hill"]
    
    # Ensure "long" and "easy" are in workout_types.
    if "long" not in workout_types:
        workout_types.insert(0, "long")
    if "easy" not in workout_types:
        workout_types.insert(1, "easy")
    
    # Separate required and optional workouts.
    required = ["long", "easy"]
    optional = [w for w in workout_types if w not in required]
    
    # Determine taper weeks: if target_dist <=20, taper_weeks = round(target_dist/10) (min 1), else taper_weeks = 2.
    if target_dist <= 20:
        taper_weeks = max(1, round(target_dist / 10))
    else:
        taper_weeks = 2
    build_weeks = total_weeks - taper_weeks
    if build_weeks < 1:
        raise ValueError("Total weeks must exceed the taper weeks.")
    
    # Define a minimum desired easy-run distance.
    min_easy_run = max(3, 0.5 * target_dist)
    desired_final_weekly = target_dist + (num_runs - 1) * min_easy_run  # ensures final long run can be built and easy runs are not trivial
    
    plan = {}
    weekly_mileage = initial_mileage
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # --- Build Phase ---
    for week in range(1, build_weeks + 1):
        # Adjust mileage:
        if week > 1:
            if week % 4 == 0:
                weekly_mileage *= 0.80  # recovery week
            else:
                weekly_mileage *= 1.10  # increase 10%
        weekly_mileage = round(weekly_mileage, 1)
        
        # In final build week, ensure weekly mileage is at least the desired_final_weekly.
        if week == build_weeks and weekly_mileage < desired_final_weekly:
            weekly_mileage = desired_final_weekly
        
        # Compute ideal distribution:
        # Let E be the easy/tempo run distance and L = ratio * E.
        # Then: weekly_mileage = L + (num_runs - 1)*E = (ratio + num_runs - 1)*E.
        ideal_easy = weekly_mileage / ((num_runs - 1) + ratio)
        ideal_long = ratio * ideal_easy
        
        # Cap the long run at 1.3 × target_dist.
        if week == build_weeks:
            # In final build week, force long run to be at least target_dist.
            long_run = max(ideal_long, target_dist)
        else:
            long_run = ideal_long
        long_run = min(long_run, target_dist * 1.3)
        easy_run = (weekly_mileage - long_run) / (num_runs - 1) if num_runs > 1 else 0
        
        # Round distances.
        long_run = round(long_run, 1)
        easy_run = round(easy_run, 1)
        
        # Build daily workout plan.
        daily_workouts = {}
        available_days = days_of_week.copy()
        # Always assign:
        daily_workouts[available_days.pop(0)] = Workout("long", long_run)
        daily_workouts[available_days.pop(0)] = Workout("easy", easy_run)
        remaining_slots = num_runs - 2
        
        # Cycle through optional workouts if available.
        for i in range(remaining_slots):
            opt_index = ((week - 1) * remaining_slots + i) % (len(optional) if optional else 1)
            workout_type = optional[opt_index] if optional else "easy"
            daily_workouts[available_days.pop(0)] = Workout(workout_type, easy_run)
        
        plan[f"Week {week}"] = {
            "phase": "build",
            "weekly_mileage": weekly_mileage,
            "long_run": long_run,
            "easy_run": easy_run,
            "daily_workouts": daily_workouts
        }
    
    build_last_mileage = weekly_mileage  # final build week's mileage
    
    # --- Taper Phase ---
    # Use a simple linear reduction: first taper week at 80% of build_last_mileage, second (if exists) at 70%.
    taper_factors = [0.8, 0.7] if taper_weeks >= 2 else [0.8]
    for t in range(1, taper_weeks + 1):
        week = build_weeks + t
        weekly_mileage_taper = round(build_last_mileage * taper_factors[t - 1], 1)
        
        # For taper, distribute mileage as before. We want to maintain at least a minimal long run:
        ideal_easy = weekly_mileage_taper / ((num_runs - 1) + ratio)
        ideal_long = ratio * ideal_easy
        # In taper, we might want to reduce intensity so long run can be slightly reduced but not below target in first taper week.
        if t == 1:
            long_run = max(min(ideal_long, build_last_mileage * 0.9), target_dist)
        else:
            long_run = ideal_long
        long_run = min(long_run, target_dist * 1.3)
        easy_run = (weekly_mileage_taper - long_run) / (num_runs - 1) if num_runs > 1 else 0
        
        long_run = round(long_run, 1)
        easy_run = round(easy_run, 1)
        
        daily_workouts = {}
        available_days = days_of_week.copy()
        daily_workouts[available_days.pop(0)] = Workout("long", long_run)
        daily_workouts[available_days.pop(0)] = Workout("easy", easy_run)
        for i in range(num_runs - 2):
            daily_workouts[available_days.pop(0)] = Workout("easy", easy_run)
        
        plan[f"Week {week}"] = {
            "phase": "taper",
            "weekly_mileage": weekly_mileage_taper,
            "long_run": long_run,
            "easy_run": easy_run,
            "daily_workouts": daily_workouts
        }
    
    return plan

if __name__ == "__main__":
    try:
        total_weeks = int(input("Enter total number of weeks in the plan (build + taper): "))
        num_runs = int(input("Enter number of running days per week: "))
        initial_mileage = float(input("Enter your starting weekly mileage (km): "))
        target_dist = float(input("Enter your target race distance (km): "))
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        exit(1)
    
    # Optionally, user can provide workout types. Here we use a default.
    user_workout_types = ["long", "easy", "tempo", "interval", "hill"]
    
    plan = create_run_plan(total_weeks, num_runs, initial_mileage, target_dist, workout_types=user_workout_types, ratio=1.75)
    
    # Display the plan:
    print("\nGenerated Running Plan:")
    for week, data in plan.items():
        phase = data["phase"].capitalize()
        print(f"{week} [{phase} Phase] - Total Mileage: {data['weekly_mileage']} km")
        print(f"  Long Run: {data['long_run']} km, Other Runs: {data['easy_run']} km")
        for day, workout in data["daily_workouts"].items():
            print(f"  {day}: {workout.type.capitalize()} run of {workout.dist} km")
        print("  (Add additional recovery or cross-training days as needed.)\n")

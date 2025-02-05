import datetime
import math

def start_plan_form():
    run_length, num_runs, mileage = get_mileage()
    target_dist, end_date, weeks_till_end = get_target_dist_date(run_length, mileage)

    pace = get_current_pace(target_dist)


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
    if target_dist <= run_length:
        return 0, "Ready now"
    else:
        num_weeks = (math.log(target_dist) - math.log(mileage * 0.25)) / math.log(1.1)
        end_date = datetime.date.today() + datetime.timedelta(days=round(num_weeks * 7))

        return num_weeks, end_date
    
get_pace(21)
start_plan_form()
    


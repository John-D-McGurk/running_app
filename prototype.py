import datetime

def start_plan_form():
    run_length, num_runs, mileage = get_mileage()

    

    pace = get_current_pace(target_dist)


def get_mileage():
    run_length = input('Average running distance(km): ')
    num_runs = input('Number of runs per week: ')

    mileage = run_length * num_runs
    #potentially print mileage and ask for confirmation

    return run_length, num_runs, mileage


def get_current_pace(target_dist):
    current_paces = []
    running = True

    # Find most useful distance combo
    # Most recent or longest? Maybe another question
    while running:
        dist = float(input('Distance(km): '))
        pace = input("Pace(km/h): ")
        current_paces.append((dist, pace))
        if dist >= target_dist:
            running = False

    return current_paces

def get_target_dist_date(run_length, mileage):
    target_dist = input("Target distance(km): ")



    date = input("Date: ")

def get_date_from_target_dist(run_length, mileage, target_dist):
    if target_dist <= run_length:
        print('ready')
        return "Ready now"
    else:
        num_weeks_1 = 0
        while run_length < target_dist:
            if run_length < 10:
                run_length += 1
            else: 
                run_length += run_length * 0.1
            num_weeks_1 += 1

        num_weeks_2 = 0

        long_run = mileage * 0.25
        while long_run < target_dist:
            long_run += long_run * 0.1
            num_weeks_2 += 1
        
        print(num_weeks_1)
        print(num_weeks_2)
    


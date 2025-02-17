import datetime
import math

class Workout:
    def __init__(self, type, dist, pace=False):
        self.type = type
        self.dist = dist
        self.pace = pace

class User:
    def __init__(self):
        self.category = None

class Plan:
    def __init__(self, user):
        self.user = user

def start_plan_form():
    run_length, num_runs, mileage = get_mileage()
    target_dist, end_date, weeks_till_end = get_target_dist_date(run_length, mileage)
    pace = get_pace(target_dist)
    workout_types = get_workout_types()

def get_mileage():
    already_run = input("Do you currently run? ")
    if already_run.lower() not in ["yes", "y"]:
        run_length = 2.5
        num_runs = 4
    else:
        run_length = float(input('Average running distance(km): '))
        num_runs = int(input('Number of runs per week: '))

    mileage = run_length * num_runs
    return run_length, num_runs, mileage

def initialize():
    user = User()
    plan = Plan(user)
    return user, plan
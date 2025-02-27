import datetime
import math
from queue import PriorityQueue

class Workout:
    def __init__(self, type, dist, pace=False, ):
        self.type = set_type(type)
        self.dist = dist
        self.pace = pace
        self.priorty_rest_after = 6

    def set_type(self, type):
        if type not in ['long', 'easy', 'tempo', 'interval', 'hill', 'swim']:
            raise ValueError(f"Invalid workout type: {type}")
        return type

class User:
    def __init__(self):
        self.category = None
        self.five_k_time = None
        self.pace_level = 0
        self.mileage = 0
        self.pace_level = 1

    def set_category(self):
        pace_weight = 0.5
        if not self.pace_level:
            pace_weight = 0
        elif self.mileage > self.pace_level:
            pace_weight = self.mileage / (self.mileage + self.pace_level)
        else:
            pace_weight = self.pace_level / (self.mileage + self.pace_level)
            
        overall_score = pace_weight * self.pace_level +  (1 - pace_weight) * self.mileage

        if overall_score > 80:
            self.category = "Elite"
        elif overall_score > 60:
            self.category = "Advanced"
        elif overall_score > 40:
            self.category = "Intermediate"
        elif overall_score > 20:
            self.category = "Beginner"


    def set_five_k_time(self, time, distance):
        self.five_k_time = riegel_formula(distance, time, 5)
        self.pace_level = get_pace_level(self.five_k_time)



class Plan:
    def __init__(self, user):
        self.user = user
        self.target_dist = None
        self.end_date = None
        self.num_weeks = None
        self.taper_length = None
        self.taper_start = None
        self.plan = []

    def set_end_date(self, date):
        self.end_date = date
        self.num_weeks = (self.end_date - datetime.date.today()).days / 7
        self.taper_length = math.round(2 * self.target_dist / 3)
        self.taper_start = self.end_date - datetime.timedelta(days=math.round(self.taper_length))


def riegel_formula(dist, time, new_dist):
    """Uses the Riegel formula to predict a time for a new distance based on a time for a known distance."""
    return time * (new_dist / dist) ** 1.06

def get_pace_level(five_k_time):
    """Assigns a level based on a 5k time. Maps to 15min = level 100, 33 min = level 50 and 60min = level 1."""
    return 503.3 - 115.2 * math.log(five_k_time + 18.2)

def get_deriv_pace_level(five_k_time):
    """Takes the derivative of the pace level function."""
    return -1 * 115.2 / (five_k_time + 18.2)

def get_10_perc_pace_inc_time(five_k_time, augment=30):
    """Returns the time for a 10% increase in pace. Current assumption is 4 runs per week."""
    if five_k_time > 35:
        return -2 * get_deriv_pace_level(five_k_time)
    else:
        return 1.3 ** (-1 * get_deriv_pace_level(five_k_time - augment)) + 0.64


def start_plan_form(user, plan):
    get_mileage(user)
    get_target_dist( plan)
    get_target_date(user, plan)
    target_pace = input("Do you have a target pace? ")
    if target_pace.lower() in ["yes", "y"]:
        get_pace(user, plan.target_dist)
    get_workout_types(plan)
    create_workouts(plan)

def get_mileage(user):
    already_run = input("Do you currently run? ")
    if already_run.lower() not in ["yes", "y"]:
        user.set_category("Beginner")
    else:
        mileage = float(input('Average weekly running distance(km): '))

    user.mileage = mileage

def get_target_dist(plan):
    plan.target_dist = float(input("What is your target distance(km)? "))

def get_target_date(user, plan):
    recom_date = get_recom_target_date(user, plan)
    print(f"Based on your current mileage, we recommend an earliest date of {recom_date}")
    plan.set_end_date(datetime.date.strftime(input("Enter your desired target date (DD-MM-YYYY): "), "%d-%m-%Y"))

def get_recom_target_date(user, plan):
    num_weeks = (math.log(plan.target_dist) - math.log(user.mileage * 0.25)) / math.log(1.1)
    end_date = datetime.date.today() + datetime.timedelta(days=round(num_weeks * 7))

    return end_date

def get_pace(user, target_dist):
    running = True

    while running:
        print("Let us know a recent pace record")
        dist = float(input('Distance(km): '))
        pace = input("Time(mins): ")

        if abs(dist - target_dist) < target_dist / 2:
            running = False
        else:
            have_longer = input("Do you have any paces for runs closer to your desired distance?")
            if have_longer.lower() not in ["y", "yes"]:
                running = False
    
    user.set_five_k_time(pace, dist)
    
def get_workout_types(user, plan):
    if user.category == "Beginner":
        plan.workout_types = ['easy', 'long']
    elif user.category == "Intermediate":
        plan.workout_types = ['easy', 'long', 'tempo']
    elif user.category == "Advanced":
        plan.workout_types = ['easy', 'long', 'tempo', 'interval', 'strength']
    else:
        plan.workout_types = ['easy', 'long', 'tempo', 'interval', 'strength', 'cross']

    # add in a swap function for user to change workout types

def get_workout_freq(user, plan):
    if user.category == "Beginner":
        plan.num_runs = 3
    elif user.category == "Intermediate":
        plan.num_runs = 4
    elif user.category == "Advanced":
        plan.num_runs = 5
    else:
        plan.num_runs = 6

    # add in a swap function for user to change workout frequency


def create_workouts(user, plan):
    weeks_in_cycle = 1
    if plan.workout_types > plan.num_runs:
        weeks_in_cycle = math.ceil(plan.workout_types / plan.num_runs)
    current_weekday = datetime.date.today().weekday()
    
    full_weeks_till_taper = plan.num_weeks - (plan.taper_length - plan.taper_start.weekday() - current_weekday) / 7
    cycles_till_taper = math.floor(full_weeks_till_taper / weeks_in_cycle)

    for cycle in cycles_till_taper:
        for week in range(weeks_in_cycle):
            week_workouts = [None] * 7
            if 'long' in plan.workout_types:

                week_workouts[6] = Workout('long', )

      



def initialize():
    user = User()
    plan = Plan(user)
    return user, plan





if __name__ == "__main__":
    pass
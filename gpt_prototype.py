def generate_run_plan(experience_level, current_weekly_mileage, target_distance, training_days, total_weeks):
    """
    Generates a running plan as a list of weekly dictionaries.
    
    Parameters:
      experience_level (str): "novice", "intermediate", or "advanced"
      current_weekly_mileage (float): current weekly mileage (miles)
      target_distance (str): target race distance (e.g., "5K", "10K", "half", "marathon")
      training_days (int): number of running days per week
      total_weeks (int): length of the plan in weeks
      
    Returns:
      plan (list): a list of dictionaries, one per week, with the weekly mileage and daily breakdown.
    """
    
    # For novices, enforce a minimum baseline mileage (e.g., 10 miles)
    if experience_level.lower() == "novice":
        weekly_mileage = max(current_weekly_mileage, 10)
    else:
        weekly_mileage = current_weekly_mileage

    plan = []
    previous_long_run = 0

    for week in range(1, total_weeks + 1):
        # For weeks beyond the first, adjust mileage:
        if week > 1:
            # Every 4th week is a recovery (drop-back) week: reduce mileage by 20%
            if week % 4 == 0:
                weekly_mileage *= 0.80
            else:
                weekly_mileage *= 1.10  # Increase by 10%
        # Round the weekly mileage to one decimal place
        weekly_mileage = round(weekly_mileage, 1)
        
        # Determine the long run distance (set as ~25% of the weekly mileage)
        long_run = round(weekly_mileage * 0.25, 1)
        # Ensure that the long run increases by at least 1 mile compared to last week (if applicable)
        if previous_long_run > 0:
            long_run = max(long_run, previous_long_run + 1)
        previous_long_run = long_run
        
        # Distribute the remaining mileage over the other days.
        # One day is the long run; assume one day is designated for a speed/tempo workout.
        if training_days > 1:
            remaining_mileage = weekly_mileage - long_run
            # For simplicity, we assume Day 2 is a speed/tempo run.
            # The remaining mileage for Day 2 is calculated as the average of the non-long run days.
            # Here, we assume that the total number of “other” runs is (training_days - 1)
            avg_run = round(remaining_mileage / (training_days - 1), 1)
            # For variety, you could designate Day 2 as the speed run and the rest as easy runs.
            speed_run = avg_run  # This can be tweaked based on desired workout intensity.
            # The rest of the days (if any beyond the speed day) are considered easy runs.
            num_easy_days = training_days - 2
            easy_run = round((remaining_mileage - speed_run) / num_easy_days, 1) if num_easy_days > 0 else 0
        else:
            avg_run = 0
            speed_run = 0
            easy_run = 0
        
        # Build the weekly plan dictionary.
        week_plan = {
            "week": week,
            "weekly_mileage": weekly_mileage,
            "long_run": long_run,
            "daily_plan": {}
        }
        # Day 1: Long run
        week_plan["daily_plan"]["Day 1"] = f"Long run: {long_run} miles"
        # Day 2: Speed/tempo workout (if available)
        if training_days >= 2:
            week_plan["daily_plan"]["Day 2"] = f"Speed/tempo run: {speed_run} miles"
        # Remaining days: Easy runs
        for day in range(3, training_days + 1):
            week_plan["daily_plan"][f"Day {day}"] = f"Easy run: {easy_run} miles"
        
        # Append the plan for this week
        plan.append(week_plan)
    
    return plan


if __name__ == "__main__":
    # Collect user input
    experience = input("Enter your experience level (novice, intermediate, advanced): ").strip()
    try:
        current_mileage = float(input("Enter your current weekly mileage (in miles): "))
    except ValueError:
        print("Invalid input. Please enter a number for mileage.")
        exit(1)
    target_distance = input("Enter your target race distance (e.g., 5K, 10K, half, marathon): ").strip()
    try:
        training_days = int(input("Enter the number of training days per week: "))
        total_weeks = int(input("Enter the total number of weeks in your plan: "))
    except ValueError:
        print("Invalid input. Please enter integer values for training days and weeks.")
        exit(1)
    
    # Generate the plan
    run_plan = generate_run_plan(experience, current_mileage, target_distance, training_days, total_weeks)
    
    # Display the plan
    print("\nGenerated Running Plan:")
    for week_plan in run_plan:
        print(f"Week {week_plan['week']} - Total Mileage: {week_plan['weekly_mileage']} miles")
        for day, activity in sorted(week_plan["daily_plan"].items()):
            print(f"  {day}: {activity}")
        print("  (Include additional rest or cross-training days as needed.)\n")

########################################
# Bryan Hernandez Rodriguez -----------#
# Patient_search.py:  Functions        #
#              Patient Search          #
########################################

heart_rate_samples = {
    "J. Alvarez": [72, 75, 78],
    "M. Chen": [80, 82],
    "R. Okafor": [65, 68, 70, 66],
    "S. Patel": [90, 95, 92, 88, 91],
    "T. Nguyen": [77, 79],
    "L. Kowalski": [68, 70, 69],
    "D. Osei": [98, 101, 95, 99],
    "A. Whitfield": [74, 76, 75, 73],
}

def patient_search(data):
    return {i + 1: name for i, name in enumerate(data.keys())}

def heart_rate_calc(*args):
    if not args:
        return None
    return {
        "count": len(args),
        "average": round(sum(args) / len(args), 2),
        "min": min(args),
        "max": max(args),
    }

def all_stats(name, *args):
    stats = heart_rate_calc(*args)
    print(f"\n--- Stats for {name} ---")
    print(f"Results {list(args)}:")
    for label, value in stats.items():
        print(f"{label.capitalize()}: {value}")

def specific_stats(name, stat_choice, *args):
    stats = heart_rate_calc(*args)
    if stat_choice not in stats:
        print(f"{stat_choice}' in not a valid choice.")
        return
    print(f"\n{stat_choice.capitalize()} for {name}: {stats[stat_choice]}")

def patient_directory():
    directory = patient_search(heart_rate_samples)

    print("\nPatient Directory:")
    for number, name in directory.items():
        print(f"{number}: {name}")

    while True:
        choice = input("\nEnter a Patient number: ").strip()
        if not choice.isdigit() or int(choice) not in directory:
            print("\nInvalid Patient number.")
            continue
        return int(choice), directory

def get_stat_choice():
    valid = ["all", "count", "average", "min", "max"]
    print("\nWhat do you want to see?")
    print("Options: all, count, average, min, max")
    while True:
        choice = input("\nEnter your choice: ").strip().lower()
        if choice in valid:
            return choice
        print("\nInvalid choice.")

def main():
    print("\nPatient Heart Rate Search")

    while True:
        patient_number, directory = patient_directory()
        patient_name = directory[patient_number]
        reading = heart_rate_samples[patient_name]

        stat_choice = get_stat_choice()

        if stat_choice == "all":
            all_stats(patient_name, *reading)
        else:
            specific_stats(patient_name, stat_choice, *reading)

        again = input("\nWould you like to look another patient? (y/n)").strip().lower()
        if again != "y":
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()
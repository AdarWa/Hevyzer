from typing import List, Optional
import re

from auth.models import Exercise, ProgressiveOverload, Report, Set
# import generator

# Only god knows what is happening here
def parse_workout(
    text: str,
    previous_reports: Optional[List[Report]] = None,
    activity_id: int = 1,
    name: str = "Workout"
) -> Report:
    """
    Parse a workout text and return a Report, filling progressive overload history
    from previous reports with the same workout name and same exercise.
    """
    exercises = []
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.startswith('Set'):
            i += 1
            continue

        exercise_name = line
        sets_list = []
        i += 1
        set_index = 0

        while i < len(lines) and lines[i].startswith('Set'):
            set_line = lines[i]

            # Match formats
            kg_match = re.match(r"Set \d+: (\d+) ?kg x (\d+)(?: \[(.+?)\])?", set_line)
            reps_match = re.match(r"Set \d+: (\d+) reps(?: \[(.+?)\])?", set_line)

            weight = 0.0
            reps = 0
            set_type = ""
            if kg_match:
                weight, reps, raw_type = float(kg_match.group(1)), int(kg_match.group(2)), kg_match.group(3)
                if raw_type:
                    set_type = raw_type.lower()
            elif reps_match:
                reps, raw_type = int(reps_match.group(1)), reps_match.group(2)
                weight = 0.0
                if raw_type:
                    set_type = raw_type.lower()

            volume = weight * reps

            # Progressive overload
            po = ProgressiveOverload()

            if previous_reports:
                # Collect history from previous reports with same workout name & exercise
                for prev_report in reversed(previous_reports):
                    if prev_report.name != name:
                        continue  # skip different workouts
                    prev_exercise = next((e for e in prev_report.exercises if e.name == exercise_name), None)
                    if prev_exercise and set_index < len(prev_exercise.sets):
                        prev_set = prev_exercise.sets[set_index]
                        # append previous set to history
                        po.history.extend(prev_set.progressive_overload.history)
                        # add last known values for comparison
                        po.last_weight = prev_set.weight
                        po.last_reps = prev_set.reps
                        po.last_volume = prev_set.volume

                        break  # take most recent matching set

            # add current set to history
            po.current_weight = weight
            po.current_reps = reps
            po.current_volume = volume
            po.add_to_history()

            sets_list.append(
                Set(
                    reps=reps,
                    weight=weight,
                    volume=volume,
                    progressive_overload=po,
                    set_type=set_type
                )
            )

            i += 1
            set_index += 1

        exercises.append(Exercise(name=exercise_name, sets=sets_list))

    return Report(activity_id=activity_id, exercises=exercises, name=name, notes="")



def report_to_text(report: Report) -> str:
    lines = []
    for exercise in report.exercises:
        lines.append(exercise.name)
        for idx, s in enumerate(exercise.sets, start=1):
            weight_str = f"{s.weight} kg" if s.weight > 0 else "Bodyweight"
            line = f"Set {idx}: {weight_str} x {s.reps} reps (Volume: {s.volume})"
            if s.set_type:
                line += f" [{s.set_type.capitalize()}]"

            if s.progressive_overload.history:
                history_lines = []
                for h in s.progressive_overload.history[:-1]:  # exclude current
                    h_weight_str = f"{h['weight']} kg" if h['weight'] else "Bodyweight"
                    history_lines.append(f"{h_weight_str} x {h['reps']} reps (Vol: {h['volume']})")
                if history_lines:
                    line += " | History: " + " -> ".join(history_lines)

            lines.append(line)
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    workout_text = """Bench Press (Barbell)
Set 1: 20 kg x 26 [Warm-up]
Set 2: 40 kg x 10
Set 3: 40 kg x 10
Set 4: 40 kg x 9

Cable Fly Crossovers
Set 1: 32 kg x 14
Set 2: 32 kg x 14
Set 3: 32 kg x 16

Chest Press (Machine)
Set 1: 29 kg x 10
Set 2: 25 kg x 10
Set 3: 25 kg x 12

Triceps Dip
Set 1: 10 reps
Set 2: 9 reps
Set 3: 9 reps

Triceps Rope Pushdown
Set 1: 23 kg x 12
Set 2: 23 kg x 10
Set 3: 23 kg x 9 [Drop]

Shoulder Press (Machine Plates)
Set 1: 15 kg x 13
Set 2: 15 kg x 13
Set 3: 15 kg x 7

Lateral Raise (Dumbbell)
Set 1: 10 kg x 12
Set 2: 10 kg x 12
Set 3: 10 kg x 11 
"""

    previous_reports = []

# Workout template
    workout_name = "Full Body A"

    workouts = [
    """Bench Press (Barbell)
Set 1: 20 kg x 10
Set 2: 30 kg x 8
Set 3: 40 kg x 6

Squat (Barbell)
Set 1: 40 kg x 10
Set 2: 50 kg x 8
Set 3: 60 kg x 6
""",
    """Bench Press (Barbell)
Set 1: 22 kg x 10
Set 2: 32 kg x 8
Set 3: 42 kg x 6

Squat (Barbell)
Set 1: 45 kg x 10
Set 2: 55 kg x 8
Set 3: 65 kg x 6
""",
    """Bench Press (Barbell)
Set 1: 24 kg x 10
Set 2: 34 kg x 8
Set 3: 44 kg x 6

Squat (Barbell)
Set 1: 50 kg x 10
Set 2: 60 kg x 8
Set 3: 70 kg x 6
"""
    ]

# Parse each workout and store progressive overload
    for i, w_text in enumerate(workouts, start=1):
        report = parse_workout(w_text, previous_reports=previous_reports, activity_id=i, name=workout_name)
        previous_reports.append(report)

    # Show last report with full progressive overload history
    last_report = previous_reports[-1]
    report_text = report_to_text(last_report)
    print(report_text)
    # print(generator.analyze_report(report, "mistral:7b-instruct-q4_K_M"))
from typing import List, Optional
from pydantic import BaseModel
import re

from auth.models import Exercise, ProgressiveOverload, Report, Set

def parse_workout(text: str, previous_report: Optional[Report] = None, activity_id: int = 1) -> Report:
    exercises = []
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]  # skip empty lines
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.startswith('Set'):
            i += 1
            continue

        # Line is an exercise name
        exercise_name = line
        sets_list = []
        i += 1
        set_index = 0
        while i < len(lines) and lines[i].startswith('Set'):
            set_line = lines[i]
            match = re.match(r"Set \d+: (\d+) ?(kg|reps) x (\d+)", set_line)
            if match:
                weight_or_reps, unit, reps = match.groups()
                reps = int(reps)
                weight = float(weight_or_reps) if unit == 'kg' else 0
                volume = weight * reps

                # Progressive overload from previous report
                po = ProgressiveOverload()
                if previous_report:
                    prev_exercise = next((e for e in previous_report.exercises if e.name == exercise_name), None)
                    if prev_exercise and set_index < len(prev_exercise.sets):
                        last_set = prev_exercise.sets[set_index]
                        po.last_reps = last_set.reps
                        po.last_weight = last_set.weight
                        po.last_volume = last_set.volume

                po.current_reps = reps
                po.current_weight = weight
                po.current_volume = volume

                sets_list.append(Set(reps=reps, weight=weight, volume=volume, progressive_overload=po))

            i += 1
            set_index += 1

        exercises.append(Exercise(name=exercise_name, sets=sets_list))

    return Report(activity_id=activity_id, exercises=exercises)

def report_to_text(report: Report) -> str:
    lines = []
    for exercise in report.exercises:
        lines.append(exercise.name)
        for idx, s in enumerate(exercise.sets, start=1):
            weight_str = f"{s.weight} kg" if s.weight else ""
            line = f"Set {idx}: {weight_str} x {s.reps} reps (Volume: {s.volume})"
            po = s.progressive_overload
            if po.last_volume or po.last_reps or po.last_weight:
                line += f" | Last: {po.last_weight} kg x {po.last_reps} reps (Volume: {po.last_volume})"
            lines.append(line)
        lines.append("")  # blank line between exercises
    return "\n".join(lines)

if __name__ == "__main__":
    workout_text = """Triceps Rope Pushdown
Set 1: 29 kg x 10
Set 2: 29 kg x 10
Set 3: 29 kg x 10



Bicep Curl (Cable)
Set 1: 20 kg x 12
Set 2: 20 kg x 12
Set 3: 20 kg x 12
"""

    report = parse_workout(workout_text)
    print(report.model_dump_json(indent=2))
    print(report_to_text(report))
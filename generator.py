# workout_analysis.py
from os import getenv
from auth.models import Report
from hevy_parser import parse_workout, report_to_text
from openai import OpenAI
client = OpenAI(api_key=getenv("LLM_API_KEY"))

def analyze_report(report: Report, model: str = "gpt-4") -> str:
    """
    Converts a Report to text and asks the OpenAI API to analyze it.
    Returns the LLM response as a string.
    """
    workout_text = report_to_text(report)

    prompt = f"""
You are a professional fitness coach. Analyze the following workout report and provide insights:
- Suggest improvements, potential risks, or imbalances
- Highlight exercises with poor progressive overload
- Give tips on reps, sets, or weight adjustments

Workout Report:
{workout_text}

Please provide a clear, structured analysis.
"""

    response = client.responses.create(
        model="deepseek-coder-v2:16b",
        input="Write a one-sentence bedtime story about a unicorn."
    )

    return response.output_text


if __name__ == "__main__":
    workout_text = """Triceps Rope Pushdown
Set 1: 29 kg x 10
Set 2: 29 kg x 10
Set 3: 29 kg x 10"""
    
    report = parse_workout(workout_text)
    analysis = analyze_report(report)
    print(analysis)

from os import getenv
from auth.models import Report
from hevy_parser import parse_workout, report_to_text
from openai import OpenAI
import markdown
from mailer import Mailer
import auth.models as models
client = OpenAI(api_key=getenv("LLM_API_KEY", "ollama"), base_url=getenv("LLM_BASE_URL","http://192.168.1.55:8080/api"))

def analyze_report(report: Report, model: str = "deepseek-coder-v2:16b") -> str: # mistral:7b-instruct-q4_K_M for testing
    workout_text = report_to_text(report)

    prompt = f"""
You are a professional fitness coach. Analyze the following workout report and provide insights:
- Suggest improvements, potential risks, or imbalances
- Highlight exercises with poor progressive overload
- Give tips on reps, sets, or weight adjustments
- Do not tell to seek a professional coach - give the tips yourself.
- Imporve the exercises and change the routine if needed.

my measures are:
Bodyweight: {models.config.measures.bodyweight}kg
Age: {models.config.measures.age}y 
Experience: {models.config.measures.experience}y

Workout Notes:
{report.notes}

Workout Report:
{workout_text}

Please provide a clear, structured analysis, use markdown for clear structure.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            # {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content or "Empty Response."

def send_report(report: Report, model: str = "mistral:7b-instruct-q4_K_M"):
    analyzed = analyze_report(report, model)
    final = "# Hevyzer Report for " + report.name + "\n\n" + analyzed
    report.llm_output = final
    models.reports.save()
    Mailer().send(f"Hevyzer Report - {report.name}", markdown.markdown(final), models.config.emails, html=True)

if __name__ == "__main__":
    workout_text = """Triceps Rope Pushdown
Set 1: 29 kg x 10
Set 2: 29 kg x 10
Set 3: 29 kg x 10"""
    
    report = parse_workout(workout_text)
    analysis = analyze_report(report)
    print(analysis)

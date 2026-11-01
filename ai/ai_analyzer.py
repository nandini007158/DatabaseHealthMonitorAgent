import requests
import json


def analyze_database_health(problems, health_score, metrics):

    prompt = f"""
You are an expert MySQL Database Health Analysis AI Agent.

Your task is to analyze the actual database monitoring information.

DATABASE METRICS:
{json.dumps(metrics, indent=4)}

HEALTH SCORE:
{health_score}/100

DETECTED PROBLEMS:
{json.dumps(problems, indent=4)}

IMPORTANT RULES:

1. Use only the information provided above.
2. Never invent database errors, problems, or measurements.
3. Do not claim that a query is slow unless evidence is provided.
4. If no problems are detected, clearly say that no
   monitored issues were found.
5. Explain possible causes as possibilities, not confirmed facts.
6. Never recommend deleting data or executing SQL automatically.
7. Do not recommend changing database settings without evidence.
8. Give practical preventive monitoring suggestions.

PROVIDE YOUR ANALYSIS IN THIS FORMAT:

1. DATABASE CONDITION
Explain the current database condition.

2. METRIC ANALYSIS
Explain the important database metrics.

3. DETECTED PROBLEMS
Explain each detected problem.
If there are none, clearly mention that.

4. POSSIBLE ROOT CAUSES
Give possible causes only when supported by the evidence.

5. RECOMMENDED ACTIONS
Suggest safe and practical actions.

6. PRIORITY
Choose LOW, MEDIUM, or HIGH and explain why.

Use simple, professional English.
"""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            },
            timeout=180
        )

        response.raise_for_status()

        result = response.json()

        return result["response"]

    except requests.exceptions.RequestException as error:

        return f"AI connection error: {error}"

    except (KeyError, ValueError) as error:

        return f"AI response processing error: {error}"
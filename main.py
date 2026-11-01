from database.monitor import run_health_check
from ai.ai_analyzer import analyze_database_health


def main():

    print("\n======================================")
    print(" AI DATABASE HEALTH MONITORING AGENT")
    print("======================================")

    # Step 1: Monitor the MySQL database
    print("\nSTEP 1: Monitoring MySQL Database")

    report = run_health_check()

    metrics = report["metrics"]
    health_score = report["health_score"]
    overall_health = report["overall_health"]
    problems = report["problems"]
    root_causes = report["root_causes"]

    print("\nDatabase Status:", overall_health)
    print("Health Score:", health_score, "/ 100")

    # Step 2: Display detected problems
    print("\nSTEP 2: Problem Detection")

    if problems:
        for problem in problems:
            print("-", problem)
    else:
        print("No problems detected.")

    # Step 3: Display rule-based investigation
    print("\nSTEP 3: Initial Root Cause Investigation")

    if root_causes:
        for cause in root_causes:
            print("-", cause)
    else:
        print("No root-cause investigation required.")

    # Step 4: Send actual database metrics to AI
    print("\nSTEP 4: Sending Information to Local AI...")
    print("Please wait...")

    ai_result = analyze_database_health(
        problems,
        health_score,
        metrics
    )

    # Step 5: Display AI analysis
    print("\n========== AI ANALYSIS ==========")
    print(ai_result)
    print("=================================")

    print("\nDatabase monitoring and AI analysis completed.")


if __name__ == "__main__":
    main()
from ai.ai_analyzer import analyze_database_health

health_score = 100

metrics = {
    "Active Connections": 2,
    "Failed Connections": 4,
    "Slow Query Log": "ON",
    "Database": "database_health_monitor"
}

problems = []

print("Sending database information to AI...")

result = analyze_database_health(
    problems,
    health_score,
    metrics
)

print("\n========== AI DATABASE ANALYSIS ==========")
print(result)
print("==========================================")
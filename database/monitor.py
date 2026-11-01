try:
    from database.connection import get_connection
except ModuleNotFoundError:
    from connection import get_connection


DATABASE_NAME = "database_health_monitor"


# 1. Collect database metrics
def collect_database_metrics():

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        print("\nCollecting database information...")

        # Database size
        cursor.execute("""
            SELECT ROUND(
                COALESCE(SUM(data_length + index_length), 0)
                / 1024 / 1024, 2
            )
            FROM information_schema.tables
            WHERE table_schema = %s
        """, (DATABASE_NAME,))

        database_size = cursor.fetchone()[0]

        # Table names
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
        """, (DATABASE_NAME,))

        tables = [row[0] for row in cursor.fetchall()]

        # Active connections
        cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
        active_connections = int(cursor.fetchone()[1])

        # Failed connections
        cursor.execute("SHOW GLOBAL STATUS LIKE 'Aborted_connects'")
        failed_connections = int(cursor.fetchone()[1])

        # Slow query logging
        cursor.execute("SHOW VARIABLES LIKE 'slow_query_log'")
        slow_query_log = cursor.fetchone()[1]

        # Index information
        cursor.execute("""
            SELECT table_name, index_name, column_name
            FROM information_schema.statistics
            WHERE table_schema = %s
        """, (DATABASE_NAME,))

        indexes = [
            {
                "table": row[0],
                "index": row[1],
                "column": row[2]
            }
            for row in cursor.fetchall()
        ]

        metrics = {
            "database": DATABASE_NAME,
            "database_status": "HEALTHY",
            "database_size_mb": float(database_size or 0),
            "tables": tables,
            "table_count": len(tables),
            "active_connections": active_connections,
            "failed_connections": failed_connections,
            "slow_query_log": slow_query_log,
            "indexes": indexes
        }

        print("Database information collected successfully.")

        return metrics

    except Exception as error:

        print("Database monitoring error:", error)

        return {
            "database": DATABASE_NAME,
            "database_status": "UNHEALTHY",
            "error": str(error)
        }

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# 2. Calculate database health score
def calculate_health_score(metrics):

    if metrics.get("database_status") != "HEALTHY":
        return 0, "CRITICAL"

    score = 100

    failed_connections = metrics["failed_connections"]
    active_connections = metrics["active_connections"]
    slow_query_log = metrics["slow_query_log"]

    if failed_connections > 10:
        score -= 30
    elif failed_connections > 5:
        score -= 15

    if active_connections > 50:
        score -= 30
    elif active_connections > 20:
        score -= 15

    if slow_query_log.upper() == "OFF":
        score -= 10

    if score >= 80:
        status = "HEALTHY"
    elif score >= 50:
        status = "WARNING"
    else:
        status = "CRITICAL"

    return score, status


# 3. Detect database problems
def detect_problems(metrics):

    problems = []

    if metrics.get("database_status") != "HEALTHY":
        problems.append("Database monitoring failed.")
        return problems

    if metrics["failed_connections"] > 10:
        problems.append("High number of failed database connections")

    elif metrics["failed_connections"] > 5:
        problems.append("Increased number of failed database connections")

    if metrics["active_connections"] > 50:
        problems.append("Very high number of active database connections")

    elif metrics["active_connections"] > 20:
        problems.append("High number of active database connections")

    if metrics["slow_query_log"].upper() == "OFF":
        problems.append("Slow query logging is disabled")

    return problems


# 4. Investigate possible root causes
def investigate_root_causes(problems):

    root_causes = []

    for problem in problems:

        if "failed database connections" in problem.lower():

            root_causes.append(
                "Possible causes include incorrect credentials, "
                "network interruptions, or connection configuration issues."
            )

        elif "active database connections" in problem.lower():

            root_causes.append(
                "Possible causes include high application traffic "
                "or connections that are not being closed properly."
            )

        elif "slow query logging" in problem.lower():

            root_causes.append(
                "Slow query logging is disabled, so slow queries "
                "may not be recorded for investigation."
            )

        elif "monitoring failed" in problem.lower():

            root_causes.append(
                "Check the MySQL connection and user permissions."
            )

    return root_causes


# 5. Investigate currently running MySQL queries
def investigate_active_queries():

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        print("\nInvestigating active MySQL queries...")

        cursor.execute("SHOW FULL PROCESSLIST")

        process_list = cursor.fetchall()

        long_running_queries = []

        for process in process_list:

            query_time = process.get("Time", 0)
            command = process.get("Command")
            query = process.get("Info")

            if (
                command != "Sleep"
                and query_time is not None
                and query_time >= 5
                and query
            ):

                long_running_queries.append({
                    "connection_id": process.get("Id"),
                    "user": process.get("User"),
                    "database": process.get("db"),
                    "running_time_seconds": query_time,
                    "query": query
                })

        print(
            "Long-running queries found:",
            len(long_running_queries)
        )

        return long_running_queries

    except Exception as error:

        print("Query investigation error:", error)

        return []

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# 6. Run complete database health check
def run_health_check():

    metrics = collect_database_metrics()

    health_score, overall_health = calculate_health_score(metrics)

    problems = detect_problems(metrics)

    root_causes = investigate_root_causes(problems)

    return {
        "metrics": metrics,
        "health_score": health_score,
        "overall_health": overall_health,
        "problems": problems,
        "root_causes": root_causes
    }


# 7. Run monitoring directly when this file is executed
if __name__ == "__main__":

    result = run_health_check()

    print("\n========== DATABASE HEALTH REPORT ==========")

    print("Health Score:", result["health_score"], "/ 100")
    print("Overall Health:", result["overall_health"])

    print("\nDetected Problems:")

    if result["problems"]:
        for problem in result["problems"]:
            print("-", problem)
    else:
        print("No problems detected.")

    print("\nPossible Root Causes:")

    if result["root_causes"]:
        for cause in result["root_causes"]:
            print("-", cause)
    else:
        print("No investigation required.")

    print("\n============================================")
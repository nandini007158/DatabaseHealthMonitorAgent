from connection import get_connection


def check_connection():

    try:
        connection = get_connection()

        if connection.is_connected():
            print("Database Status: HEALTHY")

        connection.close()

    except Exception as e:
        print("Database Status: UNHEALTHY")
        print("Error:", e)


def get_database_size():

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT
        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2)
    FROM information_schema.tables
    WHERE table_schema = 'database_health_monitor'
    """

    cursor.execute(query)

    result = cursor.fetchone()

    print("Database Size:", result[0], "MB")

    cursor.close()
    connection.close()


def get_tables():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'database_health_monitor'
    """)

    tables = cursor.fetchall()

    print("\nTables:")

    for table in tables:
        print("-", table[0])

    cursor.close()
    connection.close()


def get_active_connections():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SHOW STATUS LIKE 'Threads_connected'")

    result = cursor.fetchone()

    print("\nActive Connections:", result[1])

    cursor.close()
    connection.close()


def check_slow_queries():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SHOW VARIABLES LIKE 'slow_query_log'")

    result = cursor.fetchone()

    print("\nSlow Query Log:", result[1])

    cursor.close()
    connection.close()


def get_indexes():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            table_name,
            index_name,
            column_name
        FROM information_schema.statistics
        WHERE table_schema = 'database_health_monitor'
        ORDER BY table_name, index_name
    """)

    indexes = cursor.fetchall()

    print("\nIndexes:")

    for index in indexes:
        print("-", index[0], "|", index[1], "|", index[2])

    cursor.close()
    connection.close()


def get_database_errors():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SHOW GLOBAL STATUS LIKE 'Aborted_connects'")

    result = cursor.fetchone()

    print("\nFailed Connections:", result[1])

    cursor.close()
    connection.close()


def calculate_health_score():

    score = 100

    connection = get_connection()
    cursor = connection.cursor()

    # Check failed connections
    cursor.execute("SHOW GLOBAL STATUS LIKE 'Aborted_connects'")

    result = cursor.fetchone()

    failed_connections = int(result[1])

    if failed_connections > 10:
        score -= 30
    elif failed_connections > 5:
        score -= 15

    # Check active connections
    cursor.execute("SHOW STATUS LIKE 'Threads_connected'")

    result = cursor.fetchone()

    active_connections = int(result[1])

    if active_connections > 50:
        score -= 30
    elif active_connections > 20:
        score -= 15

    # Check slow query log
    cursor.execute("SHOW VARIABLES LIKE 'slow_query_log'")

    result = cursor.fetchone()

    slow_query_log = result[1]

    if slow_query_log.upper() == "OFF":
        score -= 10

    cursor.close()
    connection.close()

    print("\nCalculating Database Health Score...")

    print("Failed Connections:", failed_connections)

    print("Active Connections:", active_connections)

    print("Slow Query Log:", slow_query_log)

    print("Health Score:", score, "/ 100")

    if score >= 80:
        print("Overall Health: HEALTHY")
    elif score >= 50:
        print("Overall Health: WARNING")
    else:
        print("Overall Health: CRITICAL")


def detect_problems():

    connection = get_connection()
    cursor = connection.cursor()

    problems = []

    # Check failed connections
    cursor.execute("SHOW GLOBAL STATUS LIKE 'Aborted_connects'")

    result = cursor.fetchone()

    failed_connections = int(result[1])

    if failed_connections > 10:
        problems.append(
            "High number of failed database connections"
        )

    elif failed_connections > 5:
        problems.append(
            "Increased number of failed database connections"
        )

    # Check active connections
    cursor.execute("SHOW STATUS LIKE 'Threads_connected'")

    result = cursor.fetchone()

    active_connections = int(result[1])

    if active_connections > 50:
        problems.append(
            "Very high number of active database connections"
        )

    elif active_connections > 20:
        problems.append(
            "High number of active database connections"
        )

    # Check slow query log
    cursor.execute("SHOW VARIABLES LIKE 'slow_query_log'")

    result = cursor.fetchone()

    slow_query_log = result[1]

    if slow_query_log.upper() == "OFF":
        problems.append(
            "Slow query logging is disabled"
        )

    cursor.close()
    connection.close()

    print("\nProblem Detection:")

    if len(problems) == 0:

        print("No problems detected.")

    else:

        for problem in problems:
            print("-", problem)


check_connection()
get_database_size()
get_tables()
get_active_connections()
check_slow_queries()
get_indexes()
get_database_errors()
calculate_health_score()
detect_problems()
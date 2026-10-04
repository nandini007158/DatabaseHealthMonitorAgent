import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="database_health_monitor"
)

print("Connected to database successfully!")

cursor = connection.cursor()

cursor.execute("SELECT * FROM customers")

results = cursor.fetchall()

for row in results:
    print(row)

cursor.close()
connection.close()


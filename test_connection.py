import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="Merabeta123",
    port="5433"
)

cursor = conn.cursor()

cursor.execute("""
SELECT COUNT(*)
FROM "Food_wastage_mngnt_Sys".providers
""")

result = cursor.fetchone()

print("Total Providers:", result[0])

cursor.close()
conn.close()
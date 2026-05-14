import psycopg2

conn = psycopg2.connect("postgresql://mindbudget_db_user:W7QDfFNWN26SndPcnBjL1L4RER7OBCSW@dpg-d82dte8g4nts73atjo00-a.oregon-postgres.render.com/mindbudget_db")

cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
tables = cur.fetchall()
print("Tables found:", tables)
cur.close()
conn.close()
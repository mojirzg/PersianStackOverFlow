import psycopg2
import config
conn = psycopg2.connect(host='localhost', database='postgres', user='postgres', password=config.dbpassword)
print("Connecting to database\n	")

cursor = conn.cursor()
print("Connected!\n")


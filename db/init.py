import psycopg2 as postgres

with open("./db/queries/init.sql", "r") as init_qf:
    queries = init_qf.read().split(";")
conn = postgres.connect(user="admin",
            password="qwer",
            host="localhost",
            dbname="intime")
cursor = conn.cursor()
for query in queries:
    if query != "":
        cursor.execute(query + ";")
        conn.commit()
cursor.close()
conn.close()
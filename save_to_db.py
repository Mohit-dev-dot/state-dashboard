import pandas as pd
import sqlite3

print("Reading excel...")

df = pd.read_excel("data/Project.xlsx")

print("Creating database...")

conn = sqlite3.connect("data/project.db")

df.to_sql("states", conn, if_exists="replace", index=False)

conn.close()

print("Saved to database successfully!")

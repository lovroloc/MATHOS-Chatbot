import mysql.connector
import json
import os
from dotenv import load_dotenv

load_dotenv()
conn = mysql.connector.connect(
    host="localhost", port=3306,
    user="chatbot", password=os.getenv("MYSQL_PASSWORD"), database="intranet"
)
cursor = conn.cursor()

cursor.execute("""
    SELECT DISTINCT c.code, c.nameHr, c.ects,
           s.name AS study, spc.year, spc.semester, spc.type AS component_type,
           e.firstName, e.lastName, a.role
    FROM courses c
    JOIN studyProgrammeComponents spc ON spc.courseId = c.id
    JOIN studies s ON s.id = spc.studyId
    JOIN implementationProgrammeComponents ipc ON ipc.studyProgrammeComponentId = spc.id
    JOIN assignments a ON a.implementationProgrammeComponentId = ipc.id
    JOIN employees e ON e.id = a.employeeId
""")

columns = [desc[0] for desc in cursor.description]
rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

with open("data/teaching.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")

print("Ukupno redaka (kolegij-studij-nastavnik):", len(rows))
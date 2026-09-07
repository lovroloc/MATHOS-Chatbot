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
    SELECT e.id, e.firstName, e.lastName, e.email, e.room, e.phoneNumber, e.scholarUrl,
           t.nameHr AS title,
           rg.nameHr AS chair,
           GROUP_CONCAT(DISTINCT et.nameHr SEPARATOR ', ') AS types
    FROM employees e
    LEFT JOIN titles t ON e.titleId = t.id
    LEFT JOIN researchGroups rg ON e.researchGroupId = rg.id
    LEFT JOIN employeesEmployeeTypes eet ON e.id = eet.employeesId
    LEFT JOIN employeeTypes et ON eet.employeeTypesId = et.id
    GROUP BY e.id
""")

columns = [desc[0] for desc in cursor.description]
staff = [dict(zip(columns, row)) for row in cursor.fetchall()]

with open("data/staff.jsonl", "w", encoding="utf-8") as f:
    for s in staff:
        f.write(json.dumps(s, ensure_ascii=False, default=str) + "\n")

print("Ukupno osoblja:", len(staff))
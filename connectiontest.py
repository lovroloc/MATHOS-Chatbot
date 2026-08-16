import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    port=3306,          # prilagodi ako je drugačije
    user="chatbot",
    password="eZi#i0o9i",
    database="intranet"
)
print("Spojeno:", conn.is_connected())

cursor = conn.cursor()
#cursor.execute("SHOW TABLES")
#for (table, ) in cursor.fetchall():
#    print(table)
priority_tables = [
    "employees", "titles", "chairs", "employeeTypes", "employeesEmployeeTypes",
    "courses", "assignments",
    "studies", "studyProgrammeComponents", "implementationProgrammeComponents", "studyYearMetadatas",
    "notifications",
    "events", "seminarTypes",
]
#for t in priority_tables:
#    print(f"\n=== {t} ===")
#    cursor.execute(f"DESCRIBE {t}")
#    for row in cursor.fetchall():
#        print(row)

''' 
cursor.execute("""
    SELECT DISTINCT c.nameHr, c.ects, e.firstName, e.lastName, a.role
    FROM courses c
    JOIN studyProgrammeComponents spc ON spc.courseId = c.id
    JOIN implementationProgrammeComponents ipc ON ipc.studyProgrammeComponentId = spc.id
    JOIN assignments a ON a.implementationProgrammeComponentId = ipc.id
    JOIN employees e ON e.id = a.employeeId
    LIMIT 10
""")
for row in cursor.fetchall():
    print(row)
'''
''' 
cursor.execute("""
    SELECT courseId, COUNT(*) as cnt
    FROM studyProgrammeComponents
    GROUP BY courseId
    HAVING cnt > 1
    LIMIT 10
""")
for row in cursor.fetchall():
    print(row)
'''

'''
# Usporedba s WP aktualne_obavijesti
cursor.execute("SELECT title, supertitle, subtitle, LEFT(text, 100), startDate, endDate FROM notifications ORDER BY createdAt DESC LIMIT 5")
for row in cursor.fetchall():
    print(row)

# Test articleId mosta prema WordPressu
cursor.execute("SELECT id, firstName, lastName, articleId FROM employees WHERE articleId IS NOT NULL LIMIT 5")
for row in cursor.fetchall():
    print(row)
'''

#cursor.execute("SELECT COUNT(*), MIN(startDate), MAX(startDate) FROM notifications")
#print(cursor.fetchone())


import requests
''' 
r = requests.get("https://www.mathos.unios.hr/wp-json/wp/v2/moj_profil/76")
print(r.status_code)
print(r.json().get("title", {}).get("rendered"))
print(r.json().get("content", {}).get("rendered", "")[:500])
'''

''' 
r = requests.get("https://www.mathos.unios.hr/wp-json/wp/v2/aktualne_obavijesti", params={"per_page": 1})
print("WP total:", r.headers.get("X-WP-Total"))
r2 = requests.get("https://www.mathos.unios.hr/wp-json/wp/v2/aktualne_obavijesti", params={"per_page": 5, "orderby": "date", "order": "desc"})
for item in r2.json():
    print(item["title"]["rendered"], item["date"])
'''

r = requests.get("https://www.mathos.unios.hr/wp-json/wp/v2/kolegiji", params={"per_page": 1})
data = r.json()[0]
print(data["title"]["rendered"])
print(data["content"]["rendered"][:1000])
print(data["link"])
print(repr(data["content"]["rendered"]))
print("Duljina:", len(data["content"]["rendered"]))
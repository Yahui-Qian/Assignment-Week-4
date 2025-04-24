#!/usr/bin/env python3
# professor_assignment.py
# Assign professors to course sections to maximize total satisfaction

import pulp as pl
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD

# ---- Data ----
professors = ["Prof1", "Prof2", "Prof3"]
courses    = ["Marketing", "Finance", "Production"]
semesters  = ["Fall", "Spring"]

# Semester satisfaction
sem_pref = {
    ("Prof1", "Fall"):   3, ("Prof1", "Spring"): 4,
    ("Prof2", "Fall"):   5, ("Prof2", "Spring"): 3,
    ("Prof3", "Fall"):   4, ("Prof3", "Spring"): 4,
}

# Course satisfaction
course_pref = {
    ("Prof1", "Marketing"):  6, ("Prof1", "Finance"):  5, ("Prof1", "Production"): 4,
    ("Prof2", "Marketing"):  4, ("Prof2", "Finance"):  6, ("Prof2", "Production"): 5,
    ("Prof3", "Marketing"):  5, ("Prof3", "Finance"):  4, ("Prof3", "Production"): 6,
}

# ---- Model ----
model = LpProblem("Professor_Course_Assignment", LpMaximize)

# Decision variables: x[p,c,s] = number of sections professor p teaches of course c in semester s
x = {
    (p,c,s): LpVariable(f"x_{p}_{c}_{s}", lowBound=0, cat="Integer")
    for p in professors
    for c in courses
    for s in semesters
}

# Objective: maximize total satisfaction
model += lpSum(
    (sem_pref[p,s] + course_pref[p,c]) * x[p,c,s]
    for p in professors
    for c in courses
    for s in semesters
), "Total_Satisfaction"

# 1) Exactly 4 sections of each course per year
for c in courses:
    model += lpSum(x[p,c,s] for p in professors for s in semesters) == 4, f"TotalSections_{c}"

# 2) At least 1 section of each course each semester
for c in courses:
    for s in semesters:
        model += lpSum(x[p,c,s] for p in professors) >= 1, f"Min_{c}_{s}"

# 3) Each professor teaches exactly 4 sections total
for p in professors:
    model += lpSum(x[p,c,s] for c in courses for s in semesters) == 4, f"Load_{p}"

# ---- Solve ----
model.solve(PULP_CBC_CMD(msg=False))

# ---- Output ----
print(f"Status: {pl.LpStatus[model.status]}")
print(f"Optimal Total Satisfaction = {pl.value(model.objective):.0f}\n")
print("Assignments:")
for p in professors:
    for s in semesters:
        for c in courses:
            v = x[p,c,s].varValue
            if v > 0:
                print(f"  {p} teaches {int(v)} section(s) of {c} in {s}")

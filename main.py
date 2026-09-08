from scheduler.data_loader import load_all
from scheduler.ranking import rank_classes, rank_teachers
from scheduler.allocator import get_eligible_teachers
from scheduler.generator import generate_timetable, save_routine

data = load_all()
teachers = data["teachers"]
classes = data["classes"]

print("Teachers:", len(teachers["teachers"]))
print("Classes:", len(classes["classes"]))

sorted_classes = rank_classes(classes["classes"])
print("\n--- Class Ranking (higher rank first) ---")
for cls in sorted_classes:
    print(" ", cls["class_name"], cls["rank"])

ranked_teachers = rank_teachers(teachers["teachers"])
print("\n--- Teacher Ranking (least flexible first) ---")
for teacher in ranked_teachers:
    available = len(teacher["available_periods"])
    print(" ", teacher["empid"], teacher["teacher_name"], "available_periods:", available)

eligible = get_eligible_teachers(
    teachers["teachers"], "VI", "Mathematics"
)
print("\n--- Eligible Teachers for VI Mathematics ---")
for teacher in rank_teachers(eligible):
    print(" ", teacher["empid"], teacher["teacher_name"])

result = generate_timetable(data)
report = result["validation"]
mapping = result["mapping"]
timetable = result["timetable"]

print("\n--- Mapping Sample (VI-A) ---")
for subject, teacher in mapping["VI-A"].items():
    if teacher:
        print(" ", subject, "->", teacher["teacher_name"])
    else:
        print(" ", subject, "-> No teacher")

print("\n--- Timetable Sample (VI-A) ---")
for day in ["MON", "TUE", "WED", "THU", "FRI", "SAT"]:
    slots = timetable["VI-A"][day]
    row = []
    for period, slot in slots.items():
        if slot is None:
            row.append(f"{period}:---")
        else:
            row.append(f"{period}:{slot['subject'][:4]}")
    print(" ", day, " | ".join(row))

print("\n--- Validation Report ---")
print("Valid:", report["valid"])
print("Teacher clashes:", len(report["teacher_clashes"]))
print("Class clashes:", len(report["class_clashes"]))
print("Availability violations:", len(report["availability_violations"]))
print("Daily load violations:", len(report["daily_load_violations"]))
print("Eligibility violations:", len(report["eligibility_violations"]))
print("Subject lock violations:", len(report["subject_lock_violations"]))
print("Missing subject periods:", len(report["missing_subjects"]))
print("Daily period limit violations:", len(report["daily_period_limit_violations"]))
print("Empty slots:", report["empty_slots"], "/", report["total_slots"])

if report["missing_subjects"]:
    print("\nUnresolved conflicts (teacher capacity exceeded):")
    for missing in report["missing_subjects"][:10]:
        print(
            " ",
            missing["class_section"],
            missing["subject"],
            f"{missing['placed']}/{missing['required']}",
        )

path = save_routine(timetable)
print("\nRoutine saved to:", path)

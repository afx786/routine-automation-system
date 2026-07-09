from scheduler.data_loader import load_teachers, load_classes
from scheduler.ranking import rank_classes
from scheduler.allocator import get_eligible_teachers
from scheduler.ranking import rank_teachers
from scheduler.allocator import assign_teacher_to_subject
from scheduler.generator import generate_subject_teacher_mapping
from scheduler.workload import initialize_workload
from scheduler.workload import assign_workload
from scheduler.timetable import initialize_timetable
from scheduler.checks import is_class_free
teachers = load_teachers()
classes = load_classes()

print("Teachers:", len(teachers["teachers"]))
print("Classes:", len(classes["classes"]))

classes = load_classes()
sorted_classes = rank_classes(
    classes["classes"]
)

for cls in sorted_classes:
    print( cls["class_name"], cls["rank"])
    
teachers = load_teachers()

eligible = get_eligible_teachers(
    teachers ["teachers"], "VI", "Mathematics",
)
print("Eligible Teachers:")

for teacher in eligible:
    print(teacher["empid"], teacher["teacher_name"])
    
ranked = rank_teachers(eligible)

for teacher in ranked:
    print (teacher["empid"], teacher["teacher_name"])
    
teacher = load_teachers
teacher = assign_teacher_to_subject(teachers["teachers"], "VI", "Mathematics")

print(teacher["empid"], teacher["teacher_name"])

mapping = generate_subject_teacher_mapping(teachers, classes)
print(mapping["VI-A"])

workload = initialize_workload(teachers["teachers"])
print(workload["EMP010"])

teacher = teachers["teachers"][0]
assign_workload(workload, teacher, "VI-A", "Mathematics")
assign_workload(workload, teacher, "VI-B", "Mathematics")
print(workload[teacher["empid"]])

classes = load_classes()
timetable = initialize_timetable(classes)
print(timetable["VI-A"])

print(is_class_free(timetable, "VI-A", "MON", 1))
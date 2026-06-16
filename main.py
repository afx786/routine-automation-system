from scheduler.data_loader import load_teachers, load_classes
from scheduler.ranking import rank_classes
from scheduler.allocator import get_eligible_teachers
from scheduler.ranking import rank_teachers
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
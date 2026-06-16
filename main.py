from scheduler.data_loader import load_teachers, load_classes

teachers = load_teachers()
classes = load_classes()

print("Teachers:", len(teachers["teachers"]))
print("Classes:", len(classes["classes"]))
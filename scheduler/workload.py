def initialize_workload(teachers):
    workload = {}
    for teacher in teachers:
         workload[teacher["empid"]] = {
             "teacher_name" : teacher["teacher_name"],
             "assigned_subjects": [], "assignment_count": 0
        }
    return workload

def assign_workload(workload, teacher, class_section, subject):
    empid = teacher["empid"]
    workload[empid]["assignment_count"] += 1
    workload[empid]["assigned_subjects"].append(
        {"class_section": class_section, "subjects": subject}
    )
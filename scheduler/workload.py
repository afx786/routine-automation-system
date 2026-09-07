def initialize_workload(teachers):
    workload = {}
    for teacher in teachers:
        workload[teacher["empid"]] = {
            "teacher_name": teacher["teacher_name"],
            "assigned_subjects": [],
            "assignment_count": 0,
            "daily_periods": {},
            "weekly_periods": 0,
            "projected_weekly": 0
        }
    return workload


def assign_workload(workload, teacher, class_section, subject, day=None):
    empid = teacher["empid"]
    entry = workload[empid]
    entry["assignment_count"] += 1
    if day is not None:
        entry["daily_periods"][day] = entry["daily_periods"].get(day, 0) + 1
        entry["weekly_periods"] += 1
    entry["assigned_subjects"].append(
        {"class_section": class_section, "subjects": subject}
    )


def daily_workload(workload, teacher_id, day):
    return workload[teacher_id]["daily_periods"].get(day, 0)


def weekly_workload(workload, teacher_id):
    return workload[teacher_id]["weekly_periods"]
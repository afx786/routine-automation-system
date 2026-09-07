from scheduler.timetable import DAYS
from scheduler.workload import daily_workload


def is_class_free(timetable, class_section, day, period, teacher_id=None):
    return timetable[class_section][day][period] is None


def is_teacher_free(timetable, teacher_id, day, period):
    for class_section in timetable:
        slot = timetable[class_section][day][period]
        if slot is None:
            continue
        if slot["teacher_id"] == teacher_id:
            return False
    return True


def is_eligible(teacher, class_name, subject_name):
    for subject in teacher["subjects"]:
        if (
            subject["subject_name"] == subject_name
            and class_name in subject["classes"]
        ):
            return True
    return False


def is_teacher_available(teacher, period):
    return period in teacher["available_periods"]


def teacher_daily_limit(teacher, workload, day):
    return daily_workload(workload, teacher["empid"], day) < teacher["max_periods_per_day"]


def locked_teacher(timetable, class_section, subject):
    for day in DAYS:
        for slot in timetable[class_section][day].values():
            if slot is None:
                continue
            if slot["subject"] == subject:
                return slot["teacher_id"]
    return None


def contract_teacher_check(timetable, class_section, subject, teacher_id):
    existing = locked_teacher(timetable, class_section, subject)
    if existing is None:
        return True
    return existing == teacher_id


def class_periods_on_day(timetable, class_section, day):
    return sum(
        1 for slot in timetable[class_section][day].values() if slot is not None
    )


def under_class_daily_limit(timetable, class_section, day, class_working_days):
    return class_periods_on_day(timetable, class_section, day) < class_working_days[day]


def can_assign(timetable, workload, teacher, class_section, subject, day, period, class_working_days):
    class_name = class_section.split("-")[0]
    return (
        is_class_free(timetable, class_section, day, period)
        and is_teacher_free(timetable, teacher["empid"], day, period)
        and is_teacher_available(teacher, period)
        and teacher_daily_limit(teacher, workload, day)
        and is_eligible(teacher, class_name, subject)
        and contract_teacher_check(timetable, class_section, subject, teacher["empid"])
        and under_class_daily_limit(timetable, class_section, day, class_working_days)
    )
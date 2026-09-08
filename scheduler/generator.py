import json
from pathlib import Path

from scheduler.data_loader import load_all
from scheduler.ranking import rank_classes, class_rank_map
from scheduler.allocator import assign_teacher_to_subject
from scheduler.timetable import initialize_timetable, DAYS
from scheduler.workload import initialize_workload, assign_workload
from scheduler.checks import can_assign
from scheduler.validator import validate_timetable

OUTPUT_PATH = Path("data/generated_routine.json")


def generate_subject_teacher_mapping(teachers, classes):
    mapping = {}
    sorted_classes = rank_classes(classes["classes"])
    rank_map = class_rank_map(classes["classes"])
    workload = initialize_workload(teachers["teachers"])

    for cls in sorted_classes:
        class_name = cls["class_name"]
        for subject in cls["subjects"]:
            subject_name = subject["subject_name"]
            locked_teacher_id = None
            for section in cls["sections"]:
                section_key = f"{class_name}-{section}"
                if section_key not in mapping:
                    mapping[section_key] = {}

                teacher = assign_teacher_to_subject(
                    teachers["teachers"],
                    class_name,
                    subject_name,
                    rank_map=rank_map,
                    workload=workload,
                    locked_teacher_id=locked_teacher_id
                )

                if teacher:
                    mapping[section_key][subject_name] = {
                        "teacher_id": teacher["empid"],
                        "teacher_name": teacher["teacher_name"]
                    }
                    assign_workload(workload, teacher, section_key, subject_name)
                    workload[teacher["empid"]]["projected_weekly"] += subject["periods_per_week"]
                    locked_teacher_id = teacher["empid"]
                else:
                    mapping[section_key][subject_name] = None

    return mapping


def build_teacher_index(teachers):
    return {
        teacher["empid"]: teacher
        for teacher in teachers
    }


def order_subjects(cls):
    return sorted(
        cls["subjects"],
        key=lambda subject: subject["periods_per_week"],
        reverse=True
    )


def allocate_subject_periods(timetable, section_key, subject_name, required, teacher, working_days, workload):
    active_days = [day for day in DAYS if working_days.get(day, 0) > 0]
    placed = 0

    while placed < required:
        before = placed
        for day in active_days:
            if placed >= required:
                break
            if try_place_period(timetable, section_key, subject_name, day, working_days, teacher, workload):
                placed += 1
        if placed == before:
            break

    return placed


def try_place_period(timetable, section_key, subject_name, day, working_days, teacher, workload):
    for period in range(1, working_days[day] + 1):
        if not can_assign(
            timetable,
            workload,
            teacher,
            section_key,
            subject_name,
            day,
            period,
            working_days
        ):
            continue

        timetable[section_key][day][period] = {
            "subject": subject_name,
            "teacher_id": teacher["empid"],
            "teacher_name": teacher["teacher_name"]
        }
        assign_workload(workload, teacher, section_key, subject_name, day)
        return True

    return False


def allocate_class_section(timetable, cls, section_key, mapping, workload, teacher_index):
    working_days = cls["working_days"]

    for subject in order_subjects(cls):
        subject_name = subject["subject_name"]
        required = subject["periods_per_week"]
        assigned = mapping[section_key].get(subject_name)

        if assigned is None:
            continue

        teacher = teacher_index[assigned["teacher_id"]]
        allocate_subject_periods(
            timetable,
            section_key,
            subject_name,
            required,
            teacher,
            working_days,
            workload
        )


def allocate_timetable(timetable, classes, mapping, teachers):
    workload = initialize_workload(teachers["teachers"])
    teacher_index = build_teacher_index(teachers["teachers"])

    for cls in rank_classes(classes["classes"]):
        class_name = cls["class_name"]
        for section in cls["sections"]:
            section_key = f"{class_name}-{section}"
            allocate_class_section(
                timetable,
                cls,
                section_key,
                mapping,
                workload,
                teacher_index
            )

    return timetable, workload


def generate_timetable(data=None):
    if data is None:
        data = load_all()

    teachers = data["teachers"]
    classes = data["classes"]

    mapping = generate_subject_teacher_mapping(teachers, classes)
    timetable = initialize_timetable(classes)
    timetable, workload = allocate_timetable(timetable, classes, mapping, teachers)
    report = validate_timetable(timetable, classes, teachers["teachers"])

    return {
        "teachers": teachers,
        "classes": classes,
        "mapping": mapping,
        "timetable": timetable,
        "workload": workload,
        "validation": report
    }


def save_routine(timetable, path=OUTPUT_PATH):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(timetable, file, indent=2)
    return path

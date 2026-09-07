from scheduler.timetable import DAYS
from scheduler.checks import is_eligible


def build_teacher_index(teachers):
    return {teacher["empid"]: teacher for teacher in teachers}


def class_name_of(section_key):
    return section_key.split("-")[0]


def find_teacher_clashes(timetable):
    clashes = []
    for day in DAYS:
        for period in range(1, 7):
            seen = {}
            for section_key in timetable:
                slot = timetable[section_key][day].get(period)
                if slot is None:
                    continue
                teacher_id = slot["teacher_id"]
                if teacher_id in seen:
                    clashes.append({
                        "day": day,
                        "period": period,
                        "teacher_id": teacher_id,
                        "class_sections": [seen[teacher_id], section_key]
                    })
                else:
                    seen[teacher_id] = section_key
    return clashes


def find_class_clashes(timetable):
    clashes = []
    for day in DAYS:
        for section_key in timetable:
            for period, slot in timetable[section_key][day].items():
                if slot is None:
                    continue
                if not (isinstance(slot, dict) and "subject" in slot and "teacher_id" in slot):
                    clashes.append({
                        "day": day,
                        "period": period,
                        "class_section": section_key,
                        "slot": slot
                    })
    return clashes


def find_availability_violations(timetable, teachers):
    violations = []
    index = build_teacher_index(teachers)
    for day in DAYS:
        for section_key in timetable:
            for period, slot in timetable[section_key][day].items():
                if slot is None:
                    continue
                teacher = index[slot["teacher_id"]]
                if period not in teacher["available_periods"]:
                    violations.append({
                        "day": day,
                        "period": period,
                        "class_section": section_key,
                        "teacher_id": teacher["empid"]
                    })
    return violations


def find_daily_load_violations(timetable, teachers):
    index = build_teacher_index(teachers)
    counts = {}
    for day in DAYS:
        for section_key in timetable:
            for period, slot in timetable[section_key][day].items():
                if slot is None:
                    continue
                teacher_id = slot["teacher_id"]
                counts[(teacher_id, day)] = counts.get((teacher_id, day), 0) + 1
    violations = []
    for (teacher_id, day), count in counts.items():
        teacher = index[teacher_id]
        if count > teacher["max_periods_per_day"]:
            violations.append({
                "teacher_id": teacher_id,
                "day": day,
                "count": count,
                "max": teacher["max_periods_per_day"]
            })
    return violations


def find_eligibility_violations(timetable, teachers):
    violations = []
    index = build_teacher_index(teachers)
    for day in DAYS:
        for section_key in timetable:
            for period, slot in timetable[section_key][day].items():
                if slot is None:
                    continue
                teacher = index[slot["teacher_id"]]
                class_name = class_name_of(section_key)
                if not is_eligible(teacher, class_name, slot["subject"]):
                    violations.append({
                        "day": day,
                        "period": period,
                        "class_section": section_key,
                        "teacher_id": teacher["empid"],
                        "subject": slot["subject"]
                    })
    return violations


def find_subject_lock_violations(timetable):
    violations = []
    for section_key in timetable:
        teacher_by_subject = {}
        for day in DAYS:
            for period, slot in timetable[section_key][day].items():
                if slot is None:
                    continue
                subject = slot["subject"]
                teacher_id = slot["teacher_id"]
                existing = teacher_by_subject.get(subject)
                if existing is not None and existing != teacher_id:
                    violations.append({
                        "class_section": section_key,
                        "subject": subject,
                        "teacher_ids": [existing, teacher_id]
                    })
                else:
                    teacher_by_subject[subject] = teacher_id
    return violations


def count_subject_periods(timetable, section_key):
    counts = {}
    for day in DAYS:
        for slot in timetable[section_key][day].values():
            if slot is None:
                continue
            subject = slot["subject"]
            counts[subject] = counts.get(subject, 0) + 1
    return counts


def find_missing_subjects(timetable, classes):
    missing = []
    for cls in classes["classes"]:
        class_name = cls["class_name"]
        for section in cls["sections"]:
            section_key = f"{class_name}-{section}"
            counts = count_subject_periods(timetable, section_key)
            for subject in cls["subjects"]:
                subject_name = subject["subject_name"]
                required = subject["periods_per_week"]
                placed = counts.get(subject_name, 0)
                if placed < required:
                    missing.append({
                        "class_section": section_key,
                        "subject": subject_name,
                        "required": required,
                        "placed": placed
                    })
    return missing


def count_periods_on_day(timetable, section_key, day):
    return sum(
        1 for slot in timetable[section_key][day].values() if slot is not None
    )


def find_daily_period_limit_violations(timetable, classes):
    violations = []
    for cls in classes["classes"]:
        class_name = cls["class_name"]
        working_days = cls["working_days"]
        for section in cls["sections"]:
            section_key = f"{class_name}-{section}"
            for day, limit in working_days.items():
                count = count_periods_on_day(timetable, section_key, day)
                if count > limit:
                    violations.append({
                        "class_section": section_key,
                        "day": day,
                        "count": count,
                        "max": limit
                    })
    return violations


def count_empty_slots(timetable):
    total = 0
    empty = 0
    for section_key in timetable:
        for day in DAYS:
            for slot in timetable[section_key][day].values():
                total += 1
                if slot is None:
                    empty += 1
    return empty, total


def validate_timetable(timetable, classes, teachers):
    teacher_clashes = find_teacher_clashes(timetable)
    class_clashes = find_class_clashes(timetable)
    availability_violations = find_availability_violations(timetable, teachers)
    daily_load_violations = find_daily_load_violations(timetable, teachers)
    eligibility_violations = find_eligibility_violations(timetable, teachers)
    subject_lock_violations = find_subject_lock_violations(timetable)
    missing_subjects = find_missing_subjects(timetable, classes)
    daily_period_limit_violations = find_daily_period_limit_violations(timetable, classes)
    empty_slots, total_slots = count_empty_slots(timetable)

    violation_count = (
        len(teacher_clashes)
        + len(class_clashes)
        + len(availability_violations)
        + len(daily_load_violations)
        + len(eligibility_violations)
        + len(subject_lock_violations)
        + len(missing_subjects)
        + len(daily_period_limit_violations)
    )

    return {
        "valid": violation_count == 0,
        "teacher_clashes": teacher_clashes,
        "class_clashes": class_clashes,
        "availability_violations": availability_violations,
        "daily_load_violations": daily_load_violations,
        "eligibility_violations": eligibility_violations,
        "subject_lock_violations": subject_lock_violations,
        "missing_subjects": missing_subjects,
        "daily_period_limit_violations": daily_period_limit_violations,
        "empty_slots": empty_slots,
        "total_slots": total_slots,
        "violation_count": violation_count
    }
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scheduler.timetable import initialize_timetable
from scheduler.validator import (
    validate_timetable,
    find_teacher_clashes,
    find_availability_violations,
    find_eligibility_violations,
    find_subject_lock_violations,
    find_missing_subjects,
    find_daily_period_limit_violations,
    count_empty_slots,
)

TEACHERS = [
    {
        "empid": "T1",
        "teacher_name": "Teacher One",
        "max_periods_per_day": 4,
        "available_periods": [1, 2, 3, 4],
        "subjects": [{"subject_name": "Math", "classes": ["VI"]}],
    },
    {
        "empid": "T2",
        "teacher_name": "Teacher Two",
        "max_periods_per_day": 5,
        "available_periods": [1, 2, 3, 4, 5, 6],
        "subjects": [{"subject_name": "Science", "classes": ["VI"]}],
    },
    {
        "empid": "T3",
        "teacher_name": "Teacher Three",
        "max_periods_per_day": 4,
        "available_periods": [1, 3],
        "subjects": [{"subject_name": "Math", "classes": ["VI"]}],
    },
]

CLASSES = {
    "classes": [
        {
            "class_name": "VI",
            "rank": 9,
            "sections": ["A", "B"],
            "working_days": {"MON": 4, "TUE": 4, "WED": 4, "THU": 4, "FRI": 4, "SAT": 2},
            "subjects": [
                {"subject_name": "Math", "periods_per_week": 3},
                {"subject_name": "Science", "periods_per_week": 2},
            ],
        },
    ]
}


def build_violating_timetable():
    timetable = initialize_timetable(CLASSES)
    slot = lambda subject, teacher_id: {"subject": subject, "teacher_id": teacher_id}

    timetable["VI-A"]["MON"][1] = slot("Math", "T1")
    timetable["VI-B"]["MON"][1] = slot("Math", "T1")
    timetable["VI-A"]["MON"][2] = slot("Math", "T3")
    timetable["VI-A"]["MON"][3] = slot("Math", "T1")
    timetable["VI-A"]["MON"][4] = slot("Science", "T2")
    timetable["VI-A"]["MON"][5] = slot("Science", "T2")
    timetable["VI-A"]["TUE"][1] = slot("Science", "T2")
    timetable["VI-A"]["TUE"][3] = slot("Math", "T1")
    timetable["VI-B"]["MON"][2] = slot("Math", "T2")

    return timetable


def test_validate_timetable_detects_all_violations():
    timetable = build_violating_timetable()
    report = validate_timetable(timetable, CLASSES, TEACHERS)

    assert report["valid"] is False
    assert len(report["teacher_clashes"]) == 1
    assert len(report["availability_violations"]) == 1
    assert len(report["daily_load_violations"]) == 0
    assert len(report["eligibility_violations"]) == 1
    assert len(report["subject_lock_violations"]) == 2
    assert len(report["missing_subjects"]) == 2
    assert len(report["daily_period_limit_violations"]) == 1


def test_find_teacher_clashes():
    timetable = build_violating_timetable()
    clashes = find_teacher_clashes(timetable)
    assert clashes[0]["day"] == "MON"
    assert clashes[0]["period"] == 1
    assert clashes[0]["teacher_id"] == "T1"


def test_find_availability_violations():
    timetable = build_violating_timetable()
    violations = find_availability_violations(timetable, TEACHERS)
    assert violations[0]["teacher_id"] == "T3"
    assert violations[0]["period"] == 2


def test_find_eligibility_violations():
    timetable = build_violating_timetable()
    violations = find_eligibility_violations(timetable, TEACHERS)
    assert violations[0]["teacher_id"] == "T2"
    assert violations[0]["subject"] == "Math"


def test_find_subject_lock_violations():
    timetable = build_violating_timetable()
    violations = find_subject_lock_violations(timetable)
    assert len(violations) == 2


def test_find_missing_subjects():
    timetable = build_violating_timetable()
    missing = find_missing_subjects(timetable, CLASSES)
    missing_by_section = {m["class_section"] + ":" + m["subject"]: m for m in missing}
    assert "VI-B:Science" in missing_by_section
    assert "VI-B:Math" in missing_by_section


def test_find_daily_period_limit_violations():
    timetable = build_violating_timetable()
    violations = find_daily_period_limit_violations(timetable, CLASSES)
    assert violations[0]["class_section"] == "VI-A"
    assert violations[0]["count"] == 5


def test_count_empty_slots():
    timetable = initialize_timetable(CLASSES)
    empty, total = count_empty_slots(timetable)
    assert empty == total


def test_valid_timetable_passes():
    timetable = initialize_timetable(CLASSES)
    slot = lambda subject, teacher_id: {"subject": subject, "teacher_id": teacher_id}

    timetable["VI-A"]["MON"][1] = slot("Math", "T1")
    timetable["VI-A"]["MON"][2] = slot("Science", "T2")
    timetable["VI-A"]["TUE"][1] = slot("Math", "T1")
    timetable["VI-A"]["TUE"][2] = slot("Science", "T2")
    timetable["VI-A"]["WED"][1] = slot("Math", "T1")
    timetable["VI-A"]["WED"][2] = slot("Science", "T2")

    timetable["VI-B"]["THU"][1] = slot("Math", "T1")
    timetable["VI-B"]["THU"][2] = slot("Science", "T2")
    timetable["VI-B"]["FRI"][1] = slot("Math", "T1")
    timetable["VI-B"]["FRI"][2] = slot("Science", "T2")
    timetable["VI-B"]["SAT"][1] = slot("Math", "T1")
    timetable["VI-B"]["SAT"][2] = slot("Science", "T2")

    report = validate_timetable(timetable, CLASSES, TEACHERS)
    assert report["valid"] is True

    empty, total = count_empty_slots(timetable)
    assert empty == total - 12

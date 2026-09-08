import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scheduler.checks import (
    is_class_free,
    is_teacher_free,
    is_teacher_available,
    is_eligible,
    teacher_daily_limit,
    locked_teacher,
    contract_teacher_check,
    class_periods_on_day,
    can_assign,
)
from scheduler.workload import initialize_workload, assign_workload
from scheduler.timetable import initialize_timetable

TEACHERS = [
    {
        "empid": "T1",
        "teacher_name": "Teacher One",
        "max_periods_per_day": 4,
        "available_periods": [1, 2, 3, 4],
        "subjects": [
            {"subject_name": "Math", "classes": ["VI"]},
        ],
    },
    {
        "empid": "T2",
        "teacher_name": "Teacher Two",
        "max_periods_per_day": 5,
        "available_periods": [1, 2, 3],
        "subjects": [
            {"subject_name": "Science", "classes": ["VI"]},
        ],
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


def build_timetable():
    return initialize_timetable(CLASSES)


def test_is_class_free_true_when_empty():
    timetable = build_timetable()
    assert is_class_free(timetable, "VI-A", "MON", 1) is True


def test_is_class_free_false_when_occupied():
    timetable = build_timetable()
    timetable["VI-A"]["MON"][1] = {"subject": "Math", "teacher_id": "T1"}
    assert is_class_free(timetable, "VI-A", "MON", 1) is False


def test_is_teacher_free_detects_clash():
    timetable = build_timetable()
    timetable["VI-A"]["MON"][1] = {"subject": "Math", "teacher_id": "T1"}
    assert is_teacher_free(timetable, "T1", "MON", 1) is False
    assert is_teacher_free(timetable, "T1", "MON", 2) is True


def test_is_teacher_available():
    teacher = TEACHERS[0]
    assert is_teacher_available(teacher, 2) is True
    assert is_teacher_available(teacher, 6) is False


def test_is_eligible():
    teacher = TEACHERS[0]
    assert is_eligible(teacher, "VI", "Math") is True
    assert is_eligible(teacher, "VI", "Science") is False
    assert is_eligible(teacher, "VII", "Math") is False


def test_teacher_daily_limit():
    timetable = build_timetable()
    workload = initialize_workload(TEACHERS)
    teacher = TEACHERS[0]
    assert teacher_daily_limit(teacher, workload, "MON") is True
    for period in range(1, 5):
        assign_workload(workload, teacher, "VI-A", "Math", "MON")
    assert teacher_daily_limit(teacher, workload, "MON") is False


def test_locked_teacher_and_contract_check():
    timetable = build_timetable()
    timetable["VI-A"]["MON"][1] = {"subject": "Math", "teacher_id": "T1"}
    assert locked_teacher(timetable, "VI-A", "Math") == "T1"
    assert locked_teacher(timetable, "VI-A", "Science") is None

    assert contract_teacher_check(timetable, "VI-A", "Math", "T1") is True
    assert contract_teacher_check(timetable, "VI-A", "Math", "T2") is False
    assert contract_teacher_check(timetable, "VI-A", "Science", "T2") is True


def test_can_assign_rejects_busy_teacher():
    timetable = build_timetable()
    timetable["VI-B"]["MON"][1] = {"subject": "Math", "teacher_id": "T1"}
    workload = initialize_workload(TEACHERS)
    working_days = CLASSES["classes"][0]["working_days"]
    result = can_assign(
        timetable, workload, TEACHERS[0], "VI-A", "Math", "MON", 1, working_days
    )
    assert result is False


def test_can_assign_rejects_unavailable_period():
    timetable = build_timetable()
    workload = initialize_workload(TEACHERS)
    working_days = CLASSES["classes"][0]["working_days"]
    result = can_assign(
        timetable, workload, TEACHERS[1], "VI-A", "Science", "MON", 4, working_days
    )
    assert result is False


def test_can_assign_accepts_valid_slot():
    timetable = build_timetable()
    workload = initialize_workload(TEACHERS)
    working_days = CLASSES["classes"][0]["working_days"]
    result = can_assign(
        timetable, workload, TEACHERS[0], "VI-A", "Math", "MON", 1, working_days
    )
    assert result is True


def test_class_periods_on_day():
    timetable = build_timetable()
    timetable["VI-A"]["MON"][1] = {"subject": "Math", "teacher_id": "T1"}
    assert class_periods_on_day(timetable, "VI-A", "MON") == 1
    assert class_periods_on_day(timetable, "VI-A", "TUE") == 0

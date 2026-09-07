import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scheduler.allocator import (
    get_eligible_teachers,
    assign_teacher_to_subject,
    subject_max_rank,
)
from scheduler.ranking import class_rank_map
from scheduler.workload import initialize_workload, assign_workload

TEACHERS = {
    "teachers": [
        {
            "empid": "T1",
            "teacher_name": "Teacher One",
            "max_periods_per_day": 6,
            "available_periods": [1, 2, 3, 4, 5, 6],
            "subjects": [
                {"subject_name": "Math", "classes": ["VI", "VII"]},
                {"subject_name": "Science", "classes": ["VI"]},
            ],
        },
        {
            "empid": "T2",
            "teacher_name": "Teacher Two",
            "max_periods_per_day": 5,
            "available_periods": [1, 2, 3],
            "subjects": [
                {"subject_name": "Math", "classes": ["VII", "VIII"]},
            ],
        },
        {
            "empid": "T3",
            "teacher_name": "Teacher Three",
            "max_periods_per_day": 6,
            "available_periods": [1, 2, 3, 4, 5, 6],
            "subjects": [
                {"subject_name": "Science", "classes": ["VIII"]},
            ],
        },
    ]
}

CLASSES = {
    "classes": [
        {"class_name": "VI", "rank": 9, "sections": ["A"], "subjects": []},
        {"class_name": "VII", "rank": 10, "sections": ["A"], "subjects": []},
        {"class_name": "VIII", "rank": 11, "sections": ["A"], "subjects": []},
    ]
}


def test_get_eligible_teachers_filters_by_subject_and_class():
    eligible = get_eligible_teachers(TEACHERS["teachers"], "VI", "Math")
    assert [t["empid"] for t in eligible] == ["T1"]

    eligible = get_eligible_teachers(TEACHERS["teachers"], "VIII", "Math")
    assert [t["empid"] for t in eligible] == ["T2"]


def test_assign_teacher_empty_returns_none():
    result = assign_teacher_to_subject(TEACHERS["teachers"], "IX", "Math")
    assert result is None


def test_assign_teacher_prefers_least_flexible():
    result = assign_teacher_to_subject(TEACHERS["teachers"], "VII", "Math")
    assert result["empid"] == "T2"


def test_assign_teacher_honours_locked_teacher():
    result = assign_teacher_to_subject(
        TEACHERS["teachers"], "VII", "Math", locked_teacher_id="T1"
    )
    assert result["empid"] == "T1"


def test_assign_teacher_prefers_lower_workload():
    workload = initialize_workload(TEACHERS["teachers"])
    assign_workload(workload, TEACHERS["teachers"][0], "VI-A", "Math")
    result = assign_teacher_to_subject(
        TEACHERS["teachers"], "VI", "Math", workload=workload
    )
    assert result["empid"] == "T1"


def test_subject_max_rank_uses_rank_map():
    rank_map = class_rank_map(CLASSES["classes"])
    assert subject_max_rank(TEACHERS["teachers"][0], "Math", rank_map) == 10
    assert subject_max_rank(TEACHERS["teachers"][1], "Math", rank_map) == 11
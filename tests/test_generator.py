import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scheduler.generator import (
    generate_subject_teacher_mapping,
    generate_timetable,
    save_routine,
    allocate_subject_periods,
)
from scheduler.timetable import initialize_timetable, DAYS

WORKING_DAYS = {"MON": 4, "TUE": 4, "WED": 4, "THU": 4, "FRI": 4, "SAT": 2}

DATA = {
    "teachers": {
        "teachers": [
            {
                "empid": "T1",
                "teacher_name": "Teacher One",
                "max_periods_per_day": 4,
                "available_periods": [1, 2, 3, 4],
                "subjects": [
                    {"subject_name": "Math", "classes": ["VI", "VII"]},
                ],
            },
            {
                "empid": "T2",
                "teacher_name": "Teacher Two",
                "max_periods_per_day": 4,
                "available_periods": [1, 2, 3, 4],
                "subjects": [
                    {"subject_name": "Science", "classes": ["VI", "VII"]},
                ],
            },
        ]
    },
    "classes": {
        "classes": [
            {
                "class_name": "VI",
                "rank": 9,
                "sections": ["A", "B"],
                "working_days": WORKING_DAYS,
                "subjects": [
                    {"subject_name": "Math", "periods_per_week": 3},
                    {"subject_name": "Science", "periods_per_week": 2},
                ],
            },
            {
                "class_name": "VII",
                "rank": 10,
                "sections": ["A", "B"],
                "working_days": WORKING_DAYS,
                "subjects": [
                    {"subject_name": "Math", "periods_per_week": 3},
                    {"subject_name": "Science", "periods_per_week": 2},
                ],
            },
        ]
    },
}


def count_subject(timetable, section_key, subject):
    placed = 0
    for day in DAYS:
        for slot in timetable[section_key][day].values():
            if slot is not None and slot["subject"] == subject:
                placed += 1
    return placed


def test_generate_subject_teacher_mapping_covers_every_subject():
    mapping = generate_subject_teacher_mapping(DATA["teachers"], DATA["classes"])
    for section_key in ["VI-A", "VI-B", "VII-A", "VII-B"]:
        assert mapping[section_key]["Math"]["teacher_id"] == "T1"
        assert mapping[section_key]["Science"]["teacher_id"] == "T2"


def test_reuses_same_teacher_across_sections():
    mapping = generate_subject_teacher_mapping(DATA["teachers"], DATA["classes"])
    assert mapping["VI-A"]["Math"]["teacher_id"] == mapping["VI-B"]["Math"]["teacher_id"]


def test_allocate_subject_periods_distributes_across_days():
    timetable = initialize_timetable(DATA["classes"])
    teacher = DATA["teachers"]["teachers"][0]
    from scheduler.workload import initialize_workload

    workload = initialize_workload(DATA["teachers"]["teachers"])
    working_days = DATA["classes"]["classes"][0]["working_days"]

    allocate_subject_periods(timetable, "VI-A", "Math", 3, teacher, working_days, workload)

    used_days = set()
    for day in DAYS:
        for slot in timetable["VI-A"][day].values():
            if slot is not None and slot["subject"] == "Math":
                used_days.add(day)

    assert count_subject(timetable, "VI-A", "Math") == 3
    assert len(used_days) >= 2


def test_full_pipeline_generates_valid_timetable():
    result = generate_timetable(DATA)
    assert result["validation"]["valid"] is True

    timetable = result["timetable"]
    for section_key in ["VI-A", "VI-B", "VII-A", "VII-B"]:
        assert count_subject(timetable, section_key, "Math") == 3
        assert count_subject(timetable, section_key, "Science") == 2


def test_no_teacher_clashes_in_generated_timetable():
    result = generate_timetable(DATA)
    timetable = result["timetable"]

    for teacher in DATA["teachers"]["teachers"]:
        for day in DAYS:
            for period in range(1, 7):
                sections = [
                    section_key
                    for section_key in timetable
                    if timetable[section_key][day][period] is not None
                    and timetable[section_key][day][period]["teacher_id"] == teacher["empid"]
                ]
                assert len(sections) <= 1


def test_mapping_prefers_higher_ranked_class_teacher():
    from scheduler.allocator import assign_teacher_to_subject

    teacher = assign_teacher_to_subject(
        DATA["teachers"]["teachers"], "VII", "Math"
    )
    assert teacher["empid"] == "T1"


def test_save_routine_writes_file(tmp_path):
    result = generate_timetable(DATA)
    output = tmp_path / "routine.json"
    path = save_routine(result["timetable"], output)
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert '"VI-A"' in content

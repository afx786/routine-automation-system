# Timetable Automation and Scheduling System

An automated school timetable generator that builds a weekly class routine from teacher and class configuration data, enforced against a set of hard scheduling constraints and validated before output.

## Project Overview

The system reads two JSON configuration files defining the teaching staff and the structure of every class, then produces a weekly timetable. The scheduling engine:

- maps every subject of every class section to an eligible teacher,
- allocates the required number of weekly periods across the working days,
- respects teacher availability windows and daily workload limits,
- prevents class and teacher conflicts,
- validates the final timetable against all configured rules,
- reports unresolved allocations when the input dataset makes a perfect timetable impossible.

The engine is built as a modular pipeline. Each module has a single responsibility, and the generator orchestrates the full flow from raw data to a validated routine.

## Features

- **Automatic teacher assignment** for every class-section subject pair.
- **Eligibility-aware selection** — a teacher is only considered for subjects and classes explicitly defined in their configuration.
- **Availability-aware scheduling** — teachers are only assigned during their configured `available_periods`.
- **Daily workload enforcement** — a teacher never exceeds `max_periods_per_day`.
- **Subject-teacher locking** — once a teacher is assigned to a subject for a class section, all periods of that subject are taught by that same teacher.
- **Conflict prevention** — teachers cannot teach two sections simultaneously and a section cannot have two subjects in the same period.
- **Class priority** — higher-ranked classes are scheduled before lower-ranked ones.
- **Subject distribution** — a subject's periods are spread across the week instead of being placed on a single day.
- **Least-flexible teacher first** — teachers with fewer options are allocated before teachers with broader availability to reduce future conflicts.
- **Seniority preference** — when multiple teachers can teach a subject, the teacher associated with the highest class rank is preferred.
- **Section consistency** — the same teacher is reused for the same subject across sections of a class whenever possible.
- **Full validation pass** — the generated timetable is checked against every rule and a validation report is returned.

## Scheduling Rules Implemented

| Rule | Description |
| --- | --- |
| 1. Teacher Clash | A teacher cannot teach more than one class section in the same period on the same day. |
| 2. Class Clash | A class section cannot have more than one subject in the same period. |
| 3. Teacher Subject Locking | All periods of a subject for a class section are taught by the same teacher. |
| 4. Teacher Eligibility | A teacher only teaches subjects and classes defined in the teacher configuration. |
| 5. Teacher Availability | A teacher is only assigned during their configured available periods. |
| 6. Teacher Daily Load | A teacher's assignments on a day never exceed `max_periods_per_day`. |
| 7. Weekly Subject Requirement | Every subject receives its configured `periods_per_week`. |
| 8. Class Working Days | Timetable generation respects each class's configured working days. |
| 9. Daily Period Limit | A day never receives more periods than its configured period count. |
| 10. Higher Rank First | Scheduling starts from higher-ranked classes and proceeds to lower-ranked ones. |
| 11. Teacher Seniority Preference | Among eligible teachers, the one with the highest associated class rank is preferred. |
| 12. Least Flexible Teacher First | Teachers with fewer available periods are allocated first. |
| 13. Teacher Subject Consistency | The same teacher is preferred for the same subject across sections of a class. |
| 14. Avoid Empty Slots | Free periods are created only when no valid allocation exists. |
| 15. Validate Before Final Output | The timetable is fully validated and unresolved conflicts are reported. |

## Project Structure

```
project/
│
├── main.py
│
├── data/
│   ├── teacher_list.json
│   ├── class_subjects.json
│   └── generated_routine.json
│
├── scheduler/
│   ├── data_loader.py
│   ├── ranking.py
│   ├── allocator.py
│   ├── generator.py
│   ├── timetable.py
│   ├── workload.py
│   ├── checks.py
│   └── validator.py
│
├── tests/
│   ├── test_allocator.py
│   ├── test_constraints.py
│   ├── test_generator.py
│   └── test_validator.py
│
└── docs/
```

### Module Responsibilities

- **data_loader.py** — loads teacher and class configuration from JSON files.
- **timetable.py** — defines the week layout and creates an empty timetable grid for every class section.
- **ranking.py** — orders classes by rank (highest first) and teachers by flexibility.
- **workload.py** — tracks teacher assignment counts, daily periods, and projected weekly load.
- **allocator.py** — selects the best valid teacher for a subject, considering eligibility, workload, and priority rules.
- **checks.py** — encodes the hard constraint checks used during allocation.
- **validator.py** — performs a full validation pass and produces a conflict report.
- **generator.py** — orchestrates the end-to-end pipeline and saves the generated routine.

## Technology Stack

- **Python 3** — the entire system is written in standard-library Python. No third-party runtime dependencies.
- **JSON** — input configuration and output routine are JSON documents.
- **pytest** — used for the automated test suite.

## How to Run

From the project root:

```
python main.py
```

The script runs the full pipeline and prints the class ranking, teacher ranking, an example mapping, a sample timetable, the validation report, and the path of the saved routine.

To run the test suite:

```
python -m pytest tests
```

## Input JSON Files

### `data/teacher_list.json`

A list of teachers. Each teacher defines:

- `empid` and `teacher_name`
- `max_periods_per_day` — daily teaching limit
- `available_periods` — the period numbers the teacher can work
- `subjects` — the subjects the teacher can teach and, for each subject, the classes they are eligible to teach

Example:

```json
{
  "empid": "EMP003",
  "teacher_name": "Rajesh Kumar",
  "max_periods_per_day": 5,
  "available_periods": [1, 2, 3, 4, 5],
  "subjects": [
    {"subject_name": "English", "classes": ["VI", "VII", "VIII"]}
  ]
}
```

### `data/class_subjects.json`

A list of classes. Each class defines:

- `class_name` and `rank` — rank determines scheduling priority and teacher seniority
- `sections` — e.g. `["A", "B"]`
- `working_days` — the number of periods per day for each day of the week
- `subjects` — the subjects taught and the required `periods_per_week` for each

Example:

```json
{
  "class_name": "VI",
  "rank": 9,
  "sections": ["A", "B"],
  "working_days": {"MON": 6, "TUE": 6, "WED": 6, "THU": 6, "FRI": 6, "SAT": 3},
  "subjects": [
    {"subject_name": "English", "periods_per_week": 5}
  ]
}
```

## Output

The generated routine is saved to `data/generated_routine.json`. The timetable is organized by class section, then by day, then by period:

```json
{
  "VI-A": {
    "MON": {
      "1": {"subject": "Mathematics", "teacher_id": "EMP010", "teacher_name": "Vikas Kumar"},
      "2": {"subject": "Hindi", "teacher_id": "EMP006", "teacher_name": "Meena Kumari"}
    }
  }
}
```

Every slot is either an allocation or `null` when no valid assignment could be made.

## Scheduling Workflow

1. **Load data** — teacher and class configuration is read from JSON.
2. **Rank classes** — classes are ordered by rank, highest first, so senior classes are scheduled first.
3. **Generate subject-teacher mapping** — for every class section and subject, a teacher is selected. Selection filters by eligibility and then prefers the least-flexible teacher, the teacher with the highest associated class rank, and the teacher with the lowest current workload. The same teacher is reused across sections of a class where possible.
4. **Initialize timetable** — an empty grid of days and periods is created for every class section.
5. **Allocate periods** — for every class section and subject, the required weekly periods are placed by searching each working day and each period. A slot is only used when every hard constraint passes.
6. **Validate** — the completed timetable is checked against all rules.
7. **Save routine** — the validated timetable is written to `data/generated_routine.json`.

## Validation

Before returning the final timetable, the system performs a complete validation pass and reports:

- teacher clashes (a teacher in two sections at the same time),
- class clashes (two subjects in a section at the same time),
- availability violations (a slot placed outside a teacher's available periods),
- daily load violations (a teacher over their daily period limit),
- eligibility violations (a teacher assigned an unlisted subject or class),
- subject-teacher lock violations (a subject taught by different teachers),
- missing subject periods (a subject placed fewer times than required),
- daily period limit violations (a day over its configured period count),
- empty slot counts (unallocated periods remaining).

The report marks the timetable as `valid` only when every hard constraint is satisfied and every subject requirement is met.

## Known Limitations

- Period allocation is a greedy, rule-based search. It does not perform backtracking or global optimization.
- When the input dataset does not contain enough teacher capacity to cover all required periods, some subject periods are left unallocated. The timetable remains valid against all hard constraints, and the missing periods are reported as unresolved conflicts by the validator.
- A subject can only be taught by one teacher per class section. If a single teacher is the only eligible teacher for a subject and their weekly capacity is lower than the combined demand, the shortfall cannot be resolved automatically.

## Future Improvements

- Add backtracking or constraint propagation to the allocation engine to reduce unresolved allocations on over-subscribed datasets.
- Generate printable, human-readable timetable views (e.g., per-class and per-teacher weekly sheets).
- Support teacher working-day restrictions in addition to period availability.
- Add a configuration file for scheduling rules so the rules can change without code changes.
- Provide reporting on teacher workload balance and capacity utilization.
- Add an interface to edit teacher and class data and regenerate routines.
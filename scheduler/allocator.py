def get_eligible_teachers(
    teachers,
    class_name,
    subject_name
):
    eligible = []

    for teacher in teachers:

        for subject in teacher["subjects"]:

            if (
                subject["subject_name"] == subject_name
                and
                class_name in subject["classes"]
            ):
                eligible.append(teacher)

    return eligible


def subject_max_rank(teacher, subject_name, rank_map=None):
    best = 0
    for subject in teacher["subjects"]:
        if subject["subject_name"] != subject_name:
            continue
        for class_name in subject["classes"]:
            rank = rank_map.get(class_name, 0) if rank_map else 0
            if rank > best:
                best = rank
    return best


def best_teacher(eligible, subject_name, rank_map=None, workload=None, locked_teacher_id=None):
    if locked_teacher_id:
        for teacher in eligible:
            if teacher["empid"] == locked_teacher_id:
                return teacher

    def score(teacher):
        work = workload[teacher["empid"]]["assignment_count"] if workload else 0
        projected = workload[teacher["empid"]]["projected_weekly"] if workload else 0
        return (
            projected,
            len(teacher["available_periods"]),
            -subject_max_rank(teacher, subject_name, rank_map),
            work
        )

    return min(eligible, key=score)


def assign_teacher_to_subject(
    teachers,
    class_name,
    subject_name,
    rank_map=None,
    workload=None,
    locked_teacher_id=None
):

    eligible = get_eligible_teachers(
        teachers,
        class_name,
        subject_name
    )

    if not eligible:
        return None

    return best_teacher(
        eligible,
        subject_name,
        rank_map,
        workload,
        locked_teacher_id
    )
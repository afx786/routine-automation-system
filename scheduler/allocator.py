from scheduler.ranking import rank_teachers


def get_eligible_teachers(teachers, class_name, subject_name):
    
    eligible = []
    for teacher in teachers:
        for subject in teacher["subjects"]:
            if (
                subject["subject_name"] == subject_name and class_name in subject["classes"]
            ):
                eligible.append(teacher)
                
    return eligible

def assign_teacher_to_subject(teacher, subject_name, class_name):
    eligible = get_eligible_teachers(teacher, subject_name, class_name)
    if not eligible:
        return None
    ranked = rank_teachers(eligible)
    return ranked[0]
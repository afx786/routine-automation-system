from scheduler.ranking import rank_classes
from scheduler.allocator import assign_teacher_to_subject

def generate_subject_teacher_mapping(teachers, classes):
    mapping = {}
    sorted_classes = rank_classes(classes["classes"])
    for cls in sorted_classes:
        class_name = cls["class_name"]
        for section in cls["sections"]:
            section_key = f"{class_name}-{section}"
            mapping[section_key] = {}
            for subject in cls["subjects"]:
                subject_name = subject["subject_name"]
                
                teacher = assign_teacher_to_subject(teachers["teachers"], class_name, subject_name)
                if teacher:
                    mapping[section_key][subject_name] = {
                        "teacher_id" : teacher["empid"], "teacher_name": teacher["teacher_name"]
                    }
                else:
                    mapping[section_key][subject_name] = None
                    
    return mapping

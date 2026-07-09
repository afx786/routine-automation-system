def is_class_free(timetable, class_section, day, period, teacher_id):
    return timetable[class_section][day][period] is None

def is_teacher_free(timetable, teacher_id, day, period):
    for class_section in timetable:
        slot = timetable[class_section][day][period]
        if slot is None:
            continue
        if slot["teacher_id"] == teacher_id:
            return False
    return True
    


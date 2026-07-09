def is_class_free(timetable, class_section, day, period):
    return timetable[class_section][day][period] is None
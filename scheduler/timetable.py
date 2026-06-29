DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT"]

def initialize_timetable(classes):
    timetable={}
    for cls in classes ["classes"]:
        class_name = cls["class_name"]
        for section in cls["sections"]:
            section_key = f"{class_name}-{section}"
            timetable[section_key] = {}
            for day in DAYS:
                timetable[section_key][day] = {}
                for period in range(1, 7):
                    timetable[section_key][day][period] = None
    return timetable
                
def rank_classes(classes):
    
    
    return sorted(
        classes, key=lambda cls: cls["rank"],
        reverse=True
    )

def rank_teachers(teachers):
    '''Sort teachers based on :
    1. Least flexibility first
    2. Lower availability first'''
    
    def flexibility_score(teacher):
        total_options = 0
        
        for subject in teacher["subjects"]:
            total_options += len(subject["classes"])
        return total_options
    
    return sorted(teachers, key=lambda teacher:( flexibility_score(teacher), len(teacher["available_periods"])))

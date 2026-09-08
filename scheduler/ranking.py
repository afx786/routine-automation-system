def rank_classes(classes):
    return sorted(
        classes, key=lambda cls: cls["rank"],
        reverse=True
    )


def class_rank_map(classes):
    return {
        cls["class_name"]: cls["rank"]
        for cls in classes
    }


def rank_teachers(teachers):
    def flexibility_score(teacher):
        total_options = 0
        for subject in teacher["subjects"]:
            total_options += len(subject["classes"])
        return total_options

    return sorted(
        teachers,
        key=lambda teacher: (
            flexibility_score(teacher),
            len(teacher["available_periods"])
        )
    )

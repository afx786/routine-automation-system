import json
from pathlib import Path
DATA_DIR = Path("data")
def load_teachers():
    with open(DATA_DIR / "teacher_list.json", "r") as file:
        return json.load(file)
    
def load_classes():
    with open(DATA_DIR / "class_subjects.json", "r") as file:
        return json.load(file)
    
def load_all():
    return{
        "teachers": load_teachers(),
        "classes": load_classes()
    }
import json


def save_settings(file, settings):
    try:
        with open(file, "w") as f:
            json.dump(settings, f)
        print("saved")
    except Exception as e:
        print("Error saving settings", e)


def load_settings(file):
    try:
        with open(file, "r") as f:
            settings = json.load(f)
        print("loaded")
        return settings
    except Exception as e:
        print("Error loading settings", e)
        return None

def assign_priority(age, pain_level, fever, chest_pain, breathing_difficulty, chronic_disease):
    if chest_pain == "Yes" or breathing_difficulty == "Yes":
        return 1, "Emergency"

    elif pain_level >= 8 or (fever == "Yes" and age >= 60):
        return 2, "Urgent"

    elif fever == "Yes" or chronic_disease == "Yes" or pain_level >= 5:
        return 3, "Normal"

    else:
        return 4, "Routine"
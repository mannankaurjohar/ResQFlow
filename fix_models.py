with open(r"backend\app\models.py", "r", encoding="utf-8") as f:
    text = f.read()

target = 'class SeverityLevel(str, enum.Enum):\n    LOW = "LOW"\n    MODERATE = "MODERATE"'
replacement = 'class SeverityLevel(str, enum.Enum):\n    LOW = "LOW"\n    MEDIUM = "MEDIUM"\n    MODERATE = "MODERATE"'

if target in text:
    text = text.replace(target, replacement, 1)
    with open(r"backend\app\models.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Replaced SeverityLevel successfully")
else:
    print("Target not found")

with open(r"frontend\src\services\api.ts", "r", encoding="utf-8") as f:
    lines = f.readlines()

filtered = [l for l in lines if not l.strip().startswith("import axios")]

with open(r"frontend\src\services\api.ts", "w", encoding="utf-8") as f:
    f.writelines(filtered)

print("Cleaned api.ts imports.")

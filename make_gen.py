import os

with open("generate_backend.py", "w", encoding="utf-8") as f:
    f.write('''# Backend Generator for ResQFlow AI
import os

BASE = os.path.join(os.path.dirname(__file__), "backend", "app")
os.makedirs(BASE, exist_ok=True)
os.makedirs(os.path.join(BASE, "ai"), exist_ok=True)
os.makedirs(os.path.join(BASE, "routers"), exist_ok=True)

print("Starting backend file generation...")
''')

print("generate_backend.py initial stub ready")

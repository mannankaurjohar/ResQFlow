import os

ROUTERS_DIR = os.path.join(os.path.dirname(__file__), "backend", "app", "routers")

with open(os.path.join(ROUTERS_DIR, "__init__.py"), "w", encoding="utf-8") as f:
    f.write("# Routers package\n")

print("routers/__init__.py ready")

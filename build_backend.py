import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "backend", "app")
AI_DIR = os.path.join(APP_DIR, "ai")
ROUTERS_DIR = os.path.join(APP_DIR, "routers")
TESTS_DIR = os.path.join(BASE_DIR, "backend", "tests")

for d in [APP_DIR, AI_DIR, ROUTERS_DIR, TESTS_DIR]:
    os.makedirs(d, exist_ok=True)

print("Directories ready.")

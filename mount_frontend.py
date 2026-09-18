with open(r"backend\app\main.py", "r", encoding="utf-8") as f:
    text = f.read()

# Add static files serving if dist exists
target_root = """@app.get("/")
def root():"""

replacement = """from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/")
def root():
    if os.path.exists(FRONTEND_DIST):
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)"""

assert target_root in text, "target_root not found"
text = text.replace(target_root, replacement, 1)

with open(r"backend\app\main.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated main.py with frontend dist static mount")

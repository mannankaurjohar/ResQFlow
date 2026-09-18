with open(r"backend\app\main.py", "r", encoding="utf-8") as f:
    text = f.read()

target = """@app.get("/")
def root():
    if os.path.exists(FRONTEND_DIST):
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
    return {"""

replacement = """from fastapi import Request

@app.get("/")
def root(request: Request):
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header and os.path.exists(FRONTEND_DIST):
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
    return {"""

assert target in text, "target not found in main.py"
text = text.replace(target, replacement, 1)

with open(r"backend\app\main.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated root endpoint to support both browser HTML and JSON API calls.")

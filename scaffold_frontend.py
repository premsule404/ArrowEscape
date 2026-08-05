import os
import shutil

dirs = [
    "frontend/assets",
    "frontend/css",
    "frontend/js/core",
    "frontend/js/engine",
    "frontend/js/ui",
    "frontend/js/api",
    "frontend/js/utils",
    "frontend/pages",
    "frontend/components"
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

if os.path.exists("frontend/src/styles.css"):
    shutil.move("frontend/src/styles.css", "frontend/css/styles.css")
if os.path.exists("frontend/public/index.html"):
    shutil.move("frontend/public/index.html", "frontend/index.html")
if os.path.exists("frontend/src/app.js"):
    shutil.move("frontend/src/app.js", "frontend/js/main.js")

# Clean up empty old dirs if any
try:
    os.rmdir("frontend/src")
    os.rmdir("frontend/public")
except:
    pass

print("Frontend structure complete.")

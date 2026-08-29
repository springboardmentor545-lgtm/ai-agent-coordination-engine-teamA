import os

history_dir = os.path.expandvars(r'%APPDATA%\Code\User\History')
found_file = None

for root, dirs, files in os.walk(history_dir):
    for f in files:
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                if 'def chat_interaction' in content and 'app.agents.graph' in content:
                    print(f"Found in {path}")
                    found_file = path
                    break
        except Exception:
            pass
    if found_file:
        break

if found_file:
    with open(found_file, 'r', encoding='utf-8') as f:
        with open('backend/app/api/endpoints.py', 'w', encoding='utf-8') as out:
            out.write(f.read())
    print("RESTORED!")
else:
    print("Not found in VS Code history.")

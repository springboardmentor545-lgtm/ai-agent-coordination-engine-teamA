import json
import os
import glob

brain_dir = r'C:\Users\HP\.gemini\antigravity-ide\brain'
transcripts = glob.glob(os.path.join(brain_dir, '**', 'transcript_full.jsonl'), recursive=True)

latest_content = None

for log_path in transcripts:
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            if 'endpoints.py' in line and 'write_to_file' in line:
                try:
                    data = json.loads(line)
                    for call in data.get('tool_calls', []):
                        if call.get('name') == 'default_api:write_to_file':
                            args = call.get('args', {})
                            if 'endpoints.py' in args.get('TargetFile', ''):
                                latest_content = args['CodeContent']
                except Exception as e:
                    pass

if latest_content:
    print("FOUND ENDPOINTS.PY IN HISTORY!")
    with open('backend/app/api/endpoints.py', 'w', encoding='utf-8') as out:
        out.write(latest_content)
    print("WROTE ENDPOINTS.PY")
else:
    print("Could not find endpoints.py in any transcript.")

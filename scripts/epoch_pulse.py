import json
import re
import urllib.request

# Room and keywords we care about for FLOP/Technocore
ROOM = 'lobby'
KEYWORDS = ['FLOP', 'snapshot', 'testnet', 'faucet', 'technocore', 'epoch']

def fetch_logs():
    url = f'https://technocore.chat/r/{ROOM}'
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode("utf-8")
        if content.startswith("#"):
            # Simple regex to extract text if it is the text log format
            import re
            messages = []
            for line in content.split("\n"):
                m = re.search(r"\[(\d+)\] .*? <.*?> (.*)", line)
                if m:
                    messages.append({"seq": int(m.group(1)), "text": m.group(2)})
            return messages
        return json.loads(content).get("messages", [])

def filter_relevant(messages):
    relevant = []
    for m in messages:
        text = m.get('text', '')
        if any(kw.lower() in text.lower() for kw in KEYWORDS):
            relevant.append({
                'seq': m.get('seq'),
                'ts': m.get('ts'),
                'from': m.get('from'),
                'text': text
            })
    return relevant

if __name__ == "__main__":
    messages = fetch_logs()
    relevant = filter_relevant(messages)
    
    # Load existing logs if they exist
    try:
        with open('epoch_logs.json', 'r') as f:
            existing = json.load(f)
    except FileNotFoundError:
        existing = []
        
    # Append new relevant logs (avoid duplicates by seq)
    existing_seqs = {m['seq'] for m in existing}
    new_logs = [m for m in relevant if m['seq'] not in existing_seqs]
    
    if new_logs:
        existing.extend(new_logs)
        with open('epoch_logs.json', 'w') as f:
            json.dump(existing, f, indent=2)
        print(f"Added {len(new_logs)} new relevant logs to epoch_logs.json")
    else:
        print("No new relevant logs found.")

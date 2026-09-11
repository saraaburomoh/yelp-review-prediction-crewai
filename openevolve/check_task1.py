import json, os

ds_dir = r'c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\dummy_dataset'
user_id = 'PZ47ZU2aXZNd9SKm-Ua7JA'
item_id = 'Uc6PdjT_MO5bRPQsUUEy5Q'

# Check user
print('=== USER DATA ===')
found_user = False
with open(os.path.join(ds_dir, 'user.json')) as f:
    for line in f:
        line = line.strip()
        if line and user_id in line:
            u = json.loads(line)
            print(json.dumps(u, indent=2))
            found_user = True
            break
if not found_user:
    print('NOT FOUND in user.json')

print()
print('=== ITEM DATA ===')
found_item = False
with open(os.path.join(ds_dir, 'item.json')) as f:
    for line in f:
        line = line.strip()
        if line and item_id in line:
            i = json.loads(line)
            print(json.dumps(i, indent=2))
            found_item = True
            break
if not found_item:
    print('NOT FOUND in item.json')

print()
print('=== USER REVIEWS ===')
count = 0
with open(os.path.join(ds_dir, 'review.json')) as f:
    for line in f:
        line = line.strip()
        if line and user_id in line:
            r = json.loads(line)
            stars = r.get('stars')
            text = r.get('text', '')[:120]
            print(f"stars={stars} | {text}")
            count += 1
print(f'Total user reviews found: {count}')

print()
print('=== ITEM REVIEWS ===')
count = 0
with open(os.path.join(ds_dir, 'review.json')) as f:
    for line in f:
        line = line.strip()
        if line and item_id in line:
            r = json.loads(line)
            stars = r.get('stars')
            text = r.get('text', '')[:120]
            print(f"stars={stars} | {text}")
            count += 1
print(f'Total item reviews found: {count}')

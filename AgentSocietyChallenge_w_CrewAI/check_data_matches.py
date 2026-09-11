import json
import os

def check_matches():
    data_dir = 'data'
    tasks_dir = 'example/track1/yelp/tasks'
    
    # Load all user IDs we have
    users_in_db = set()
    user_file = os.path.join(data_dir, 'user.json')
    if os.path.exists(user_file):
        with open(user_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    users_in_db.add(json.loads(line)['user_id'])
                except: continue
    
    # Load all item IDs we have
    items_in_db = set()
    item_file = os.path.join(data_dir, 'item.json')
    if os.path.exists(item_file):
        with open(item_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    items_in_db.add(json.loads(line)['item_id'])
                except: continue
                
    # Check tasks
    user_matches = 0
    item_matches = 0
    both_matches = 0
    total_tasks = 0
    if os.path.exists(tasks_dir):
        task_files = [f for f in os.listdir(tasks_dir) if f.endswith('.json')]
        total_tasks = len(task_files)
        for task_file in task_files:
            with open(os.path.join(tasks_dir, task_file), 'r', encoding='utf-8') as f:
                try:
                    task = json.load(f)
                    u_id = task.get('user_id')
                    i_id = task.get('item_id')
                    u_match = u_id in users_in_db
                    i_match = i_id in items_in_db
                    if u_match: user_matches += 1
                    if i_match: item_matches += 1
                    if u_match and i_match: both_matches += 1
                except: continue
                    
    print(f"Total Training Tasks: {total_tasks}")
    print(f"User Match Count: {user_matches}")
    print(f"Item Match Count: {item_matches}")
    print(f"Both Match Count: {both_matches}")

if __name__ == "__main__":
    check_matches()

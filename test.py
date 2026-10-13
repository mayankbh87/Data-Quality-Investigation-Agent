import json,profiler;
print(json.dumps(profiler.profile_csv('data/customers.csv'),indent=1))
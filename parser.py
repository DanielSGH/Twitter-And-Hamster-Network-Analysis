from collections import defaultdict
import re

user_mappings = defaultdict(list)

pattern = re.compile(r'^@([A-Za-z0-9_]{1,15})$')

i = 0

with open("twitter-small.tsv") as f:
  for line in f:
    info = line.split()[2:]

    username = info[0]
    content = info[1:]
  
    for item in content:
      if '@' in item[0] and pattern.match(item):
        addition = item
        user_mappings[username].append(item.replace('@', ''))

with open('twitter-small-out.tsv', 'w') as f:
  f.write("username\ttarget\tweight\n")
  for user in user_mappings:
    for target in set(user_mappings[user]):
      f.write(f"{user}\t{target}\t{user_mappings[user].count(target)}\n")

  #   print(f.readline())
  #   print(f.readline()) 
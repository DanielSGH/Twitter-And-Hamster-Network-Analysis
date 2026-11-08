from collections import defaultdict
import re

user_mappings = defaultdict(list)

pattern = re.compile(r'(?<![A-Za-z0-9_])@([A-Za-z0-9_]{1,15})')

for file in ["twitter-small.tsv", "twitter-larger.tsv"]:
  with open(file, encoding="utf-8") as f:
    for line in f:
      info = line.rstrip("\n").split("\t")
      if len(info) < 3:
        continue

      username = info[1].strip().lower()
      content = info[2]

      for item in pattern.findall(content):
        user_mappings[username].append(item.lower())

  with open(f"out-{file}", "w", encoding="utf-8") as f:
    f.write("source\ttarget\tweight\n")
    for user in user_mappings:
      for target in set(user_mappings[user]):
        f.write(f"{user}\t{target}\t{user_mappings[user].count(target)}\n")
import collections

dictionarySchool = collections.defaultdict(int)

with open("input.txt", "r", encoding="utf8") as f:
    lines = f.readlines()

for line in lines:
    line = line.strip()
    _, _, school_num, _ = line.split()
    school_num = int(school_num)
    dictionarySchool[school_num] += 1

answer = []
max_participants_count = max(dictionarySchool.values())
for key in dictionarySchool.keys():
    if dictionarySchool[key] == max_participants_count:
        answer.append(key)
answer = sorted(answer)
print(" ".join([str(i) for i in answer]))

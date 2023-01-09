import os

def FormetDayTime(datelist):
    day = ""
    for i in range(3):
        if i:
            day += '-'
        day += datelist[i]

    time = ""
    for i in range(3,len(datelist)):
        if i != 3:
            time += ':'
        time += datelist[i]
    return day, time


def SaveData(day, time, num):
    # 保存人数
    if not os.path.exists("dayLogs"):
        os.mkdir("dayLogs")
    with open(os.path.join("dayLogs", day), "a", encoding='utf-8') as f:
        f.write(str(num))
        f.write("\t")
        f.write(time)
        f.write("\n")

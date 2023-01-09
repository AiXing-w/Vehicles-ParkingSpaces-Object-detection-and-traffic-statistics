import random
max_set = 42
year = "2022"
month = "5"
day = "16"

with open("./detect_Logs/countlogs", 'a') as f:
    for i in range(24):
        for j in range(60):
            for k in range(0, 60, 5):
                rdi = random.randint(0, max_set)
                f.write(str(i) + ";" + str(rdi) + ";" + str(max_set-rdi))
                f.write("\n")

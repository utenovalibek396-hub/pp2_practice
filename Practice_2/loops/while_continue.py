i = 0
while i < 5:
    i += 1
    if i == 3:
        continue
    print(i)
# the number of repetitions is unknown
# the cycle becomes endless break: ctrl + c
# If the condition is met, it skips from iteration to the next one.
# Cycle control instructions: break,continue,else
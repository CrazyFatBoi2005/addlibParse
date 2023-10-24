import datetime
time = datetime.datetime.now().time()
print(":".join([str(time.hour), str(time.minute), str(time.second)]))
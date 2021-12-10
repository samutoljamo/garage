import time

FILE_LOCATION = "/home/pi/garage/log.txt"


def to_bool(string):
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    return None


def log(msg):
    string = f'{time.strftime("%d.%m.%y %H:%M:%S", time.localtime())}: {msg}\n'
    print(string)
    with open(FILE_LOCATION, "a") as file:
        file.write(string)

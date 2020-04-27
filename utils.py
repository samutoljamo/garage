import time

def to_bool(string):
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    return None



def log(msg):
	print(f'{time.strftime("%d.%m.%y %H:%M:%S", time.localtime())}: {msg}')



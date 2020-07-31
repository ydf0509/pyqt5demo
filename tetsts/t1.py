import threading

def f():
    print('hello')


threading.Thread(target=f).start()
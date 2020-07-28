import sys


def my_excepthook(exc_type, exc_value, tb):
    msg = ' Traceback (most recent call last):\n'
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        name = tb.tb_frame.f_code.co_name
        lineno = tb.tb_lineno
        msg += '   File "%.500s", line %d, in %.500s\n' % (filename, lineno, name)
        tb = tb.tb_next

    msg += ' %s: %s\n' %(exc_type.__name__, exc_value)
    print(msg)


def divide_zero():
    1 / 0           # raise ZeroDivisionError


def f():
    divide_zero()

if __name__ == '__main__':
    sys.excepthook = my_excepthook
    f()
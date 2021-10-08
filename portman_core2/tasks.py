from portman_core2.celeryapp import app
import time


@app.task
def add(x, y):
    time.sleep(10)
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)

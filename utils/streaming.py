import time

def response_generator(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

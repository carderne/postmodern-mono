from cowsay import say


def greet() -> str:
    msg = say("Hello!")
    return msg

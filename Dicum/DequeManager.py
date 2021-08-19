import yaml


class GreenCard():
    yaml_tag = "!GreenCard"
    def __init__(self):
        self.kind = "green"

    def __repr__(self):
        return f"{self.__class__.__name__}(kind={self.kind})"


class BlackCard():
    yaml_tag = "!BlackCard"
    def __init__(self, hours):
        self.kind = "black"
        self.hours = hours

    def __repr__(self):
        return f"{self.__class__.__name__}(kind={self.kind}, hours={hours})"


class YellowCard():
    yaml_tag = "!YellowCard"
    def __init__(self, number):
        self.kind = "Yellow"
        self.number = number
    
    def __repr__(self):
        return f"{self.__class__.__name__}(kind={self.kind}, number={number})"


class RedCard():
    yaml_tag = "!RedCard"
    def __init__(self, action):
        self.kind = "red"
        self.action = action

    def __repr__(self):
        return f"{self.__class__.__name__}(kind={self.kind}, action={action})"


def dump_deque(filename, deque):
    with open(filename, "w") as file:
        file.write(yaml.dump(deque))

def load_deque(filename):
    with open(filename, "r") as file:
        text = file.read()
        return yaml.load(text, Loader=yaml.Loader)


dump_deque("test.yaml", liste)

restored_liste = load_deque("test.yaml")

for card in restored_liste:
    print(card.kind)
    if card.kind == "black":
        print(card.hours)

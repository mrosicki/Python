class First(object):
    def __init__(self):
        print("first")

class Second(First):
    def __init__(self):
        print("second")

class Third(First):
    def __init__(self):
        super().__init__()
        print("that's it")

class Fourth(Second, Third):
    def init(self):
        super().__init__()
        print("that's it")


print(Fourth.__mro__)

from config import Config



class App:
    def __init__(self):
        self.name = Config.APP_NAME

    def __call__(self):
        print(f"Hello World! {self.name}")
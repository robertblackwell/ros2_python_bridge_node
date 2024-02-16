import datetime

class MyClass:
    def __init__(self, astringvalue: str):
        self.string_value = astringvalue

    def mymethod(self):
        return f"MyClass.mymethod string_value:{self.string_value}  {datetime.datetime.now().isoformat()}"
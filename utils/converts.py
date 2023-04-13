from farsi_tools import standardize_persian_text
class Converters:
    def __init__(self):
        self.make_persian = standardize_persian_text
    
    def standardize(self, text):
        return self.make_persian(text)
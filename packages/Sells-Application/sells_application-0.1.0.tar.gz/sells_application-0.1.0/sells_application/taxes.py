from .exeptions import TaxInvalidError

class Taxes:
    def __init__(self,percentage):
        if not (0<=percentage<+1):
            raise TaxInvalidError ("Taxes rates have to be between 0 and 1, type again")
        
        self.percentage=percentage
        
    def tax_application (self,price):
        return price*self.percentage
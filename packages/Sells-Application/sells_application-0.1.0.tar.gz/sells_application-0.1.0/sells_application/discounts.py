from .exeptions import DiscountInvalidError

class Discounts:
    def __init__(self,percentage):
        if not (0<=percentage<=1):
            raise DiscountInvalidError('Discount pecentage has to be between 0 and 1, type again')
        
        self.percentage=percentage
        
    def discount_application(self,price):
        return price*self.percentage
    
    
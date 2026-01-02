from .discounts import Discounts
from .taxes import Taxes
from .prices import Prices

class Sells_Control:
    def __init__(self,price_base,tax_percentage,discount_percentage):
        self.price_base=price_base
        self.tax=Taxes(tax_percentage)
        self.discount=Discounts(discount_percentage)
        
    def final_price_calculation(self):
        discount_applied=self.discount.discount_application(self.price_base)
        tax_applied=self.tax.tax_application(self.price_base)
        final_price_applied=Prices.final_price(self.price_base,tax_applied,discount_applied)
        return round(final_price_applied,)
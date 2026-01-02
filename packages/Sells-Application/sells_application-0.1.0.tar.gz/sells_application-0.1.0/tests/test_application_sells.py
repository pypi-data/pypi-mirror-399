import unittest
from sells_application.sells_control import Sells_Control
from sells_application.exeptions import TaxInvalidError,DiscountInvalidError

class TestControlSells(unittest.TestCase):
    
    def test_final_price(self):
        gestor=Sells_Control(100.0,0.05,0.10)
        self.assertEqual(gestor.final_price_calculation(),95)
        
    def test_tax_invalid(self):
        with self.assertRaises(TaxInvalidError):
            Sells_Control(100.0,1.5,0.10)
            
    def test_dicount_invalid(self):
        with self.assertRaises(DiscountInvalidError):
            Sells_Control(100.0,0.05,1.50)
            
if __name__=="__main__":
    unittest.main()
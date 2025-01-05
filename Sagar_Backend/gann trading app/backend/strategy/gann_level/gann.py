import configparser
import sys
import os
import math
from datetime import timedelta

def round_down_if_odd(number):
    rounded_down = math.floor(number)
    if rounded_down % 2 != 0:
        return rounded_down
    else:
        return rounded_down - 1
    
def sun_price(square_root_of_prev_day_close, square_of_nine):
    rounded_down = math.floor(square_root_of_prev_day_close)
    if rounded_down % 2 != 0:
        return rounded_down + square_of_nine
    else:
        return rounded_down - 1 + square_of_nine
    
def gann_calculator(prev_day, reference_day,prev_day_close ):
    sun = round(math.sqrt((prev_day - reference_day)/timedelta(days=1)),5)
    square_of_nine = sun - round_down_if_odd(sun)
    square_of_nine_multiplier = square_of_nine*180
    square_root_of_prev_day_close = round(math.sqrt(prev_day_close),5)
    price_at_sun = round(sun_price(square_root_of_prev_day_close, square_of_nine),3)
    price_at_sunpoint = round(price_at_sun**2,2)
    return sun, square_of_nine, square_of_nine_multiplier, square_root_of_prev_day_close, price_at_sun, price_at_sunpoint


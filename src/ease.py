"""Animation easing functions"""


def ease_out_exp(x, exp=2):
    # Note: only works with even exponents currently
    return -((x - 1) ** exp) + 1



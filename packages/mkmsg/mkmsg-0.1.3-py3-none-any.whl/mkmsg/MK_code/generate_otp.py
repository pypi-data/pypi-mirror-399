import random
def Generate_otp(length=6):
    """
    Generate a random OTP of given length.
    Args:
        type (int): Number of digits (default 6)
    """
    return random.randint(10**(length-1), 10**length - 1)

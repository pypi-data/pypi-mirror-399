def greet(name):
    """تابع کمکی خوشامدگویی"""
    return f"سلام {name}!"

def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

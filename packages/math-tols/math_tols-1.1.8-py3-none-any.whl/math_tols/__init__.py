#start libary v2



def add(x,y):
	sum = (x+y)
	return sum
	
def subtract(x,y):
	men = (x-y)
	return men

def multiply(x,y):
	zar = (x*y)
	return zar
	
def divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero")
    tag = x / y
    return tag

	
	
def power(x, y):
    result = 1
    for i in range(y):
        result *= x
    return result
def sqrt(x):
	result = x ** 0.5
	return result
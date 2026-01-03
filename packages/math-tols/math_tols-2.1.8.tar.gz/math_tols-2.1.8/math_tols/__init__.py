#start libary v2



def add(x,y):
	data = (x+y)
	return data
	
def subtract(x,y):
	data = (x-y)
	return data

def multiply(x,y):
	data = (x*y)
	return data
	
def divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero")
    data = x / y
    return data

	
	
def power(x, y):
    result = 1
    for i in range(y):
        result *= x
    return result
def sqrt(x):
	data = x ** 0.5
	return data
	
	def abs(x):
	    if x < 0:
	        return -x
	    return x
	    
def is_even_or_odd(x):
    if x % 2 == 0:
        return f"{x} even "
    else:
        return 'Odd'
        
def remainder(x, y):
    if x % y == 0:
        return 0
    return x % y
    
    
def percent(x):
    data = 1 * x / 100
    return data 
    
def percent_two_num(x, y):
    data = x / y * 100
    return data

def avrage(adads):
    data = adads
    adadd = len(data)
    jam = sum(data)
    result = jam / adadd
    return result
    
    
def factorial(x):
    result = 1
    for i in range(1, x + 1):
        result *= i
    return result

        

        
def add(x,y):
  return x + y

def subract(x,y):
  return x - y

def multiply(x,y):
  return x * y

def divide(x,y):
  try:
    return x/y
  except ZeroDivisionError:
    return "Error: Divison by zero is not allowed."

def mod(x,y):
  try:
    return x % y
  except Exception as e:
    return f"Error: {e}"

def power(x,y):
  return x ** y


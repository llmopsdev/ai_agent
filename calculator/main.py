# main.py
from pkg.calculator import Calculator

calc = Calculator()
expression = "3 + 7 * 2"
result = calc.evaluate(expression)
print(result)
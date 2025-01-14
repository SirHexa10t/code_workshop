#!/usr/bin/python3

"""
Developed a formula to improve performance and you're not sure if you made a calculation error? Just test it with various values here!

Usage:
example 1:
python3 evaluation_aid.py "F(3k)*F(k)F(k+1) + 2(F(3))(F(4))" 5

example 2:
python3 evaluation_aid.py "F(3k) = F(k)*F(2k+1) + F(k-1)*F(2k)   =   F(k)(F(2k+2)-F(2k)) + (F(k+1)-F(k))*F(2k) = F(2k+2)F(k) - 2*F(2k)F(k) + F(2k)F(k+1) = (F(2k+2)-2F(2k))F(k) + F(2k)F(k+1)
    = (F(2k+1)-F(2k))F(k) + F(2k)F(k+1) = (F(k+1)^2 + F(k)^2 - F(2k))F(k) + F(2k)F(k+1) = (F(k+1)^2 + F(k)^2 - (2*F(k+1)F(k) - F(k)^2) )F(k) + (2*F(k+1)F(k) - F(k)^2)F(k+1) =
    = 3*F(k+1)^2*F(k) + 2F(k)^3 - 3*F(k+1)F(k)^2  =  3*F(k+1)F(k)( F(k+1)-F(k) ) + 2F(k)^3 = 3*F(k+1)F(k)F(k-1) + 2F(k)^3 =  3*F(k)*(F(k)^2 + (-1)^k) + 2F(k)^3
    = 5*F(k)^3 + (-1)^k*3*F(k) " 5
"""

import sys
import re
import os
from pathlib import Path
import subprocess
from contextlib import contextmanager
from sympy import sympify


fibo_calc_file = 'fibo_c.bin'

formula = sys.argv[1]
k = sys.argv[2]
bin_file_path = Path(__file__).parent / fibo_calc_file

def exit_msg(msg):
    print(msg)
    exit(1)

if not formula:
    exit_msg(f"you need to provide a string as formula in first arg. Like: 'F(3k)*F(k)F(k+1) + 2(F(3))(F(4))'")
if not k:
    exit_msg(f"you need to specify k for second arg")
if not bin_file_path.is_file():
    exit_msg(f"could not find file '{fibo_calc_file}'. Full path attempted: {bin_file_path}")
    

@contextmanager
def safe_evaluation():
    try:
        yield
    except Exception as e:
        yield f"Error: {e}"
        
def evaluate_expression(expression):
    with safe_evaluation() as safe:
        return str(sympify(expression))
        
def replace_f_with_result(text):
    def replacement_method(match):
        inner_expression = match.group(1)  # Get the content inside the parentheses
        input = evaluate_expression(inner_expression)
        calc_result = subprocess.run(f"{bin_file_path} {input}", shell=True, capture_output=True, text=True, executable='/bin/bash').stdout
        calc_result = re.sub(r"\s+", "", calc_result)  # remove all whitespaces (including newlines) by replacing them with nothing
        calc_result=f"({calc_result})"
        return calc_result

    pattern = r'F\((.*?)\)'  # match 'F(<expression>)'
    return re.sub(pattern, replacement_method, text)

def print_solution(formula_str):
    steps = {}
    steps['original'] = formula_str
    
    updated_formula = formula_str.replace(')k', ')*' + k)  # replace instances of ')k' with ')*k'
    updated_formula = re.sub(r'(\d)k', r'\1*' + k, updated_formula)  # replace instances of '<num>k' with '<num>*k'
    updated_formula = updated_formula.replace('k', k)  # replace all the rest of k instances with an actual number
    
    updated_formula = updated_formula.replace(')(', ')*(')  # replace instances of ')(' with ')*(', needed now in case of something like F((2k)(k^2))
    
    updated_formula = replace_f_with_result(updated_formula)  # calculate fibo values
    steps['after_fibo'] = updated_formula
    
    updated_formula = updated_formula.replace(')(', ')*(')  # replace instances of ')(' with ')*('
    updated_formula = re.sub(r'(\d)\(', r'\1*(', updated_formula)  # replace instances of '<num>(' with '<num>*('
    steps['final_formula'] = updated_formula
    
    updated_formula = evaluate_expression(updated_formula)  # calculate formula
    steps['result'] = updated_formula
    
    print(f"""\
        {steps['original']} =
        {steps['after_fibo']} =
        {steps['final_formula']} =
        {steps['result']}
    """)
    
    return steps['result']


results = [ print_solution(statement) for statement in formula.replace("\n", "").split("=") if not statement.isspace()]

for res in results:
    if res != results[0]:
        print(f"formula equation results don't match!")
        exit(1)

if '=' in formula:
    print(f"your equation is true for {k}")

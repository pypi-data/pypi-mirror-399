from Source import Yvel
import sympy as sp
import numpy as np

#Example variables and function
U, I = sp.symbols("U I")
R = U/I
print(R.free_symbols)
calc = Yvel(R)
print(calc)
print(calc.symbolic())
U_vals = np.array([1,2,3,4,5,6])
I_vals = np.array([6,5,4,3,2,1])
U_err = U_vals*0.001
I_err = I_vals*0.05
#Convert to desirable input format: m x k array-like, where k is your number of variables and m is your number of measurement events.
values = np.column_stack([U_vals, I_vals]) 
sigmas = np.column_stack([U_err, I_err])

sigma_R = calc.numeric(values, sigmas)

print(sigma_R)
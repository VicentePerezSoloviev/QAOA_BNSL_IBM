#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
depolarizing_error
"""

import pandas as pd

from execute import execute_ibm
from qiskit.providers.aer.noise import depolarizing_error, NoiseModel
import numpy as np

n = 3
p_max = 7
alpha = 0.9
index = 0
weights = [-10, -1, -1, -1, -10, -1]
nbshots = 1000
name = 'ibm_exp3_alpha09.csv'
dt = pd.DataFrame(columns=['state', 'prob', 'cost', 'iteration', 'p', 'avr_C'])
dt.to_csv(name, index=True)

for p in range(1, 5):
    for gamma in np.arange(0.01, 0.05, 0.01):
        noise_model = NoiseModel()
        error1 = depolarizing_error(gamma, 1)
        error2 = depolarizing_error(gamma*2, 2)
        noise_model.add_all_qubit_quantum_error(error1, ['rx', 'h', 'rz'])
        noise_model.add_all_qubit_quantum_error(error2, ['cnot', 'cx'])

        df, its, avr_C = execute_ibm(n=n, p=p, nbshots=nbshots, alpha1=17, alpha2=17, cvar_alpha=alpha,
                                     weights=weights, noise=noise_model)

        dt.loc[index] = [df.loc[0, 'state'], df.loc[0, 'prob'], df.loc[0, 'cost'], its, p, avr_C]
        index = index + 1
        dt.to_csv(name, index=True)







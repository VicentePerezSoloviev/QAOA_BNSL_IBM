#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
phase_damping_error
"""

import pandas as pd

from execute import execute_ibm
from qiskit.providers.aer.noise import phase_damping_error, NoiseModel
import numpy as np

n = 3
p_max = 7
alpha = 0.9
index = 0
weights = [-10, -1, -1, -1, -10, -1]
nbshots = 1000
name = 'ibm_exp2_alpha09.csv'
dt = pd.DataFrame(columns=['state', 'prob', 'cost', 'iteration', 'p', 'time', 'avr_C'])
dt.to_csv(name, index=True)

for p in range(1, 5):
    for gamma in np.arange(0.01, 0.1, 0.01):
        noise_model = NoiseModel()
        error = phase_damping_error(gamma)
        noise_model.add_all_qubit_quantum_error(error, ['rx', 'h', 'rz', 'cx', 'cnot'])

        df, its, avr_C = execute_ibm(n=n, p=p, nbshots=nbshots, alpha1=17, alpha2=17, cvar_alpha=alpha,
                                     weights=weights, noise=noise_model)

        dt.loc[index] = [df.loc[0, 'state'], df.loc[0, 'prob'], df.loc[0, 'cost'], its, p, avr_C]
        index = index + 1
        dt.to_csv(name, index=True)







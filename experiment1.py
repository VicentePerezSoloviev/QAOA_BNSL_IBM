#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
amplitude_damping_error
"""

import pandas as pd

from execute import execute_ibm
from qiskit.providers.aer.noise import amplitude_damping_error, NoiseModel
import numpy as np
from scores import Scores

n = 4
scores = Scores()
weights = scores.load_data("cancer.txt")
p_max = 7
alpha = 0.9
index = 0
# weights = [-10, -1, -1, -1, -10, -1]
nbshots = 1000
name = 'ibm_exp1_alpha09_cancer.csv'
dt = pd.DataFrame(columns=['state', 'prob', 'cost', 'iteration', 'p', 'avr_C'])
dt.to_csv(name, index=True)

for p in range(1, 6):
    for gamma in [10**(-4), 10**(-3.5), 10**(-3), 10**(-2.5), 10**(-2), 10**(-1.5), 10**(-1), 10**(-0.5), 1]:
        for aux in range(20):
            noise_model = NoiseModel()
            error = amplitude_damping_error(gamma)
            noise_model.add_all_qubit_quantum_error(error, ['rx', 'h', 'rz'])

            df, its, avr_C = execute_ibm(n=n, p=p, nbshots=nbshots, alpha1=17, alpha2=17, cvar_alpha=alpha,
                                         weights=weights, noise=noise_model)

            dt.loc[index] = [df.loc[0, 'state'], df.loc[0, 'prob'], df.loc[0, 'cost'], its, p, avr_C]
            index = index + 1
            dt.to_csv(name, index=True)







#!/usr/bin/env python
# -*- coding: utf-8 -*-

from execute import execute_ibm
from qiskit.providers.aer.noise import depolarizing_error, NoiseModel

n = 3
p_max = 7
p = 1
alpha = 0.9
index = 0
weights = [-10, -1, -1, -1, -10, -1]
nbshots = 1000

gamma = 0.5
noise_model = NoiseModel()
error1 = depolarizing_error(gamma, 1)
error2 = depolarizing_error(gamma*2, 2)
noise_model.add_all_qubit_quantum_error(error1, ['rx', 'h', 'rz'])
noise_model.add_all_qubit_quantum_error(error2, ['cnot', 'cx'])


df, its, avr_C = execute_ibm(n=n, p=p, nbshots=nbshots, alpha1=17, alpha2=17, cvar_alpha=alpha,
                             weights=weights, noise=noise_model)

print(df)
print(its)
print(avr_C)

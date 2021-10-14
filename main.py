#!/usr/bin/env python
# -*- coding: utf-8 -*-

from execute import execute_ibm
from qiskit.providers.aer.noise import depolarizing_error, NoiseModel
from itertools import combinations


def generate_zero_weight_matrix(n):
    matrix = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i, j] = 0

        array = [k for k in range(n) if k != i]
        for com in combinations(array, 2):
            matrix[i, com[0], com[1]] = 0

    return matrix


n = 3
p = 1
alpha = 0.9
nbshots = 1000

weights = generate_zero_weight_matrix(n)
weights[1, 0] = -10
weights[2, 0] = -10
weights[3, 1, 2] = -10

gamma = 0.5
noise_model = NoiseModel()
error1 = depolarizing_error(gamma, 1)
error2 = depolarizing_error(gamma*2, 2)
noise_model.add_all_qubit_quantum_error(error1, ['rx', 'h', 'rz'])
noise_model.add_all_qubit_quantum_error(error2, ['cnot', 'cx'])

df, its, avr_C = execute_ibm(n=n, p=p, nbshots=nbshots, alpha1=17, alpha2=17, cvar_alpha=alpha,
                             weights=weights, noise=None)

print(df)
print(its)
print(avr_C)

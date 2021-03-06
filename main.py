#!/usr/bin/env python
# -*- coding: utf-8 -*-

from execute import execute_ibm
from qiskit.providers.aer.noise import depolarizing_error, NoiseModel
from itertools import combinations
from scores import Scores


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


p = 3  # number of layers
alpha = 0.3  # Conditional Value at a Risk
nbshots = 1000  # Number of shots in the quantum circuit during runtime

scores = Scores()
weights = scores.load_data("cancer.txt")
n = len(scores.identity)

'''
gamma = 0.5
noise_model = NoiseModel()
error1 = depolarizing_error(gamma, 1)
error2 = depolarizing_error(gamma*2, 2)
noise_model.add_all_qubit_quantum_error(error1, ['rx', 'h', 'rz'])
noise_model.add_all_qubit_quantum_error(error2, ['cnot', 'cx'])
'''

df, its, avr_C = execute_ibm(n=n, p=p, nbshots=nbshots, alpha1=1000, alpha2=1000, cvar_alpha=alpha,
                             weights=weights, noise=None)

print(df)
print(its)
print(avr_C)

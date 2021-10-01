#!/usr/bin/env python
# -*- coding: utf-8 -*-

from execute import execute_ibm
from qiskit.providers.aer.noise import amplitude_damping_error

n = 3
p_max = 7
p = 1
alpha = 0.9
index = 0
weights = [-10, -1, -1, -1, -10, -1]
nbshots = 1000

noise_model = amplitude_damping_error()


df, its, avr_C = execute_ibm(n=n, p=p, nbshots=nbshots, alpha1=17, alpha2=17, cvar_alpha=alpha,
                             weights=weights, noise=None)

print(df)
print(its)
print(avr_C)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scipy.optimize import minimize
from algorithm import random_init_parameters, get_black_box_objective, get_qaoa_circuit, progress
import pandas as pd
from qiskit import Aer, execute


def execute_ibm(n, p, nbshots, alpha1, alpha2, cvar_alpha, weights, noise: None):
    obj = get_black_box_objective(p, n, alpha1, alpha2, weights, nbshots, cvar_alpha, noise=noise)
    init_point = random_init_parameters(p)
    res_sample = minimize(obj, init_point, method='COBYLA', options={'maxiter': 2500, 'disp': False})

    optimal_theta = res_sample['x']
    my_circuit, qaoa = get_qaoa_circuit(p, n, optimal_theta[:p], optimal_theta[p:], alpha1, alpha2, weights)

    # Create a job
    # job = my_circuit.to_job(nbshots=nbshots)
    backend = Aer.get_backend('aer_simulator')

    # Execute
    if noise is not None:
        job = execute(my_circuit, backend, shots=nbshots, noise_model=noise)
    else:
        job = execute(my_circuit, backend, shots=nbshots)

    # Execute
    avr_C = 0
    result = job.result().get_counts()
    dt = pd.DataFrame(columns=['state', 'prob', 'cost'])

    for sample in result:
        cost = qaoa.evaluate_solution(str(sample))
        prob = float(result[sample]/nbshots)
        dt = dt.append({'state': str(sample),
                        'prob': prob,
                        'cost': cost}, ignore_index=True)

        avr_C = avr_C + (prob * cost)

    df = dt.sort_values(['prob'], ascending=False).head(5)
    df = df.reset_index()

    return df, int(res_sample['nfev']), avr_C

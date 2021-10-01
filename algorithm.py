#!/usr/bin/env python
# -*- coding: utf-8 -*-

from QAOA_gen import QAOA
import pandas as pd
import random
import numpy as np
from qiskit import Aer, execute
import matplotlib.pyplot as plt

progress = []


def random_init_parameters(layers):
    random_float_list = []

    for i in range(2*layers):
        x = random.uniform(0, np.pi)
        random_float_list.append(x)

    return random_float_list


def get_qaoa_circuit(p, n, beta, gamma, alpha1, alpha2, weights):
    qaoa = QAOA(n=n, alpha1=alpha1, alpha2=alpha2, weights=weights)

    qaoa.add_superposition_layer()
    qaoa.add_layer(p, beta, gamma)
    qaoa.measure()

    # dt = pd.DataFrame(columns=['state', 'prob', 'cost'])
    # my_circuit = qaoa.my_program.to_circ()  # Export this program into a quantum circuit
    # my_circuit = qaoa.circuit


    # print(my_circuit.parameters)
    '''for i in range(p):
        my_circuit = my_circuit.bind_parameters({"g" + str(i): gamma[i], "b" + str(i): beta[i]})'''
        # qaoa.circuit.bind_parameters({})

    return qaoa.circuit, qaoa


def get_black_box_objective(p, n, alpha1, alpha2, weights, nbshots, alpha, noise=None):
    def f(theta):
        beta = theta[:p]
        gamma = theta[p:]
        global progress

        my_circuit, qaoa = get_qaoa_circuit(p, n, beta, gamma, alpha1, alpha2, weights)

        dt = pd.DataFrame(columns=['state', 'prob', 'cost'])

        # Create a job
        # job = my_circuit.to_job(nbshots=nbshots)
        backend = Aer.get_backend('aer_simulator')

        # Execute
        if noise is not None:
            # qpu_predef = NoisyQProc(hardware_model=noise)
            # result = qpu_predef.submit(job)
            job = execute(my_circuit, backend, shots=nbshots, noise_model=noise)

        else:
            # result = get_default_qpu().submit(job)
            job = execute(my_circuit, backend, shots=nbshots)

        result = job.result().get_counts()

        avr_c = 0
        for sample in result:
            cost = qaoa.evaluate_solution(str(sample))
            dt = dt.append({'state': str(sample),
                            'prob': float(result[sample]/nbshots),
                            'cost': cost}, ignore_index=True)

            # avr_c = avr_c + (sample.probability * cost)

        # Conditional Value at Risk (CVaR)
        aux = int(len(dt) * alpha)
        dt = dt.sort_values(by=['cost'], ascending=True).head(aux)
        # dt = dt.nlargest(aux, 'cost')
        dt = dt.reset_index()
        sum_parc = dt['prob'].sum()

        for i in range(len(dt)):
            avr_c = avr_c + (float(dt.loc[i, 'prob'])*float(dt.loc[i, 'cost'])/sum_parc)

        progress.append(avr_c)
        return avr_c  # negative when we want to maximize

    return f

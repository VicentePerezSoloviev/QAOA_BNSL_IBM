#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
We use n(n-1) qubits for the adj matrix and n(n-1)/2 qubits for the transition matrix
"""

from itertools import combinations
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Parameter


def state_2_str(state):
    return str(state)[1:len(str(state)) - 1]


def index_adj_adder(n, i, j):
    assert i != j, "Diagonal adjacency indexes must not be taken into account"
    if j > i:
        return (i * n) + j - (i + 1)
    else:
        return (i * n) + j - i


def index_r_adder(n, i, j):
    assert i < j, "Diagonal r indexes must not be taken into account"
    aux = n*(n-1)
    return aux + (i * n) + j - int(((i+2)*(i+1))/2)


class QAOA:
    layers = 0

    def __init__(self, n, alpha1, alpha2, weights):
        if len(weights) != n * (n-1):
            raise Exception('Length of weights matrix is different than expected')

        self.n = n
        self.alpha1 = alpha1
        self.alpha2 = alpha2

        self.q_adj = n * (n - 1)  # number of qubits for the adj matrix
        self.q_r = (n * (n - 1)) / 2  # number of qubits for the transition matrix

        self.weights = weights

        # Create quantum circuit
        # self.my_program = Program()
        nqubits = int(self.q_adj + self.q_r)
        self.qreg = QuantumRegister(nqubits)
        self.creg = ClassicalRegister(nqubits)
        self.circuit = QuantumCircuit(self.qreg, self.creg)
        # self.qubits = self.my_program.qalloc(int(self.q_adj + self.q_r))

        self.adders = []
        self.gen_adders()

    def gen_adders(self):
        # Transcription of the general formulas of hamiltonian to general indexes of qubits
        
        for i in range(self.n):
            for j in range(i + 1, self.n):
                for k in range(j + 1, self.n):
                    self.adders.append([self.alpha1, index_r_adder(self.n, i, k)])
                    self.adders.append([self.alpha1, index_r_adder(self.n, i, j), index_r_adder(self.n, j, k)])
                    self.adders.append([-self.alpha1, index_r_adder(self.n, i, j), index_r_adder(self.n, i, k)])
                    self.adders.append([-self.alpha1, index_r_adder(self.n, j, k), index_r_adder(self.n, i, k)])

        for i in range(self.n):
            for j in range(i + 1, self.n):
                self.adders.append([self.alpha2, index_adj_adder(self.n, j, i), index_r_adder(self.n, i, j)])
                self.adders.append([self.alpha2, index_adj_adder(self.n, i, j)])
                self.adders.append([-self.alpha2, index_adj_adder(self.n, i, j), index_r_adder(self.n, i, j)])

    def evaluate_solution(self, string):
        to_bin = []
        for i in range(len(string)):
            to_bin.append(int(string[i]))

        cost = 0
        for i in range(self.q_adj):
            cost = cost + to_bin[i] * self.weights[i]

        for i in self.adders:
            if len(i) == 2:
                cost = cost + i[0] * to_bin[i[1]]
            if len(i) == 3:
                cost = cost + i[0] * (to_bin[i[1]] * to_bin[i[2]])

        return cost

    def add_superposition_layer(self):
        # Superposition
        for i in range(len(self.qreg)):
            # if not i in self.diagonal:
            # self.my_program.apply(H, self.qubits[i])
            self.circuit.h(self.qreg[i])

    def spin_mult(self, spins, gamma):
        if len(spins) == 0 or len(spins) > 4:
            raise Exception('number of spins does not match the function requirements')

        if not isinstance(spins, list):
            raise Exception('A list is required as argument "spins"')

        for i in range(len(spins) - 1):
            # self.my_program.apply(CNOT, spins[i], spins[len(spins) - 1])
            self.circuit.cnot(spins[i], spins[len(spins) - 1])

        # self.my_program.apply(RZ(gamma), spins[len(spins) - 1])
        self.circuit.rz(gamma, spins[len(spins) - 1])

        for i in range(len(spins) - 2, -1, -1):
            # self.my_program.apply(CNOT, spins[i], spins[len(spins) - 1])
            self.circuit.cnot(spins[i], spins[len(spins) - 1])

    def adj_mult(self, adjs, gamma, coef):
        if not isinstance(adjs, list):
            raise Exception('A list is required as argument "adjs"')

        if len(adjs) == 0 or len(adjs) > 4:
            raise Exception('number of adj indexes does not match the function requirements')

        angle = coef * (gamma * 2) / (2 ** (len(adjs)))

        for adj in adjs:
            # self.my_program.apply(RZ(-angle), self.qubits[adj])  # minus sign as xi -> (1-zi)/2
            self.circuit.rz(-angle, self.qreg[adj])

        for tam in range(2, len(adjs) + 1):
            for comb in combinations(adjs, tam):
                # self.spin_mult([self.qubits[i] for i in list(comb)], angle)
                self.spin_mult([self.qreg[i] for i in list(comb)], angle)

    def add_layer(self, nlayers, beta, gamma):
        for lay in range(nlayers):
            # gamma = self.my_program.new_var(float, "g" + str(lay))
            # beta = self.my_program.new_var(float, "b" + str(lay))
            # gamma = Parameter("g" + str(lay))
            # beta = Parameter("b" + str(lay))

            # Phase Operator
            for i in range(self.q_adj):
                # if not i in self.diagonal:
                # self.my_program.apply(RZ(gamma * -self.weights[i]), self.qubits[i])
                self.circuit.rz(gamma[lay] * -self.weights[i], self.qreg[i])

            # for i in range(self.q_adj, int(self.q_adj + self.q_r)):
                # self.my_program.apply(RZ(gamma), self.qubits[i])

            for i in self.adders:
                self.adj_mult(i[1:], gamma[lay], i[0])

            # Mixing Operator
            for i in range(len(self.qreg)):
                # if not i in self.diagonal:
                # self.my_program.apply(RX(2 * beta), self.qubits[i])
                self.circuit.rx(2*beta[lay], self.qreg[i])

    def measure(self):
        self.circuit.measure(range(len(self.qreg)), range(len(self.qreg)-1, -1, -1))

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
We use n(n-1) qubits for the adj matrix and n(n-1)/2 qubits for the transition matrix
"""

from itertools import combinations
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from itertools import permutations

m = 2


def mapping_mat_vec(n, row, col):
    index = 0
    for i in range(n):
        for j in range(n):
            if i != j:
                if i == row and j == col:
                    return index
                else:
                    index = index + 1


def mapping_vec_mat(n, index):
    index_new = 0
    for i in range(n):
        for j in range(n):
            if i != j:
                if index == index_new:
                    return i, j
                else:
                    index_new = index_new + 1


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

        # weights is a matrix o nxn. In indexes ii it is weight(node|i) and ij is weight(node|i,j). Sym matrix
        self.weights = weights

        # Create quantum circuit
        nqubits = int(self.q_adj + self.q_r)
        self.qreg = QuantumRegister(nqubits)
        self.creg = ClassicalRegister(nqubits)
        self.circuit = QuantumCircuit(self.qreg, self.creg)

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
        # multiplication of each isolated and weight(node|1parent)
        for i in range(self.q_adj):
            cost = cost + to_bin[i] * self.weights[i][i]

        # multiplication of combination of 2-nodes and weight(node|2parents)
        for i in range(self.n):
            array = to_bin[i * (self.n - 1): i * (self.n - 1) + (self.n - 1)]
            sum_row = sum(array)
            if sum_row > m:
                # cases with more than m parents
                cost = cost + 99999999
            else:
                # cases of 0, 1 or 2 parents
                indexes = [i * (self.n - 1) + j for j, x in enumerate(array) if x == 1]
                if len(indexes) == 1:
                    cost = cost + self.weights[indexes[0]][indexes[0]]
                elif len(indexes) == 2:
                    cost = cost + self.weights[indexes[0]][indexes[1]]
                else:
                    pass

        # restrictions
        for i in self.adders:
            if len(i) == 2:
                cost = cost + i[0] * to_bin[i[1]]
            if len(i) == 3:
                cost = cost + i[0] * (to_bin[i[1]] * to_bin[i[2]])

        return cost

    def add_superposition_layer(self):
        # Superposition
        for i in range(len(self.qreg)):
            self.circuit.h(self.qreg[i])

    def spin_mult(self, spins, gamma):
        if len(spins) == 0 or len(spins) > 4:
            raise Exception('number of spins does not match the function requirements')

        if not isinstance(spins, list):
            raise Exception('A list is required as argument "spins"')

        for i in range(len(spins) - 1):
            self.circuit.cnot(spins[i], spins[len(spins) - 1])

        self.circuit.rz(gamma, spins[len(spins) - 1])

        for i in range(len(spins) - 2, -1, -1):
            self.circuit.cnot(spins[i], spins[len(spins) - 1])

    def adj_mult(self, adjs, gamma, coef):
        if not isinstance(adjs, list):
            raise Exception('A list is required as argument "adjs"')

        if len(adjs) == 0 or len(adjs) > 4:
            raise Exception('number of adj indexes does not match the function requirements')

        angle = coef * (gamma * 2) / (2 ** (len(adjs)))

        for adj in adjs:
            self.circuit.rz(-angle, self.qreg[adj])

        for tam in range(2, len(adjs) + 1):
            for comb in combinations(adjs, tam):
                self.spin_mult([self.qreg[i] for i in list(comb)], angle)

    def add_layer(self, nlayers, beta, gamma):
        for lay in range(nlayers):
            # Phase Operator
            # multiplication of each isolated and weight(node|1parent)
            for i in range(self.q_adj):
                self.circuit.rz(gamma[lay] * -self.weights[i][i], self.qreg[i])

            # multiplication of combination of 2-nodes and weight(node|2parents) in same adj row
            '''perm = list(permutations(list(range(self.q_adj)), m))

            for i in perm:
                self.adj_mult([int(i[0]), int(i[1])], gamma[lay], 1)  # coef = 1 -> not in one of the restrictions'''

            for i in range(self.n):
                perm = list(permutations(list(range(i*(self.n - 1), i*(self.n - 1) + (self.n - 1))), m))
                for per in perm:
                    self.adj_mult([int(per[0]), int(per[1])], gamma[lay], 1)  # coef = 1 -> not in the restrictions

            # multiplication of each of the couple restrictions
            for i in self.adders:
                self.adj_mult(i[1:], gamma[lay], i[0])

            # Mixing Operator
            for i in range(len(self.qreg)):
                self.circuit.rx(2*beta[lay], self.qreg[i])

    def measure(self):
        self.circuit.measure(range(len(self.qreg)), range(len(self.qreg)-1, -1, -1))

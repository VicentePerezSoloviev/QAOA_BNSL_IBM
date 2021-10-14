#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
We use n(n-1) qubits for the adj matrix and n(n-1)/2 qubits for the transition matrix
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from itertools import combinations

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


class QAOA:
    layers = 0

    def __init__(self, n, alpha1, alpha2, weights):
        assert isinstance(weights, dict), 'Length of weights matrix is different than expected'

        self.n = n
        self.alpha1 = alpha1
        self.alpha2 = alpha2

        self.q_adj = n * (n - 1)  # number of qubits for the adj matrix
        self.q_r = (n * (n - 1)) / 2  # number of qubits for the transition matrix

        # weights is a matrix of elements whose keys are tuples of first element the target and following the parents
        self.weights = weights

        # Create quantum circuit
        nqubits = int(self.q_adj + self.q_r)
        self.qreg = QuantumRegister(nqubits)
        self.creg = ClassicalRegister(nqubits)
        self.circuit = QuantumCircuit(self.qreg, self.creg)

        self.adders = []
        self.gen_adders()

    def index_adj_adder(self, i, j):
        assert i != j, "Diagonal adjacency indexes must not be taken into account"
        if j > i:
            return (i * self.n) + j - (i + 1)
        else:
            return (i * self.n) + j - i

    def index_r_adder(self, i, j):
        assert i < j, "Diagonal r indexes must not be taken into account"
        aux = self.n * (self.n - 1)
        return aux + (i * self.n) + j - int(((i + 2) * (i + 1)) / 2)

    def gen_adders(self):
        # Transcription of the general formulas of hamiltonian to general indexes of qubits
        
        for i in range(self.n):
            for j in range(i + 1, self.n):
                for k in range(j + 1, self.n):
                    self.adders.append([self.alpha1, self.index_r_adder(i, k)])
                    self.adders.append([self.alpha1, self.index_r_adder(i, j), self.index_r_adder(j, k)])
                    self.adders.append([-self.alpha1, self.index_r_adder(i, j), self.index_r_adder(i, k)])
                    self.adders.append([-self.alpha1, self.index_r_adder(j, k), self.index_r_adder(i, k)])

        for i in range(self.n):
            for j in range(i + 1, self.n):
                self.adders.append([self.alpha2, self.index_adj_adder(j, i), self.index_r_adder(i, j)])
                self.adders.append([self.alpha2, self.index_adj_adder(i, j)])
                self.adders.append([-self.alpha2, self.index_adj_adder(i, j), self.index_r_adder(i, j)])

    def evaluate_solution(self, string):
        to_bin = []
        for i in range(len(string)):
            to_bin.append(int(string[i]))

        cost = 0
        # multiplication of each isolated and weight(node|1parent)
        '''for i in range(self.q_adj):
            cost = cost + to_bin[i] * self.weights[i][i]'''

        # multiplication of combination of 2-nodes and weight(node|2parents)
        for i in range(self.n):
            # array = to_bin[i * (self.n - 1): i * (self.n - 1) + (self.n - 1)]  # separate each row of adj matrix
            array = [[to_bin[mapping_mat_vec(self.n, k, i)], mapping_mat_vec(self.n, k, i)]
                     for k in range(self.n) if k != i]  # separate each col adj m
            sum_col = sum([k[0] for k in array])
            if sum_col > m:
                # cases with more than m parents
                cost = cost + 99999999  # penalize
            else:
                # cases of 0, 1 or 2 parents
                # find index of each 1
                # indexes = [j * (self.n-1) for j, x in enumerate(array) if x == 1]  # index general array(no diagonal)
                indexes = [k[1] for k in array if k[0] == 1]  # index general array(no diagonal)
                if len(indexes) == 1:
                    # weight (i | index)
                    row, col = mapping_vec_mat(self.n, indexes[0])
                    cost = cost + self.weights[i, row]
                elif len(indexes) == 2:
                    # weight (i | index, index)
                    row1, col1 = mapping_vec_mat(self.n, indexes[0])
                    row2, col2 = mapping_vec_mat(self.n, indexes[1])

                    cost = cost + self.weights[i, row1, row2]
                else:
                    # 0
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
            for i in range(self.n):
                for j in range(self.n):
                    if i != j:
                        # in qubit i, j is the weight of j->i
                        self.circuit.rz(gamma[lay] * -self.weights[i, j], self.qreg[self.index_adj_adder(j, i)])

            # multiplication of combination of 2-nodes and weight(node|2parents) in same adj col
            for i in range(self.n):
                array = [k for k in range(self.n) if k != i]
                perm = combinations(array, m)
                for per in perm:
                    # i | perm, perm
                    self.adj_mult([self.index_adj_adder(per[0], i), self.index_adj_adder(per[1], i)],
                                  gamma[lay], self.weights[i, per[0], per[1]])  # coef = 1 -> not in the restrictions

            # multiplication of each of the couple restrictions
            for i in self.adders:
                self.adj_mult(i[1:], gamma[lay], i[0])

            # Mixing Operator
            for i in range(len(self.qreg)):
                self.circuit.rx(2*beta[lay], self.qreg[i])

    def measure(self):
        self.circuit.measure(range(len(self.qreg)), range(len(self.qreg)-1, -1, -1))

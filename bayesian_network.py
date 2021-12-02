#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from pyvis.network import Network
import pandas as pd
from scores import Scores


class BN:
    """
    Function to manage BN structures
    """

    def __init__(self, adj, identity):
        """
        Constructor.
        :param adj: vector with values to be transformed to adj matrix. Size of n*(n-1)
        :param identity: dictionary with string as keys and identifiers as values.
        """

        self.mat = adj
        self.identity = identity
        self.n = len(identity)

        size = self.n*(self.n-1)
        adj_mod = adj[:size]
        self.adj = np.zeros((self.n, self.n))

        for i in range(len(adj_mod)):
            row, col = self.mapping_vec_mat(i)
            self.adj[row, col] = adj_mod[i]

    def mapping_vec_mat(self, index):
        """
        Returns de adj matrix row and col, the index in the vector matches with,
        :param index: index in vector.
        :return: tuple with row and col.
        """

        index_new = 0
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    if index == index_new:
                        return i, j
                    else:
                        index_new = index_new + 1

        raise Exception('Not expected behaviour')

    def print_structure(self, name='result'):
        """
        Plots the structure of the adjacency matrix.
        :param name: string with the name of the structure. Optional parameter.
        :return: opens browser with plotted structure.
        """

        net = Network('500px', '500px', directed=True)
        nodes = list(self.identity.keys())
        net.add_nodes(nodes)

        for n in net.nodes:
            n.update({'physics': False})

        for i in range(len(self.adj)):
            for j in range(len(self.adj)):
                if self.adj[i, j] == 1:
                    net.add_edge(nodes[i], nodes[j])

        net.show_buttons()
        net.show(name + '.html')

    def compare_structures(self, structure, identity):
        """
        Function to compare the number common edges over the total.
        :param structure: Ideal structure to be compared with. Adj matrix.
        :param identity: identity dictionary to identify the indexes of adj matrix.
        :return: percentage of edges found in common.
        """

        assert self.identity == identity, 'Both identity matrices should be equal to be compared.'

        total_edges = sum(sum(structure))
        edges_common = 0

        for i in range(len(self.adj)):
            for j in range(len(self.adj)):
                if structure[i, j] == 1 and self.adj[i, j] == 1:
                    edges_common = edges_common + 1

        return edges_common/total_edges

    def export_edges(self):
        dt = pd.DataFrame(columns=['from', 'to'])
        index = 0
        nodes = list(self.identity.keys())

        for i in range(len(self.adj)):
            for j in range(len(self.adj)):
                if self.adj[i, j] == 1:
                    dt.loc[index] = [nodes[i], nodes[j]]
                    index = index + 1

        return dt


def load_asia(identity):
    # https://www.bnlearn.com/bnrepository/discrete-small.html#asia
    # identity = {'asia': 0, 'bronc': 1, 'dysp': 2, 'either': 3, 'lung': 4, 'smoke': 5, 'tub': 6, 'xray': 7}
    adj = np.zeros((len(identity), len(identity)))
    edges = [['asia', 'tub'], ['smoke', 'lung'], ['smoke', 'bronc'], ['tub', 'either'], ['lung', 'either'],
             ['bronc', 'dysp'], ['either', 'xray'], ['either', 'dysp']]

    for i in edges:
        from_ = identity[i[0]]
        to_ = identity[i[1]]

        adj[from_, to_] = 1

    return adj, identity


def load_cancer(identity):
    # https://www.bnlearn.com/bnrepository/discrete-small.html#cancer
    # identity = {'Pollution': 0, 'Cancer': 1, 'Dyspnoea': 2, 'Smoker': 3, 'Xray': 4}
    adj = np.zeros((len(identity), len(identity)))
    edges = [['Pollution', 'Cancer'], ['Smoker', 'Cancer'], ['Cancer', 'Xray'], ['Cancer', 'Dyspnoea']]

    for i in edges:
        from_ = identity[i[0]]
        to_ = identity[i[1]]

        adj[from_, to_] = 1

    return adj, identity


def load_child(identity):
    # https://www.bnlearn.com/bnrepository/discrete-medium.html#child
    dt = pd.read_csv('data/arcs_child.csv')
    adj = np.zeros((20, 20))

    for i in range(len(dt)):
        aux = list(dt.loc[i])
        from_ = identity[aux[1]]
        to_ = identity[aux[2]]

        adj[from_, to_] = 1

    return adj


def load_random_bn(filename, identity, size):
    # random sample of DAG and distribution of each variable
    dt = pd.read_csv(filename)
    adj = np.zeros((size, size))

    for i in range(len(dt)):
        aux = list(dt.loc[i])
        from_ = identity[aux[1]]
        to_ = identity[aux[2]]

        adj[from_, to_] = 1

    return adj


def load_adj(dt, identity):
    # dt = pd.read_csv(file)
    adj = np.zeros((len(identity), len(identity)))
    for i in range(len(dt)):
        aux = list(dt.loc[i])
        from_ = identity[aux[1]]
        to_ = identity[aux[2]]

        adj[from_, to_] = 1
    return adj


def load_result_experiments_alg(alg, size, prob):
    """
    Load adjacency matrix of the experiments results
    :param alg: String. Name of algorithm
    :param size: Integer. Size of dataset
    :param prob: String. Name of problem
    :return: Adjacency matrix
    """

    dt = pd.read_csv('experiment1/exp_' + str(alg) + '/1_arcs_' + alg + '_' + prob + '_' + str(size) + '.csv')
    scores = Scores(); scores.load_data("data/" + prob + "_" + str(size) + ".txt")
    identity = scores.identity
    adj = load_adj(dt, identity)

    return adj

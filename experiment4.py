from execute import execute_ibm
import pandas as pd
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


n = 4
p = 1
alpha = 0.9
weights = generate_zero_weight_matrix(n)
weights[1, 0] = -10
weights[2, 0] = -10
weights[3, 1, 2] = -10
nbshots = 1000
index = 0

name = 'ibm_exp4_alpha09.csv'
dt = pd.DataFrame(columns=['state', 'prob', 'cost', 'iteration', 'p', 'avr_C'])
dt.to_csv(name, index=True)

for p in range(1, 5):
    df, its, avr_C = execute_ibm(n=n, p=p, nbshots=nbshots, alpha1=17, alpha2=17, cvar_alpha=alpha,
                                 weights=weights, noise=None)

    dt.loc[index] = [df.loc[0, 'state'], df.loc[0, 'prob'], df.loc[0, 'cost'], its, p, avr_C]
    index = index + 1
    dt.to_csv(name, index=True)

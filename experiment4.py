from execute import execute_ibm
import pandas as pd

n = 4
p = 1
alpha = 0.9
weights = [[-10, -1, -1, -1, -10, -1, -4, -5, -10, -1, -4, -5]]*12
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
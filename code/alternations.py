import numpy as np
from sys import argv
import json

def column_permutation(pattern, i,j):
    temp = pattern[i]
    pattern[i] = pattern[j]
    pattern[j] = temp

def row_permutation(pattern, i,j):
    for k in range(len(pattern)):
        temp = pattern[k][i]
        pattern[k][i] = pattern[k][j]
        pattern[k][j] = temp

def generate_pattern(N, step, permute_columns=False, permute_rows=False):
    pattern = []

    ini_tup=[j for j in range(step)]
    tup=ini_tup
    i=0
    while ((tup != ini_tup) or i==0):
        pattern.append(['1' if j in tup else '0' for j in range(N)])
        i += step
        tup = [(i+j)%N for j in range(step)]
    #print(pattern)

    pat_dict = {}
    for n in range(len(pattern)):
        for i in range(N):
            pat_dict[i] = pat_dict.get(i, []) + [pattern[n][i]]
    #print(pat_dict)

    if permute_columns:
        num_col_permut = np.random.randint(0, N)
        for i in range(num_col_permut):
            a = np.random.randint(0, N)
            b = np.random.randint(0, N)
            column_permutation(pat_dict, a, b)
    if permute_rows:
        num_row_permut = np.random.randint(0, len(pattern))
        for i in range(num_row_permut):
            a = np.random.randint(0, len(pattern))
            b = np.random.randint(0, len(pattern))
            row_permutation(pat_dict, a, b)

    return pat_dict


if __name__ == '__main__':
    N=int(argv[1]) if len(argv) > 1 else 0
    step=int(argv[2]) if len(argv) > 2 else 0
    Npatterns=int(argv[3]) if len(argv) > 3 else 1
    seed = int(argv[4]) if len(argv) > 4 else 0

    np.random.seed(seed)

    patterns = []
    for n in range(Npatterns):
        pat_dict = generate_pattern(N, step, permute_columns=True, permute_rows=True)
        patterns.append(pat_dict)

    #print(pat_dict)
    with open("patterns.json", "w") as f:
        json.dump(patterns, f)
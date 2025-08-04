import json
import numpy as np
from sys import argv



def distribution(freq):
    dist = {}
    for k, v in freq.items():
        dist[k] = v / sum(freq.values())
    return dist

def entropy(freq):
    dist = distribution(freq)
    return -np.sum([p * np.log2(p) for p in dist.values() if p > 0])


if __name__ == "__main__":
    # No. of agents
    N = int(argv[1]) if len(argv) > 1 else 0
    # No. of available spots
    s = int(argv[2]) if len(argv) > 2 else 0

    with open(f'graph_data_N{N:d}s{s:d}.json', 'r') as f:
        struct = json.load(f)
    #print(json.dumps(struct, indent = 2))

    for Npat in range(len(struct)):
        #Average input information per node
        av_info = 0
        for node in struct[Npat]:
            ne = struct[Npat][node]['neigh']
            av_info += len(ne)
        av_info /= N
        print(f'Average input information per node: {av_info:.2f}')

        #Average input entropy per node
        av_entropy = 0
        for node in struct[Npat]:
            av_entropy += entropy(struct[Npat][node]['input freq'])
        av_entropy /= N
        print(f'Average entropy of inputs per node: {av_entropy:.2f}')

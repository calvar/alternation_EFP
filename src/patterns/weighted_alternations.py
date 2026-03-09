
class Counter:
    def __init__(self, procs, num_cpus=1):
        self.procs = sorted(procs, key=lambda x: x['weight'], reverse=True)
        self.wcount = {p['id']:p['weight'] for p in procs}
        self.wcount = dict(sorted(self.wcount.items(), key=lambda item: item[1], reverse=True))
        self.maxc = sum([p['weight'] for p in procs])
        self.counter = 0

    def reset(self):
        for k in self.wcount.keys():
            self.wcount[k] = self.procs[k]['weight']
    
    def get_proc(self):
        p = self.procs[self.counter]
        count = 0
        while self.wcount[p['id']] == 0:
            self.counter = (self.counter+1) % len(self.procs)
            p = self.procs[self.counter]
            count += 1
            if count == self.maxc:
                self.reset()
                print("Resetting counters")
                break
        self.wcount[p['id']] -= 1
        self.counter = (self.counter+1) % len(self.procs)
        return p
    
    def get_next_batch(self):
        batch = []
        for _ in range(num_cpus):
            batch.append(self.get_proc())
        return batch

    def __str__(self):
        return f"wcount={self.wcount}"

   
    


if __name__ == "__main__":
    num_cpus = 3
    # procs = [
    #     {'id': 0, 'weight': 4},
    #     {'id': 1, 'weight': 4},
    #     {'id': 2, 'weight': 3},
    #     {'id': 3, 'weight': 3},
    #     {'id': 4, 'weight': 3},
    #     {'id': 5, 'weight': 3},
    #     {'id': 6, 'weight': 2},
    #     {'id': 7, 'weight': 2},
    #     {'id': 8, 'weight': 1},
    #     {'id': 9, 'weight': 1},
    #     {'id': 10, 'weight': 1}
    # ]
    procs = [
        {'id': 0, 'weight': 4},
        {'id': 1, 'weight': 1},
        {'id': 2, 'weight': 3},
        {'id': 3, 'weight': 1},
        {'id': 4, 'weight': 2},]
    c = Counter(procs, num_cpus)
    print(c)

    rows = []
    ini = c.get_next_batch()
    ids = [proc['id'] for proc in ini]
    print(ids, end=' ')
    print(''.join('1' if (i in ids) else '0' for i in range(len(procs))))
    rows.append(''.join('1' if (i in ids) else '0' for i in range(len(procs))))
    #while True:
    for _ in range(30):
        nxt = c.get_next_batch()
        #if nxt == ini:
        #    break
        ids = [proc['id'] for proc in nxt]
        print(ids, end=' ')
        print(''.join('1' if (i in ids) else '0' for i in range(len(procs))))
        rows.append(''.join('1' if (i in ids) else '0' for i in range(len(procs))))
    
    #print(rows)
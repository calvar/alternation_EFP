
class Counter:
    def __init__(self, procs, num_cpus=1):
        self.wdict = {}
        for p in procs:
            self.wdict[p['weight']] = self.wdict.get(p['weight'], []) + [p['id']]
        self.wdict = dict(sorted(self.wdict.items()))
        self.wcount = len(self.wdict)-1
        self.currw = list(self.wdict.keys())[self.wcount]
        self.counters = {k:0 for k in self.wdict.keys()}
        self.jump = min(self.currw,len(self.wdict[self.currw]))


    def get_proc(self):
        return self.wdict[self.currw][self.counters[self.currw]]
    
    def next(self):
        next_procs = []
        for _ in range(num_cpus):
            next_procs.append(self.get_proc())
            self.counters[self.currw] = (self.counters[self.currw] + 1) % len(self.wdict[self.currw])
            self.jump -= 1
            if self.jump == 0:
                self.wcount = (self.wcount - 1) % len(self.wdict)
                self.currw = list(self.wdict.keys())[self.wcount]
                self.jump = min(self.currw, len(self.wdict[self.currw]))
        return next_procs
        
        
    
    def __str__(self):
        return f"wdict={self.wdict}\nwcount={self.wcount}\ncounters={self.counters}"
    

def take_step(c, num_procs, pattern=None):
    nxt1 = c.next()
    print(nxt1,end=' ')
    pstring = ''.join('1' if (i in nxt1) else '0' for i in range(num_procs))
    print(pstring)
    if pattern is not None:
        pattern.append(pstring)
    return nxt1


if __name__ == "__main__":
    num_cpus = 3
    procs = [
        {'id': 0, 'weight': 4},
        {'id': 1, 'weight': 4},
        {'id': 2, 'weight': 3},
        {'id': 3, 'weight': 3},
        {'id': 4, 'weight': 3},
        {'id': 5, 'weight': 3},
        {'id': 6, 'weight': 2},
        {'id': 7, 'weight': 2},
        {'id': 8, 'weight': 1},
        {'id': 9, 'weight': 1},
        {'id': 10, 'weight': 1}
    ]
    c = Counter(procs, num_cpus)
    print(c)

    
    pat1 = take_step(c, len(procs))
    pat2 = take_step(c, len(procs))
    nxt1 = [0]*len(procs)
    nxt2 = [0]*len(procs)
    rows = []
    while nxt1 != pat1 and nxt2 != pat2:
        nxt1 = nxt2
        nxt2 = take_step(c, len(procs), rows)
    
    # Convert to column‑centric representation, where each value is the pattern for an agent through time -------------
    pattern = {
        col: [row[col] for row in rows] for col in range(len(procs))
    }
    print(pattern)

    for n in range(len(procs)):
        w = sum([int(pattern[n][i]) for i in range(len(rows))])
        print(n, w)
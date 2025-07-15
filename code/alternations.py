N=4
step=2

pattern = {}

ini_tup=[j for j in range(step)]
tup=ini_tup
i=0
while ((tup != ini_tup) or i==0):
    print([1 if j in tup else 0 for j in range(N)])
    #print(list(tup))
    i += step
    tup = [(i+j)%N for j in range(step)]
    

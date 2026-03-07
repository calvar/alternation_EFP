from collections import deque


#NOT WORKING!!!!!!

def multi_cpu_weighted_round_robin(processes, quantum, num_cpus):
    # Sort by arrival
    processes.sort(key=lambda x: x['arrival'])
    n = len(processes)
    mx_time = max(p['arrival'] + p['burst'] for p in processes) * n  # Just a safe upper bound

    ws_ = list(set(p['weight'] for p in processes))
    ws = {i:j for j,i in enumerate(sorted(ws_))}
    ready_queues = [deque() for _ in range(len(ws))]
    cpu_free_at = [0] * num_cpus
    active_processes = set()

    time = 0
    completed = 0
    queue_counter = 0
    while completed < n:
        active_processes.clear()  # Clear active processes at the start of each time unit
        idx = 0
        while idx < n and processes[idx]['arrival'] <= time:
            w = processes[idx]['weight']
            for _ in range(w):
                ready_queues[ws[w]].append(processes[idx])
            idx += 1
        
        for i in range(num_cpus):
            if cpu_free_at[i] <= time and ready_queues:
                p = ready_queues[queue_counter].popleft()
                queue_counter = (queue_counter + 1) % len(ready_queues)
                active_processes.add(p['id'])
                execute_time = min(p['burst'],quantum)
                p['burst'] -= execute_time
                cpu_free_at[i] = time + execute_time
                if p['burst'] == 0:
                    p['arrival'] = mx_time+1
                    completed += 1
                else:
                    p['arrival'] = time + execute_time
        
        active_str = ''.join('1' if p['id'] in active_processes else '0' for p in processes)
        #print(f"Time: {time}, CPU Free At: {cpu_free_at}, Active: {active_str}, Ready Queue: {[p['id'] for p in ready_queue]}")
        print(f"Time: {time}, CPU Free At: {cpu_free_at}, Active: {active_str}")
        time += 1  # Increment time

if __name__ == "__main__":
    procs = [
        {'id': 'P1', 'arrival': 0, 'burst': 10, 'weight': 1},
        {'id': 'P2', 'arrival': 0, 'burst': 10, 'weight': 1},
        {'id': 'P3', 'arrival': 0, 'burst': 10, 'weight': 5},
        {'id': 'P4', 'arrival': 0, 'burst': 10, 'weight': 1},
        {'id': 'P5', 'arrival': 0, 'burst': 10, 'weight': 1},
        {'id': 'P6', 'arrival': 0, 'burst': 10, 'weight': 1},
    ]
    q = 1
    cpus = 4

    multi_cpu_weighted_round_robin(procs, q, cpus)
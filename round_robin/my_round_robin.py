from collections import deque

def multi_cpu_round_robin(processes, quantum, num_cpus):
    # Sort by arrival
    processes.sort(key=lambda x: x['arrival'])
    n = len(processes)
    mx_time = max(p['arrival'] + p['burst'] for p in processes) * n  # Just a safe upper bound

    ready_queue = deque()
    cpu_free_at = [0] * num_cpus
    active_processes = set()

    time = 0
    completed = 0
    while completed < n:
        active_processes.clear()  # Clear active processes at the start of each time unit
        idx = 0
        while idx < n and processes[idx]['arrival'] <= time:
            ready_queue.append(processes[idx])
            idx += 1
        
        for i in range(num_cpus):
            if cpu_free_at[i] <= time and ready_queue:
                p = ready_queue.popleft()
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
        {'id': 'P1', 'arrival': 0, 'burst': 8},
        {'id': 'P2', 'arrival': 0, 'burst': 8},
        {'id': 'P3', 'arrival': 0, 'burst': 8},
        {'id': 'P4', 'arrival': 0, 'burst': 8},
        {'id': 'P5', 'arrival': 0, 'burst': 8},
        {'id': 'P6', 'arrival': 0, 'burst': 8},
    ]
    q = 1
    cpus = 4

    multi_cpu_round_robin(procs, q, cpus)
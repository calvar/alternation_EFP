from collections import deque

def multi_cpu_round_robin(processes, quantum, num_cpus):
    # Sort by arrival
    processes.sort(key=lambda x: x['arrival'])
    n = len(processes)
    
    # State tracking
    rem_burst = {p['id']: p['burst'] for p in processes}
    arrival_times = {p['id']: p['arrival'] for p in processes}
    total_burst = {p['id']: p['burst'] for p in processes}
    
    # cpu_free_at[i] stores the time when CPU i becomes available
    cpu_free_at = [0] * num_cpus
    ready_queue = deque()
    results = []
    
    time = 0
    idx = 0
    completed = 0
    # Track which process is currently on which CPU to prevent 
    # the same process from being picked up by two CPUs at once
    active_processes = set()

    while completed < n:
        # Load processes that have arrived into the ready queue
        while idx < n and processes[idx]['arrival'] <= time:
            ready_queue.append(processes[idx])
            idx += 1

        # Check each CPU to see if it's free
        for i in range(num_cpus):
            if cpu_free_at[i] <= time and ready_queue:
                # Find a process in the queue not currently being worked on
                # (Relevant for very small quanta where a process might still be 
                # 'finishing' its slice on another CPU at this exact timestamp)
                sz = len(ready_queue)
                for _ in range(sz):
                    candidate = ready_queue.popleft()
                    if candidate['id'] not in active_processes:
                        p = candidate
                        break
                    else:
                        ready_queue.append(candidate)
                else:
                    # No eligible process for this CPU right now
                    continue

                p_id = p['id']
                execute_time = min(rem_burst[p_id], quantum)
                
                # Assign to CPU
                active_processes.add(p_id)
                rem_burst[p_id] -= execute_time
                cpu_free_at[i] = time + execute_time
                
                # If finished, record it
                if rem_burst[p_id] == 0:
                    completed += 1
                    active_processes.remove(p_id)
                    results.append({
                        'id': p_id,
                        'finish': cpu_free_at[i],
                        'turnaround': cpu_free_at[i] - arrival_times[p_id],
                        'waiting': (cpu_free_at[i] - arrival_times[p_id]) - total_burst[p_id]
                    })
                else:
                    # If not finished, it will be added back after the quantum
                    # We use a small 'event' logic to re-add it only when the CPU slice ends
                    # For this simulation, we'll re-add it once the time steps forward
                    def re_add(proc=p, finish=cpu_free_at[i]):
                        # This is a simplification; in a real OS, 
                        # an interrupt triggers this.
                        pass
                    # For simplicity in this loop, we'll re-add it 
                    # with a timestamp check in the next cycle.
                    p['re_arrival'] = cpu_free_at[i]
                    # We handle the re-insertion below
                    
        # Increment time to the next "event" (either a process arriving or a CPU finishing)
        # This prevents infinite loops and speeds up the simulation
        possible_times = [p['arrival'] for p in processes if p['arrival'] > time]
        possible_times += [t for t in cpu_free_at if t > time]
        
        # Check for processes that finished their slice and need to go back to queue
        # Note: We sort by re_arrival to maintain fairness
        finished_slices = [p for p in processes if 're_arrival' in p and p['re_arrival'] <= time and rem_burst[p['id']] > 0]
        for p in finished_slices:
            if p['id'] in active_processes:
                active_processes.remove(p['id'])
                ready_queue.append(p)
                del p['re_arrival']

        if possible_times:
            time = min(possible_times)
        else:
            time += 1

        active_str = ''.join('1' if p['id'] in active_processes else '0' for p in processes)
        print(f"Time: {time}, Ready Queue: {[p['id'] for p in ready_queue]}, CPU Free At: {cpu_free_at}, Active: {active_str}")

    return results

# --- Example with 2 CPUs ---
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

stats = multi_cpu_round_robin(procs, q, cpus)
print(f"{'Process':<10} | {'Finish':<10} | {'Turnaround':<15} | {'Waiting':<10}")
for s in sorted(stats, key=lambda x: x['id']):
    print(f"{s['id']:<10} | {s['finish']:<10} | {s['turnaround']:<15} | {s['waiting']:<10}")
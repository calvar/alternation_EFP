from collections import deque


def multi_cpu_weighted_round_robin(processes, quantum, num_cpus):
    """
    Multi-CPU weighted round-robin scheduler.

    Each process should have:
      - id: process identifier (string)
      - arrival: initial arrival time (int >= 0)
      - burst: total CPU burst time (int > 0)
      - weight: relative weight (int > 0)

    A process receives up to (quantum * weight) time units whenever dispatched.
    """
    if quantum <= 0:
        raise ValueError("quantum must be > 0")
    if num_cpus <= 0:
        raise ValueError("num_cpus must be > 0")

    normalized = []
    for process in processes:
        weight = process.get("weight", 1)
        if weight <= 0:
            raise ValueError(f"Process {process.get('id', '?')} has invalid weight: {weight}")
        if process["burst"] <= 0:
            raise ValueError(f"Process {process.get('id', '?')} has invalid burst: {process['burst']}")
        if process["arrival"] < 0:
            raise ValueError(f"Process {process.get('id', '?')} has invalid arrival: {process['arrival']}")

        normalized.append(
            {
                "id": process["id"],
                "arrival": process["arrival"],
                "remaining": process["burst"],
                "weight": weight,
            }
        )

    process_order = [p["id"] for p in normalized]
    normalized.sort(key=lambda p: p["arrival"])

    ready_queue = deque()
    cpu_free_at = [0] * num_cpus
    next_arrival_idx = 0
    requeue_events = []  # list of tuples (time_ready, process)

    completed = 0
    n = len(normalized)
    time = 0

    while completed < n:
        # Add newly arrived processes (initial arrivals)
        while next_arrival_idx < n and normalized[next_arrival_idx]["arrival"] <= time:
            ready_queue.append(normalized[next_arrival_idx])
            next_arrival_idx += 1

        # Add processes whose time slice ended and are ready again
        still_waiting = []
        for time_ready, process in requeue_events:
            if time_ready <= time:
                ready_queue.append(process)
            else:
                still_waiting.append((time_ready, process))
        requeue_events = still_waiting

        active_processes = set()

        # Dispatch to each free CPU
        for cpu_id in range(num_cpus):
            if cpu_free_at[cpu_id] <= time and ready_queue:
                process = ready_queue.popleft()
                active_processes.add(process["id"])

                time_slice = quantum * process["weight"]
                execute_time = min(process["remaining"], time_slice)

                process["remaining"] -= execute_time
                cpu_free_at[cpu_id] = time + execute_time

                if process["remaining"] == 0:
                    completed += 1
                else:
                    requeue_events.append((time + execute_time, process))

        active_str = "".join("1" if process_id in active_processes else "0" for process_id in process_order)
        print(f"Time: {time}, CPU Free At: {cpu_free_at}, Active: {active_str}")

        time += 1


if __name__ == "__main__":
    procs = [
        {"id": "P1", "arrival": 0, "burst": 8, "weight": 1},
        {"id": "P2", "arrival": 0, "burst": 8, "weight": 2},
        {"id": "P3", "arrival": 0, "burst": 8, "weight": 3},
        {"id": "P4", "arrival": 0, "burst": 8, "weight": 1},
        {"id": "P5", "arrival": 0, "burst": 8, "weight": 2},
        {"id": "P6", "arrival": 0, "burst": 8, "weight": 1},
    ]

    q = 1
    cpus = 4

    multi_cpu_weighted_round_robin(procs, q, cpus)

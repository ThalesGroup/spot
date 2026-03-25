# Numerical Experiments

In this page, we provide with the full example of visiting cities.
We describe how we obtain the benchmark.

## Configuration

We disign virtual ISS by shifting them of 1, 2 or 3 days.
```python
from spot.rl.environments.satellite import SatelliteEnvironment

# ISS station
tle_string = ["1 25544U 98067A   17314.40254821  .00006490  00000-0  10525-3 0 9997",
              "2 25544  51.6429  29.4166 0004559 104.3372 354.3186 15.54111847 84492"]

# compute satellites' trajectories
satellites = []
for satellite_id in [1, 2, 3]:
    satellite = SatelliteEnvironment(satellite_id)
    satellite.init_from_tle(tle_string)
    satellites.append(satellite)
```

## Observation requests
We sample random cities on earth.
```python
num_requests = 50
requests = np.genfromtxt(f"data/requests_{num_requests}.txt")
priorities = np.ones(len(requests))
```

## Solvers
We use the classical NetworkXSolver for illustration.
```python
from spot.mis.networkx import NetworkXSolver
delta_t = 10

# prepare solver
solver_params={
    "prefix": f"nx_{delta_t}_{len(requests)}_{len(satellites)}",
    "delta_t": delta_t,
}

solver = NetworkXSolver(solver_params)

# run solver
solver.run(dtos, requests, priorities, satellites)

```

## Metrics
When the solver runs, it collects some metrics.

### Global satisfaction rate
The satisfaction rate is the number of completed requests in percentage.
It can be splited by priorities.

### Time to solution
Time to solution recovers elapsed time for the solver to extract the MIS.
### Image quality
Image quality is distance to 0 pitch (second component of the satellite attitude).
The closest to 0 the better.

### Workload balance between satellites
We can evaluate how well the plan is compared to the balancing evenly the workload between satellites.

### Maneuver duration
The maneuver duration needs to be minimized as it consumes energy onboard and delays the opportunities.

## Global plan results
Here we show an example of the globla plan.
```json
"results": {
    "completion_rate":
    {
        "global_completion_rate": 6.0,
            "prioritized_completion_rates": {"1.0": 6.0}
    },
    "time_to_solution": 30.29348,
    "workload_balance": {"0": 4.0, "1": 0, "2": 2.0},
    "image_quality": NaN,
    "maneuver_duration": NaN,
    "overlap_complexity": 0,
    "global_plan": {"7": [0, 10], "16": [2, 2610], "23": [0, 30]}
}
```

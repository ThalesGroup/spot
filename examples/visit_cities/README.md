# Visiting cities with the ISS

## Prepare data
The data folder containes the file with random cities.
Before running the benchmark, we need to prepare some data:

1. the requests
2. the satellites
3. the Data Take Opportunities (DTOs)

To save requests into files:

```bash
python3 sample_requests.py
```

To generate satellites and compute DTOs:

```bash
python3 compute_dtos.py
```

## Solving the problem

```bash
python3 solve_networkx.py
```

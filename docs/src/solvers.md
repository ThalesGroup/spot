# Solvers

# Near production numerical solver flow.

![THALES + PASQAL flow](/qr4eo_process.png)

## From requests to Maximum Independent Set 
From previous discretization in time of satellites data take opportunities, we end up with DTOS and PRIORITIES. We now need too feed this data to our solvers.

```python
from spot.mis.solver import Solver
solver = Solver()
```

First, we need to collect opportunities from DTOs of each satelllite.

```python
collected_opportunities = solver.collect_opportunities(dtos, priorities)
```

This array is then converted to a graph with edges constraining missions to respect operational constraints.

```python
solving_graph = solving_map.graph_from_collected_opportunities(collected_opportunities)
```
These   graphs can be  fed to Maximum Independent Set solver

### Networkx solver
We will need a classical solver to benchmark our computations on real hardware.  We here describe the algorithm taken as state of the art resolution method to cover the MIS problemm.

```python
classical_solver = NetworkxSolver()
mis_nodes = classical_solver.get_maximum_independet_set(solving_graph)
```
This returns and list of nodes which should be independent.

### Rydberg solver

We can use already described PASQAL solution
```python
from spot.mis.rydbgerg.qubo import SpotQuboSolver

quantum_solver = SpotQUBOSolver()
mis_nodes = quantum_solver.get_maximum_independet_set(solving_graph)
```

Or use a standalone autoencoder-driver solution (less reliable)

```python
quantum_solver = PulseSolver()
mis_nodes  = quantum_solver.get_maximum_independet_set(solving_graph)
```

## Recover global plan
Finally, independently of the quantum algorithm chosen, we can recover the global plan and compute metrics.

```python
global_plan = solver.get_global_plan(mis_nodes)
```
Go to the next page (numerical experiments) to know more about how to interprete the results.

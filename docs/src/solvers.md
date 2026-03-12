# Solvers

# Near production numerical solver flow.

![THALES + PASQAL flow](/qr4eo_process.png)

## Inner graphs generation
From previous discretization in time of satellites data take opportunities, we end up with DTOS and PRIORITIES. We now need too feed this data to our solvers.

```python
from spot.mis.solver import Solver
solver = Solver()
```
First, an intermediate step is required and maps the DTOS to a 4D array.
```python
solving_map = solver.discretize_dtos(dtos, priorities)
```
This array is then converted to a graph with edges constraining missions to respect operational constraints.

```python
solving_graph = solving_map.graph_from_solving_map(solving_map)
```
These   graphs can be  fed to Maximum Independent Set solver

### Networkx solver
We will need a classical solver to benchmark our computations on real hardware.  We here describe the algorithm taken as state of the art resolution method to cover the MIS problemm.

```python
classical_solver = NetworkxSolver()
classical_solver.get_maximum_independet_set(solving_graph)
```

### Rydberg solver

We can use already described PASQAL solution
```python
quantum_solver = QUBOSolver()
mis_nodes = quantum_solver.get_maximum_independet_set(solving_graph)
```
Or use a standalone autoencoder-driver solution (less reliable)

```python
quantum_solver = PulseSolver()
mis_nodes  = quantum_solver.get_maximum_independet_set(solving_graph)
```

Finally, independently of the quantum algorithm chosen, we can recover the global plan and compute metrics.

```python
global_plan = solver.get_global_plan(mis_nodes)
```

Because the starting dates have been chosen arbitrarily at initialization, we need to further iterate with outer/extern iterations.

## Outer iterations
Let us consider the inner solver as the "expert" solver. We use a Reinforcement Learning strategy to fine tune the starting dates and thus tackle the last degree of freedom not tackled by the previously introduced inner solver RL based method adapted from previous work.

### Standard RL strategy

### Expert Iteration strategy

k

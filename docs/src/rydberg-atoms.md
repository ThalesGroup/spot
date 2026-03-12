# Rydberg Atoms

## Motivation

Quantum hardware relying on cold atoms are one of the most promising ones. More inerestingly, they provide with two levels of usage. The first level is the universal gate-based approach, which is under investigation by the scientific community.

The second level - referred to as the analog mode - is a computing paradigm closest to the physics at play at the atomic level.  In this work, we focus our efforts in investigating the potential of the latter mode to solve optimization problems.

## From optimization formalisms to physics

### MIS Solvers

### QUBO Solvers
A recent full-stack implementation of [QUBO-Solver](https://github.com/pasqal-io/qubo-solver/) developped by [PASQAL](https://www.pasqal.com/) allows to solve optimization problems directly with a connection to their [cloud access](https://www.pasqal.com/fr/solutions/cloud/)

Once the problem has been setuppp with a mathemaical formulation, it generally derives graphs that need to be mapped on the QPU respecting its physical constraints.

## Finding optimal placement of atoms
The main challenge to place atoms on a a lattice that is physically relevant is to respect the connectivity of the theoretical graph by matching it to the connectivity imposed by the Rydberg interaction blockade radius.

### Home made heuristics
TODO

### Learning with auto-encoders
One recent research track suggest that such placement can be found via GUROBI solvers, or AUTOENCODERS. Although we implemented the GUROBI solution, it does not scale well with the number of graphs we have generated via our quantum solver proposal.


```python
from spot.mis.rydberg.embeddings.autoencoder import AutoencoderEmbedding

embedder = AutoencoderEmbedding(2)
embedded_graph = embedder.compute_embedding(graph)
traps = embedder.get_traps()
```

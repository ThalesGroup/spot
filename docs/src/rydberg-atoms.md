# Rydberg Atoms

## Motivation
Quantum hardware relying on cold atoms are one of the most promising ones. More inerestingly, they provide with two levels of usage. The first level is the universal gate-based approach, which is under investigation by the scientific community.

The second level - referred to as the analog mode - is a computing paradigm closest to the physics at play at the atomic level.  In this work, we focus our efforts in investigating the potential of the latter mode to solve optimization problems.

It has been shown that many problems expressed with the Maximum Independent Set
formalism can be mapped to an array of atoms to find the solution to the initial
problem.


## Embedding graphs on atomic arrays
The main challenge to place atoms on a a lattice that is physically relevant is to respect the connectivity of the theoretical graph by matching it to the connectivity imposed by the Rydberg interaction blockade radius.

One recent research track suggest that such placement can be found via GUROBI solvers, or AUTOENCODERS. Although we implemented the GUROBI solution, it does not scale well with the number of graphs we have generated via our quantum solver proposal.


### Autoencoder embedder
We rely on the autoencoder method, which should scale better that GUROBI.
We prepare a neural network to place the atoms as in the initial layout, but add regularization losses to match the hardware constraints.
Namely, the minimal distance between atoms should be 5 micro meters. Then the Rydberg blockade radius shouls be a little higher than that, and directly depends on the divice at disposal.

Frist, initialize the embedder with layout dimension and the with device (with
the pulser package)

```python
from spot.mis.rydberg.embeddings.autoencoder import AutoencoderEmbedding
from pulser.devices import AnalogDevice

layout_dimension = 2
device = AnalogDevice
embedder = AutoencoderEmbedding(layout_dimension, device)
```

Once the embedder initialized with some device, we are able to take a graph and project it on a unit disk friendy layout.
Take a graph for example

![Initial theoretical graph](/pulse_solver_0_initial_graph.png)

```python
embedded_graph = embedder.compute_embedding(graph)
traps = embedder.get_traps()
```
This allows to recover the traps and place the atoms so as to recover the initial graph with a unit disk approximation.

![Embedded graph](/pulse_solver_0_embedding.png)

Then, we can use sample atoms by impinging a laser on this layout and recover the Maximum Independent Set apporximation.

![Embedded graph](/pulse_solver_0_sampled_mis.png)

### QUBO Solvers
A recent full-stack implementation of [QUBO-Solver](https://github.com/pasqal-io/qubo-solver/) developped by [PASQAL](https://www.pasqal.com/) allows to solve optimization problems directly with a connection to their [cloud access](https://www.pasqal.com/fr/solutions/cloud/)

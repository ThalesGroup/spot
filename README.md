<p align="center">
    <img src="figures/spot_logo.png" alt="spot_logo", style="width:50%">
</p>

# spot
The SPOT package is intended to solve Satellite Mission Planning with Rydberg
Atoms.
We consider that we have a certain number of satellites at disposition.
Each satellite has an optical instrument on board and can take pictures of Earth
while it passes over a region of interest.
A mission consists in a set of observation requests.
Each day, we need to assign the requests for each of our satellites.

There can be many requests per day to assign to each satellites.
The problem can be formulated as a Maximum Independent Set problem on a graph.
SPOT generates the graph by respecting the satellite agility constraint.

## Get started

In order to get started with our package, one can begin by the examples, in
which we include the visiting cities one.

<p align="center">
    <img src="figures/render_satellite_environment.gif" alt="render_satellite">
</p>

## Documentation

Documentation is available at [spot/docs](https://thalesgroup.github.io/spot/).

## Contributing

If you are interested in contributing to the SPOT project, start by reading the [Contributing guide](/CONTRIBUTING.md).

## License

The licence of the code can be found here [LICENSE](/LICENSE) and is Apache 2.0.
Each dependency of the code has its own licence.

## Project
This repository is part of the following collaborative project:
Towards Operational Quantum Computing for Earth Observation (QR4EO) 
The connection to the PASQAL cloud was provided in the context of this project.
It is not provided by this repository.


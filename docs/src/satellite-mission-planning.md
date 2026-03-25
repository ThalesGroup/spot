# Satellite Mission Planning

# Goal
Given a certain set of regions on earth - refered to as observation requests - and a given satelllite constellation, our goal is to assign these requests to each sattellite so that a maximum number of metrics are satisfied.

![Earth Observation Requests](/earth_requests.png)

## Constraints
In order to schedule a reliable plan for the next day, the operators need to respect a set of constraints.

### Maneuver preparation
The satellites we are working with are supposed to carry onboard optical instruments that can take pictures with a depointing angle.
There is thus a maneuver preparation time that needs to be respected in order for the satellite not to have too many vibrations while operating.

### Observation requests' priorities
Operators need to prioritize requests which are the most important, and postpone those not affoordable yet because of time constraints.
For each request, we thus assign a priority level. Which can be tuned by the scheduler depending on the request client.

### Storage Availability
Each satellite needs to schedule download operations to the ground.
For this constraint, we consider that it can be done once in a day, and exclude the time slot assigned for download from all requests

### Power Availability
The satellite needs to be powered with enough energy to carry the requests, so charging with sun needs to be scheduled appropriatly.
Again, we consider this as a pre processing step, each request will not be able to be taken during the time slot reserved for download

## Dynamics
In addition to the operational constraints described earliier, the operators need to take into account the dynamis of the satellite.
For this, we rely on the orekit python package, which can predict orbits from a starting date and the satellite TLE information strings.

### Initialize satellite from TLE

First, import satellite environment, then init each satellite with the TLE.
The parameter in the constructor of the environment takes as option the number of day that we wish to shift the satellites, which allows us to create multiple virtual satellites from the same TLE info and same starting date.
```python
from sport.rl.environments.satellite import SatelliteEnvironment

# ISS station
tle_string = ["1 25544U 98067A   17314.40254821  .00006490  00000-0  10525-3 0 9997",
              "2 25544  51.6429  29.4166 0004559 104.3372 354.3186 15.54111847 84492"]

satellite = SatelliiteEnviroonment()
satellite.init_from_tle(tle_string)
```
### Initialize acquisition requests

Second, load requests with position on Earth. In our examples, we provide with random cities, an array with longitude and latitude for each request.
```python
requests = random_cities()
```

### Prepare trajectory for next day
In order for the solver to schedule the requests, a first preprocessing step is necessary.
The following code allows to load these data take opportunities, which are an array of begin and end time between 0 and 60*60*24 (the number of seconds in a
day)

```python
dtos = satellite.compute_data_take_opportinity(requests)
```
Go to the solvers' page to see how to use this information to schedule global pland for each satellites.

# Satellite Mission Planning

# Goal
Given a certain set of regionns on earth - refered to as observation requests - and a given satelllite constellation, our goal is to assign these requests to each sattellite so that a maximum number of metrics are satisfied.

![Earth Observation Requests](/earth_requests.png)

## Constraints
In order to schedule a reliable plan for the next day, the operators need to respect a set of constraints.

### Maneuver preparation
The satellites we are working with are supposed to carry onboard optical instruments that can take pictures with a depointing angle 

### Observation requests' priorities
Operators need to prioritize requests which are the most important, and postpone those not affoordable yet because of time constraints.

### Flexibility
The plan generation needs to be fast, because the operators might need to amend the plan whenever a priority is updated.

### Storage Availability
Each satellite needs to schedule download operations to the ground.

### Power Availability
The satellite needs to be powered with enough energy to carry the requests, so charging with sun needs to be scheduled appropriatly.

## Dynamics
In addition to the operational constraints described earliier, the operators need to take into account the dynamis of the satellite.

### Initialize satellite from TLE

```python
from sport.rl.environments.satellite import SatelliteEnvironment

satellite = SatelliiteEnviroonment()
satellite.init_from_tle()

```
### Initialize acquisition requests

```python
requests = random_cities()
```

### Prepare trajectory for next day

```python
satellite.missions = missions 
dtos, positions = satellite.compute_data_take_opportinity()

```

## Metrics

### Global satisfaction rate
### Workload balance between satellites
### Image quality
### Time to solution
### Maneuver duration

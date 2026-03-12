import numpy as np
import pickle

from spot.rl.environments.satellite import SatelliteEnvironment


def prepare_satellite(satellite_id):
    """
    """
    # generate satellite and initialize it with a shifted date
    shift_day = satellite_id
    satellite = SatelliteEnvironment(shift_day)
    
    # ISS station
    tle_string = ["1 25544U 98067A   17314.40254821  .00006490  00000-0  10525-3 0 9997",
                  "2 25544  51.6429  29.4166 0004559 104.3372 354.3186 15.54111847 84492"]
    
    # compute ephemeris
    satellite.init_from_tle(tle)
    
    # save satellite
    with open(f"satellite_{satellite_id}.sat","wb") as file:
        pickle.dump(satellite, file)
    
    return satellite

def compute_dtos(satellite, requests, prefix="dtos"):
    """
    """
    # compute data take opportunity
    dtos = satellite.compute_data_take_opportunity(requests)

    # save dtos
    np.savetxt(f"{prefix}.txt", dtos)


if __name__ == "__main__":

    for num_requests in [10, 50, 100, 500, 1000]:

        # read requests
        requests = np.genfromtxt(f"requests_{num_requests}.txt")
        for satellite_id in [1, 5, 10, 15]:
            satellite = prepare_satellite(satellite_id)
            compute_dtos(requests, satellite, prefix="dtos_{num_requests}_{satellite_id}")

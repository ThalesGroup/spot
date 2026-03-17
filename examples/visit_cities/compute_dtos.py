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
    satellite.init_from_tle(tle_string)
    
    return satellite

if __name__ == "__main__":

    for num_requests in [50]:
        requests = np.genfromtxt(f"data/requests_{num_requests}.txt")
        for satellite_id in [1, 2, 3, 4, 5]:
            satellite = prepare_satellite(satellite_id)
            dtos = satellite.compute_data_take_opportunity(requests)
            np.savetxt(f"data/dtos_{num_requests}_{satellite_id}.txt", dtos)

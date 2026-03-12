import numpy as np
import pickle


from spot.mis.networkx import NetworkXSolver


def solve_networkx(requests, satellites, delta_t):
    """ Solves the problem by using the Maximum Independent Set with Networkx
        building solver
    """

    # read DTOs
    dtos = []
    for satellite_id, _ in enumerate(satellites):
        dto = np.genfromtxt(f"data/dtos_{len(requests)}_{satellite_id}.txt", delimiter=" ")
        dtos.append(dto)
    
    # prepare solver
    sovler_params={
        "prefix": f"nx_{len(requests)}_{len(satellites)}",
        "delta_t": delta_t,
    }
    solver = NetworkXSolver(solver_params)

    # run solver
    solver.run(
        dtos,
        requests,
        priorities,
        satellites),


if __name__ == "__main__":

    num_requests = 100
    num_satellites = 10
    delta_t = 10

    # load satellites
    satellites = []
    for sat_id in range(num_satellites):
        with open(f"data/satellite_{sat_id}.sat","rb") as file:
            satellite = pickle.load(file)
            satellite.init_from_tle()
            satellites.append(satellite)

    # read requests
    requests = np.genfromtxt(f"data/requests_{num_requests}.txt")

    # solve problem
    solve_networkx(requests, satellites, delta_t)

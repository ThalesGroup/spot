import numpy as np
import pandas


def sample_requests(requests, num_requests):
    """
    """
    # random cities
    vals = np.array(requests.sample(num_requests).values,dtype="float")
    lrequests = np.flip(vals,axis=1)
    np.savetxt(f"data/requests_{num_requests}.txt", lrequests)


if __name__ == "__main__":

    requests = pandas.read_csv("data/worldcities.csv", sep=",",usecols=["lat","lng"])

    for num_requests in [10, 50, 100, 500, 1000]:
        sample_requests(requests, num_requests)

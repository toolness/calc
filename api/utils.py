
import math
import statistics


def stdev(values):
    """
    Returns the population (or "unbiased") standard deviation
    for the given values.
    """
    # This replaced numpy.std(), which calculates the population
    # standard deviation, and not the sample standard deviation.
    # statistics.stdev calculates the sample sample deviation, but in
    # order to get the same value as previous calculated with have to
    # use the square root of statistics.pvariance.
    if (len(values) == 0):
        # mirror numpy.std functionality of returning nan when input is empty
        return float('nan')
    # else standard dev is the square root of the variance
    return math.sqrt(statistics.pvariance(values))


def get_histogram(values, num_bins=10):
    """
    Get a histogram of a list of numeric values.
    Returns array of "bin" dicts with keys `count`, `max`, and `min`.
    """

    if (num_bins <= 0):
        raise ValueError('num_bins must be greater than 0')

    # When input array is empty, can't determine range so use 0.0 - 1.0
    # as numpy.histogram does
    if (len(values) == 0):
        mn, mx = 0.0, 1.0
    else:
        mn, mx = min(values), max(values)

    # Adjust mn and mx if they are equivalent (ie, the input array
    # values are all the same number)
    if (mn == mx):
        mn -= 0.5
        mx += 0.5

    bin_width = (mx - mn) / num_bins

    # initialize the bins
    bins = [{
        'min': mn + bin_width * i,
        'max': mn + bin_width * (i + 1),
        'count': 0
    } for i in range(0, num_bins)]

    # bin the values
    for val in values:
        for b in bins:
            if (val >= b['min'] and val < b['max']):
                b['count'] += 1
        # correction for when a value == the max value
        if (val == mx and b['max'] == mx):
            b['count'] += 1

    return bins

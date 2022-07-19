def mean(vector: list) -> float:
    """Return the mean value of the vector.

    -----
    INFO:
    -----
    The mean value is the sum of all values, divided by its length.
    Sometimes, the mean value means to be the expected value (E(x)).

    --------
    FORMULA:
    --------
    E(x) = (x1 + x2 + ... + xn) / NO

        where:
            x1...xn: vector values
            NO: number of observations
    -----
    Args:
        vector (list): value vector

    Returns:
        float: the mean value
    """
    m = 0
    for item in vector:
        m += item
    return m / len(vector)

def var(vector: list) -> float:
    """Return variance of the vector

    -----
    INFO:
    -----
    The variance shows, how much values in vector deviates from its mean value in average.
    The deviation can be positive or negative. Because of that, to transform negative values to positive use squaring.

    Lower the variance, the closer the values are to each other.

    --------
    FORMULA:
    --------
    VAR(x) = E((x - E(x))^2)
        
        where
            E(x): mean value of x vector
            x - E(x): difference between x and mean value
    -----
    Args:
        vector (list): value vector

    Returns:
        float: variance
    """
    mean_value = mean(vector)
    var = []
    for item in vector:
        var.append((item - mean_value)**2)
    return mean(var)

def std(vector: list) -> float:
    """Return Standart Deviation of vector

    ------
    INFO:
    ------
    The standart deviation is the same as a variance,
    but here, to get STD, we calculate the square root
    of the variance, to get rid of squaring in VAR function.

    Denoted as the sigma symbol.

    --------
    FORMULA:
    --------  
    STD(x) = SQRT(VAR(x))

    -----
    Args:
        vector (list): value vector

    Returns:
        float: standart deviation value
    """
    return var(vector)**0.5

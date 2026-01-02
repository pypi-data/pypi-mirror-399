import numpy as np
import pandas as pd


def calculate_statistics(data: list) -> dict:
    """
    Calculate basic statistics for a given list of numbers.

    Parameters:
    data (list or np.ndarray): A list or array of numerical values.

    Returns:
    dict: A dictionary containing mean, median, and standard deviation.
    """ 
    d = np.array(data)
    statistics = {
        'mean': np.mean(d),
        'median': np.median(d),
        'std_dev': np.std(d)
    }
    
    return statistics
    


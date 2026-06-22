import numpy as np

def calculate_exponential_smoothing(data, alpha=0.3, initial_forecast=None):
    if initial_forecast is None:
        initial_forecast = data[0]

    es_values = [initial_forecast]

    for i in range(len(data)):
        es = alpha * data[i] + (1 - alpha) * es_values[-1]
        es_values.append(es)

    return es_values[:-1]
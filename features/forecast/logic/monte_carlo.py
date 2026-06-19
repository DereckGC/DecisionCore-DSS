import numpy as np

def monte_carlo_forecast(base_forecast, errors, simulations=10000):

    simulated_values = (
        np.random.choice(errors, size=simulations)
        + base_forecast
    )

    return {
        "mean": np.mean(simulated_values),
        "min": np.min(simulated_values),
        "max": np.max(simulated_values),
        "std": np.std(simulated_values),
        "values": simulated_values
    }
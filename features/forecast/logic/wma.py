import numpy as np

def calculate_wma(data, period):
    weights = np.arange(1, period + 1)

    forecasts = [np.nan] * period

    for i in range(len(data) - period):
        window = data[i:i + period]

        forecast = (
            np.sum(np.array(window) * weights)
            / weights.sum()
        )

        forecasts.append(forecast)

    return forecasts
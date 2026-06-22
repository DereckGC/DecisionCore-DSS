import numpy as np
import pandas as pd

def calculate_deviations(actual, predicted):
    actual = np.array(actual)
    predicted = np.array(predicted)

    mask = ~(np.isnan(actual) | np.isnan(predicted))

    actual_clean = actual[mask]
    predicted_clean = predicted[mask]

    if len(actual_clean) == 0:
        return {
            'deviations': [],
            'MAD': np.nan,
            'RMSE': np.nan,
            'MAPE': np.nan
        }

    deviations = actual_clean - predicted_clean

    mad = np.mean(np.abs(deviations))
    rmse = np.sqrt(np.mean(deviations ** 2))

    denominator = np.where(actual_clean == 0, 1e-10, actual_clean)
    mape = np.mean(np.abs(deviations / denominator)) * 100

    return {
        'deviations': deviations,
        'MAD': mad,
        'RMSE': rmse,
        'MAPE': mape
    }

def compare_methods(data, wma_values, es_values):
    data_array = np.array(data)
    wma_array = np.array(wma_values)
    es_array = np.array(es_values)

    results = {
        'WMA': calculate_deviations(data_array, wma_array),
        'ES': calculate_deviations(data_array, es_array)
    }

    metrics_df = pd.DataFrame({
        'Método': ['WMA', 'ES'],
        'DMA': [results['WMA']['MAD'], results['ES']['MAD']],
        'RMSE': [results['WMA']['RMSE'], results['ES']['RMSE']],
        'MAPE (%)': [results['WMA']['MAPE'], results['ES']['MAPE']]
    })

    return metrics_df, results
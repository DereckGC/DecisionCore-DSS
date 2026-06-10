def calculate_veip(vecip_data, vme_data):
    if vecip_data is None or vme_data is None:
        return None

    return vecip_data - vme_data["best_value"]

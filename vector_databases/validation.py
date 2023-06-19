from errors import DisparityBetweenDatabasesError


def ensure_parity_between_databases(memories_raw_data, index):
    if index.get_n_items() != len(memories_raw_data):
        raise DisparityBetweenDatabasesError(
            f"The length of the index contents ({index.get_n_items()}) doesn't match the length of the raw memory data ({len(memories_raw_data)})"
        )

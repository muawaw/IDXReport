import pandas as pd
from typing import Any

def parse_data_variable(variable: Any) -> Any:
        """
        Data validation checker if the data is Unix Timestamp then Parse it to ISO Format else dont
        """
        # Detect Unix Epoch Timestamps (e.g. 1700000000+ is post-2023)
        if isinstance(variable, (int, float)) and not isinstance(variable, bool):
            if variable > 946684800:  # Epoch for Jan 1, 2000
                try:
                    converted_timestamp = pd.to_datetime(variable, unit = 's').strftime("%Y-%m-%dT%H:%M:%S")
                    return converted_timestamp
                except Exception:
                    return variable
            else:
                return variable
        else:
            return variable
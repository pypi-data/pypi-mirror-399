import numpy as np
import pandas as pd

def downcast_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Downcasts numeric columns to more memory-efficient types."""
    df_copy = df.copy()
    for col in df_copy.select_dtypes(include=np.number).columns:
        # Downcast integers
        if pd.api.types.is_integer_dtype(df_copy[col]):
            df_copy[col] = pd.to_numeric(df_copy[col], downcast='integer')
        # Downcast floats
        else:
            df_copy[col] = pd.to_numeric(df_copy[col], downcast='float')
    return df_copy
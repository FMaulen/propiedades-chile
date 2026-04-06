from src.outliers import clean_outliers
from src.preprocessing import clean_data
from src.create_model_pipeline import create_model
import pandas as pd

def run_pipeline(df: pd.DataFrame, full: bool) -> pd.DataFrame:
    df_clean = df.copy()
    
    df_clean = clean_data(df_clean)
    df_clean = clean_outliers(df_clean)
    df_clean = create_model(df_clean, full)

    return df_clean
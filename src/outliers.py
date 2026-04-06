import pandas as pd

def _detectar_outliers_iqr(serie):
    Q1 = serie.quantile(0.25)
    Q3 = serie.quantile(0.75)
    IQR = Q3 - Q1

    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR

    mascara = (serie < limite_inferior) | (serie > limite_superior)

    return mascara, limite_inferior, limite_superior


def clean_outliers(df_clean: pd.DataFrame) -> pd.DataFrame:
    LIMITES = dict()

    df_numeric = df_clean.select_dtypes('number')

    for col in df_numeric.columns:
        _, _, ls = _detectar_outliers_iqr(df_numeric[col])
        LIMITES[col] = (ls)

    for col, sup in LIMITES.items():
        match col:
            case 'Price_UF':
                df_clean = df_clean[(df_clean['Price_UF'] > 500) & (df_clean['Price_UF'] < sup)]
            case 'Built Area':
                df_clean = df_clean[(df_clean['Built Area'] > 42) & (df_clean['Built Area'] < sup)]
            case 'Total Area':
                df_clean = df_clean[(df_clean['Total Area'] > 42) & (df_clean['Total Area'] < sup)]
            case 'Baths':
                df_clean = df_clean[(df_clean['Baths'] > 0) & (df_clean['Baths'] < 6)]
            case _:
                pass
    df_clean['UF_m2'] = df_clean['Price_UF'] / df_clean['Built Area']
    return df_clean
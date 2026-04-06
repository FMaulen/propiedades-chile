import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder 
from sklearn.compose import ColumnTransformer 
from sklearn.pipeline import Pipeline 

def create_model(df: pd.DataFrame, full: bool):
    numeric_features = ['Price_UF', 'UF_m2', 'Total Area', 'Built Area', 'Baths', 'Parking', 'Dorms']
    categorical_features = ['Comuna']

    # Transformaciones
    preprocessor = ColumnTransformer(
        transformers = [
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ]
    )    

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor)
    ])
    if full:
        data_transformed = pipeline.fit_transform(df)
        return data_transformed

    return df
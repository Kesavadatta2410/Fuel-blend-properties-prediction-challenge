# -*- coding: utf-8 -*-
"""Untitled10.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Qq8cfRCsB4aGNsrOZBLTH6Lzk-oFL2hi
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load data
train = pd.read_csv('/content/train.csv')
test = pd.read_csv('/content/test.csv')

# Separate features and targets
X = train.iloc[:, :-10].copy()  # First 55 columns — use .copy() to avoid SettingWithCopyWarning
y = train.iloc[:, -10:]         # Last 10 columns

# Handle any missing values
X.fillna(0, inplace=True)
test.fillna(0, inplace=True)

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# If test has an ID column (e.g., first column), exclude it during scaling
# Modify this based on the actual structure of test.csv
if 'ID' in test.columns:
    test_features = test.drop(columns=['ID'])
else:
    test_features = test.iloc[:, 1:]  # Fallback if ID is unnamed

test_scaled = scaler.transform(test_features)

from sklearn.preprocessing import PolynomialFeatures

poly = PolynomialFeatures(degree=2, interaction_only=True)
X_poly = poly.fit_transform(X_scaled)
test_poly = poly.transform(test_scaled)

!pip install catboost

from catboost import CatBoostRegressor
from sklearn.multioutput import MultiOutputRegressor

model = MultiOutputRegressor(CatBoostRegressor(iterations=1000, depth=6, learning_rate=0.1, verbose=0))
model.fit(X_poly, y)

from sklearn.metrics import mean_absolute_percentage_error
from sklearn.model_selection import cross_val_score

X_train, X_val, y_train, y_val = train_test_split(X_poly, y, test_size=0.2, random_state=42)

model.fit(X_train, y_train)
y_pred = model.predict(X_val)

# Calculate MAPE for each target and average
mape_scores = [mean_absolute_percentage_error(y_val.iloc[:, i], y_pred[:, i]) for i in range(10)]
average_mape = sum(mape_scores) / 10
print(f'Average MAPE: {average_mape}')

test_predictions = model.predict(test_poly)

# Create submission DataFrame
submission = pd.DataFrame(test_predictions, columns=[f'BlendProperty{i+1}' for i in range(10)])
submission['ID'] = test['ID']  # Assuming ID is the first column in test.csv
submission = submission[['ID'] + [f'BlendProperty{i+1}' for i in range(10)]]
submission.to_csv('submission.csv', index=False)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 22:27:17 2021

@author: eoinvondy
"""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV

from sklearn.metrics import classification_report

# scikit models
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier 
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.preprocessing import MinMaxScaler


st.set_page_config(
    page_title='Model Exploration', 
    layout='wide'
)

st.sidebar.title('Airbnb Data Analysis')
st.sidebar.write(
    '''
    A dashboard for exploring the performance of various models 
    in classifying target columns of the Airbnb dataset.
    '''
)

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    df.columns = [col.lower() for col in df.columns]

    return df

data = load_data('visdata.csv')

st.write('Here is a sample of the input data after loading:')
st.dataframe(data.head(10))


target_col = st.sidebar.selectbox(
    label='Select the target column from input data:',
    options=sorted(data.columns),
)

# Use the selected target variable to define X and y objects for using in ML
y = data[target_col].values
X = data.drop(target_col, axis=1)
categorical_cols = X.columns



### MODEL ###


# Encode the cetegorical columns
X = pd.get_dummies(
    X,
    columns=[col for col in categorical_cols if col!=target_col],
    drop_first=True
)


# Initialise the scaler
scaler = MinMaxScaler() 

# Apply MinMaxScaler and cast to DataFrame 
data = pd.DataFrame(
                    scaler.fit_transform(data), 
                    columns = data.columns, 
                    index = data.index)

# Print the first rows
st.write('Here is a sample of the input data after MinMaxScaler:')
st.dataframe(data.head(10))



# Define portion for the train/test split
test_proportion = st.sidebar.slider(
    label='Proportion of data to hold back for testing:',
    min_value=0.05,
    max_value=0.95,
    value=0.2,
    step=0.05,
    
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=test_proportion,
    random_state=1,
)

def params_DecisionTreeClassifier():
    """Get user input for defined parameters of model."""
    params = {
        'max_depth': st.sidebar.slider(
            label='Max depth of tree:',
            min_value=1,
            max_value=20,
            step=1,
        ),
        'criterion': st.sidebar.select_slider(
            label='Function to measure the quality of a split:',
            options=['entropy', 'gini']
        ),
    }

    return params

def params_KNeighborsClassifier():
    """Get user input for defined parameters of model."""
    params = {
        'n_neighbors': st.sidebar.slider(
            label='Number of neighbors:',
            min_value=1,
            max_value=20,
            step=1,
        ),
    }

    return params

def params_LogisticRegression():
    """Get user input for defined parameters of model."""
    params = {
        'C': st.sidebar.select_slider(
            label='C',
            options=list(np.logspace(-5, 1, 7))
        ),
    }

    return params

def params_GaussianNB():
    """Get user input for defined parameters of model."""
    params = {
    }

    return params

def params_SVC():
    """Get user input for defined parameters of model."""
    params = {
        'C': st.sidebar.select_slider(
            label='Regularization parameter',
            options=list(np.logspace(-5, 2, 8))
        ),
        'kernel': st.sidebar.select_slider(
            label='Function to measure the quality of a split:',
            options=['linear', 'poly', 'rbf', 'sigmoid']
        ),
    }

    return params

# This dictionary contains all the models available as well as the model
# parameter function which allows user customisation for the model.

models = {
    'decision trees' : {
        'model': DecisionTreeClassifier,
        'params': params_DecisionTreeClassifier,
    },
    'k nearest neighbours': {
        'model': KNeighborsClassifier,
        'params': params_KNeighborsClassifier,
    },
    'logistic regression': {
        'model': LogisticRegression,
        'params': params_LogisticRegression,
    },
    'gaussian naive bayes': {
        'model': GaussianNB,
        'params': params_GaussianNB,
    },
    'support vector machine': {
        'model': SVC,
        'params': params_SVC,
    },
}

model_name = st.sidebar.selectbox(
    label='Choose ML model to apply:',
    options=sorted(models.keys())
)

model_params = models[model_name]['params']()
    
# Set instance of model with base parameters
model = models[model_name]['model'](**model_params)

st.sidebar.write(f'{model_name} parameters are:')
st.sidebar.write(model.get_params())

with st.spinner('Running the model...'):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

st.write(f'Accuracy: {model.score(X_test, y_test)}')
st.text('Model Report:\n ' + classification_report(y_test, y_pred, zero_division=0))

#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 18:17:26 2024

@author: aashi
"""
#Importing required libraries
import io
import pickle
from flask import Flask, request, send_file
from flasgger import Swagger
import pandas as pd

#Loading the trained random forest model using pickle
with open(r'../predicting_employee_attrition/model_artifacts/rf.pkl', 'rb') as model_pkl:
    model = pickle.load(model_pkl)


#Loading the saved ColumnTransformer using pickle
with open(r'../predicting_employee_attrition/model_artifacts/ct.pkl', 'rb') as ct_pkl:
    ct = pickle.load(ct_pkl)

#Loading the saved scaler using pickle
with open(r'../predicting_employee_attrition/model_artifacts/sc.pkl', 'rb') as sc_pkl:
    sc = pickle.load(sc_pkl)
    
app = Flask(__name__)
swagger = Swagger(app)


#Defining function to drop specific (duplicate) columns
def drop_specific_columns(dataset):
    dataset.drop(['EmployeeCount','StandardHours','Over18','EmployeeNumber'],axis=1, inplace=True, errors='ignore')
    return dataset


#Defining function to rearrange specific columns
def rearrange_columns(dataset):
    # Define the columns you want to keep and rearrange
    expected_columns = ['BusinessTravel', 'Department', 'EducationField', 'Gender', 'JobRole', 
                    'MaritalStatus', 'OverTime', 'Age', 'DailyRate', 'DistanceFromHome', 
                    'Education', 'EnvironmentSatisfaction', 'HourlyRate', 'JobInvolvement', 
                    'JobLevel', 'JobSatisfaction', 'MonthlyIncome', 'MonthlyRate', 
                    'NumCompaniesWorked', 'PercentSalaryHike', 'PerformanceRating', 
                    'RelationshipSatisfaction', 'StockOptionLevel', 'TotalWorkingYears', 
                    'TrainingTimesLastYear', 'WorkLifeBalance', 'YearsAtCompany', 
                    'YearsInCurrentRole', 'YearsSinceLastPromotion', 'YearsWithCurrManager']
    # Select only the available columns in the dataset
    dataset = dataset[[col for col in expected_columns if col in dataset.columns]]
    return dataset



# Defining API endpoint to handle file upload
@app.route('/predict', methods=['POST'])
def predict():
    """
    This is the prediction endpoint.
    It takes a CSV file as input and returns predictions.
    ---
    parameters:
      - name: input_file
        in: formData
        type: file
        required: true
        description: The CSV file containing the input data.
    responses:
      200:
        description: Predictions of Employee Attrition (1=Employee will exit, 0=Employee will stay)
    """
    #reading the input file
    input_data = pd.read_csv(request.files.get("input_file"))
    
    #retaining the original input data
    original_input_data = input_data
    
    #dropping redundant columns
    input_data = drop_specific_columns(input_data)
    
    #rearraging columns to match expected order for model consumption
    input_data = rearrange_columns(input_data)
    
    
    #encoding categorical variables using saved ColumnTransformer
    encoded_input_data = ct.transform(input_data)
    onehot_encoder = ct.named_transformers_['encoder']
    encoded_column_names = onehot_encoder.get_feature_names_out(input_data.columns[:7])
    remainder_column_names = input_data.columns[7:]
    new_column_names = list(encoded_column_names) + list(remainder_column_names)
    input_data = pd.DataFrame(encoded_input_data, columns=new_column_names, index=input_data.index)
    
    #standardizing numerical variables using saved scaler
    input_data.iloc[:, 28:] = sc.transform(input_data.iloc[:, 28:])
    
    #performing predictions using the pre-trained model
    predictions = model.predict(input_data)
    
    #appending predictions to the original input data
    original_input_data['Predictions'] = predictions
    
    #creating an in-memory CSV file with both input data and predictions
    output = io.BytesIO()
    original_input_data.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)

    #sending the CSV file as a response
    return send_file(output, mimetype='text/csv', as_attachment=True, attachment_filename='predictions_output.csv')
    
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000, debug=True)
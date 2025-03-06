import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import glob
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import io
from django.core.files.base import ContentFile
import base64
import json
def demand_forecast(request):
    if request.method == "GET":
        with open('pred/stops.json','r') as f:
            stops = json.load(f)
        return render(request, "forecast_form.html", {'stops': stops})
    
    elif request.method == "POST":
        # user_from_stop = request.POST.get("from_stop_name")
        user_to_stop = request.POST.get("to_stop_name")
        user_date = request.POST.get("date")

        csv_directory_path = 'pred/data/airflow.csv'

        data_grouped_pandas = pd.read_csv(csv_directory_path)

        # Filter data for the selected from and to stop
        data_grouped_pandas = data_grouped_pandas[
            # (data_grouped_pandas['FROM_STOP_NAME'] == user_from_stop) & 
            (data_grouped_pandas['TO_STOP_NAME'] == user_to_stop)
        ]
        print(data_grouped_pandas.head())
        # Ensure DATE_HOUR is parsed as a datetime column
        data_grouped_pandas["DATE_HOUR"] = pd.to_datetime(
            data_grouped_pandas["DATE_HOUR"], format="%Y-%m-%d %H", errors="coerce"
        )

        # Drop invalid rows
        data_grouped_pandas = data_grouped_pandas.dropna(subset=["DATE_HOUR"]).sort_values(by="DATE_HOUR")
        
        try:
            prediction_start_time = pd.to_datetime(f"{user_date} 00:00")
            prediction_end_time = pd.to_datetime(f"{user_date} 23:59")
        except ValueError:
            return JsonResponse({"error": "Invalid date format. Please use YYYY-MM-DD."})

        # Filter data for the last 24 and 48 hours before prediction start time
        data_filtered = data_grouped_pandas[data_grouped_pandas["DATE_HOUR"] < prediction_start_time].tail(24)
        data_filtered_2days = data_grouped_pandas[data_grouped_pandas["DATE_HOUR"] < prediction_end_time].tail(48)

        if data_filtered.empty:
            return JsonResponse({"error": f"Not enough historical data available for {user_date}. Please select another date.","data_grouped_pandas":data_grouped_pandas.to_dict()})

        # Check if there is at least one sample before applying MinMaxScaler
        if len(data_filtered) == 0:
            return JsonResponse({"error": "Insufficient data to make predictions.","data_grouped_pandas":data_grouped_pandas.to_dict()})

        scaler = MinMaxScaler()

        try:
            scaler.fit(data_filtered["TOTAL_PASSENGER"].values.reshape(-1, 1))
        except ValueError:
            return JsonResponse({"error": "Not enough data points to scale. Please try a different date."})

        # Normalize data
        data_filtered["TOTAL_PASSENGERS_NORMALIZED"] = scaler.transform(
            data_filtered["TOTAL_PASSENGER"].values.reshape(-1, 1)
        )

        # Prepare input for the model
        previous_24 = data_filtered["TOTAL_PASSENGERS_NORMALIZED"].values
        if len(previous_24) < 24:
            previous_24 = np.pad(previous_24, (24 - len(previous_24), 0), constant_values=0)

        previous_24 = previous_24.reshape((1, 24, 1))

        # Load the model
        model_path = f'pred/models/joined.keras'
        try:
            model = load_model(model_path)
        except Exception as e:
            return JsonResponse({"error": f"Failed to load the model. Error: {str(e)}"})

        # Predict demand
        predictions = []
        current_input = previous_24

        for _ in range(24):
            pred = model.predict(current_input, verbose=0)
            predictions.append(pred[0][0])
            current_input = np.append(current_input[:, 1:, :], pred.reshape(1, 1, 1), axis=1)

        # Inverse normalization
        predictions_actual = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()

        # Create plot
        plt.figure(figsize=(10, 6))
        actual_demand = data_filtered["TOTAL_PASSENGER"].values
        actual_2day_demand = data_filtered["TOTAL_PASSENGER"].values if not data_filtered.empty else []

        if len(actual_2day_demand) < 24:
            actual_2day_demand = [0] * (24 - len(actual_demand)) + list(actual_demand)

        plt.plot(range(-24, 0), actual_demand, label="Actual Demand (Last 24 Hours)", marker='o', color='blue')
        plt.plot(range(24), predictions_actual, label="Predicted Demand (Next 24 Hours)", marker='o', color='red')
        plt.axvline(x=0, linestyle="--", color="gray", label="Prediction Start")
        plt.xlabel("Hour")
        plt.ylabel("Passenger Count")
        plt.title(f"Demand Forecast for {user_date} and the Next 24 Hours")
        plt.legend()
        plt.grid()

        # Save plot to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        return render(request, "forecast_results.html", {
            "total_demand": sum(predictions_actual),
            "hourly_demand": list(predictions_actual),
            "image_base64": image_base64,
        })

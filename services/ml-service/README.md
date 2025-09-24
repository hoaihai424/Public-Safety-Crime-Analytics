# Machine Learning Service

This service is responsible for training and serving machine learning models. It provides a RESTful API for getting predictions.

## Technology

-   FastAPI for serving the API.
-   PyTorch, TensorFlow, or Scikit-learn for ML models.

## Features

-   **/classification**: Predicts the type of crime likely to occur.
-   **/clustering**: Detects areas with similar crime patterns.
-   **/forecasting**: Predicts the number of crimes by season.

## Directories

-   `/src`: The FastAPI application code.
-   `/models`: Saved/pre-trained model artifacts.
-   `/notebooks`: Jupyter notebooks for experimentation and analysis.
-   `/tests`: Tests for the service.

## API Endpoints

(Define the API endpoints here, e.g., using OpenAPI/Swagger documentation.)

-   `POST /predict/crime-type`
-   `GET /clusters/similar-areas`
-   `GET /forecast/seasonal`

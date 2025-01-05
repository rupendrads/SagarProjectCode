# Index Creation/Deletion API

## Overview

This repository provides an API for creating and deleting indices based on filenames. It includes two main endpoints:
- `POST /create-indices`: Creates indices for specified files.
- `DELETE /delete-indices`: Deletes indices for specified files.

These APIs can be used to manage file-based indexing for applications requiring structured data storage, retrieval, and deletion.

## Prerequisites

To run this API, ensure you have the following:
- **Python 3.7+**
- **FastAPI** 
- Any additional dependencies, as specified in `requirements.txt`

## Setup and Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/CSACHIN77/Sagar_Dataharvesting.git
    cd GDFL_upload\db_indices_management
    ```

2. **Install dependencies**:
    Use `pip` to install required packages.
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the API server**:
    Start the server by running the main Python script (replace `app.py` with the actual filename if different).
    ```bash
    python app.py
    ```
    By default, the server will run on `http://127.0.0.1:5000`. Update the host and port as needed.

## API Endpoints

### 1. Create Indices
- **Endpoint**: `POST /create-indices`
- **Description**: Creates indices for the specified files.
- **Request Body**:
    ```json
    {
        "filenames": [
            "GFDLNFO_BACKADJUSTED_01092024.csv",
            "GFDLNFO_BACKADJUSTED_01092023.csv",
            "GFDLNFO_BACKADJUSTED_01092022.csv"
        ]
    }
    ```
- **Response**:
    - **Success**:
        ```json
        {
            "status": "success"
        }
        ```
    - **Error**:
        ```json
        {
            "status": "error"
        }
        ```

### 2. Delete Indices
- **Endpoint**: `DELETE /delete-indices`
- **Description**: Deletes indices for the specified files.
- **Request Body**:
    ```json
    {
        "filenames": [
            "GFDLNFO_BACKADJUSTED_01092024.csv",
            "GFDLNFO_BACKADJUSTED_01092023.csv",
            "GFDLNFO_BACKADJUSTED_01092022.csv"
        ]
    }
    ```
- **Response**:
    - **Success**:
        ```json
        {
            "status": "success"
        }
        ```
    - **Error**:
        ```json
        {
            "status": "error"
            
        }
        ```

## Usage

### Example Request Using `curl`

1. **Create Indices**:
    ```bash
    curl -X POST http://127.0.0.1:9001/create-indices \
    -H "Content-Type: application/json" \
    -d '{
          "filenames": [
              "GFDLNFO_BACKADJUSTED_01092024.csv",
              "GFDLNFO_BACKADJUSTED_01092023.csv",
              "GFDLNFO_BACKADJUSTED_01092022.csv"
          ]
        }'
    ```

2. **Delete Indices**:
    ```bash
    curl -X DELETE http://127.0.0.1:9001/delete-indices \
    -H "Content-Type: application/json" \
    -d '{
          "filenames": [
              "GFDLNFO_BACKADJUSTED_01092024.csv",
              "GFDLNFO_BACKADJUSTED_01092023.csv",
              "GFDLNFO_BACKADJUSTED_01092022.csv"
          ]
        }'
    ```

## Important Notes

- **Host and Port**: Replace `127.0.0.1:9001` with the actual host and port of your API server.
- **Error Handling and Logging**: Consider adding error handling to return informative error messages and logging to track API requests and failures.


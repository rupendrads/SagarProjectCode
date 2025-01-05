# Folder Processing API

This FastAPI application processes CSV files containing options and futures data for NSE, validates them against a MySQL database, and manages file organization based on data consistency checks.

## Overview

The application provides an API endpoint that:
1. Processes CSV files with the pattern `GFDLNFO_BACKADJUSTED_YYYYMMDD.csv`
2. Compares record counts between files and database tables
3. Organizes files into processed and discrepancy folders based on validation results
4. Maintains detailed logs of the entire process

## Prerequisites

- Python 3.7+
- MySQL Server
- Sufficient disk space for file processing
- Network access to the MySQL database

## Installation

1. Clone this repository to your local machine

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `constants.py` file with your database credentials:
```python
db_creds = {
    'host': 'localhost',
    'database': 'index_data',
    'user': 'root',
    'password': 'your_password'
}
```

2. Ensure the MySQL database is properly configured with:
   - A database named `index_data`
   - Tables following the patterns `*_YYYY` or `*_fut`
   - An `upload_status` table for tracking file processing status

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. The API will be available at `http://localhost:8000`

## API Usage

### Process Folder Endpoint

**Endpoint:** `/process_folder`
**Method:** GET
**Request Body:**
```json
{
    "folderPath": "/path/to/your/folder"
}
```
USE // instead of  / if you are running it on windows in folderPath
The folder should contain CSV files following the naming pattern: `GFDLNFO_BACKADJUSTED_DDMMYYYY.csv`

### Response

```json
{
    "message": "Processing completed. Check logs and folders for details."
}
```

## Folder Structure

The application creates the following folder structure:
```
input_folder/
├── GFDLNFO_BACKADJUSTED_*.csv
├── processed_files/
│   └── (successfully processed files)
└── discrepancy/
    └── (files with count mismatches)
```

## Generated Files

1. `database_tables.csv`: Contains list of relevant database tables
2. `discrepancy.txt`: Log of processing errors and count mismatches
3. `app.log`: Detailed application logs

## Process Flow

1. Validates the input folder path
2. Identifies relevant CSV files
3. Creates a cache of database table names
4. For each file:
   - Extracts date from filename
   - Queries database for matching records
   - Compares record counts
   - Moves files to appropriate folders
   - Logs results and any discrepancies

## Error Handling

- Invalid folder paths return 400 error
- Database connection issues return 500 error
- File processing errors are logged to `discrepancy.txt`
- All operations are logged to `app.log`

## Requirements.txt

The following dependencies are required and can be installed via the requirements.txt file:

```txt
fastapi
uvicorn
pydantic
mysql-connector-python
pandas
python-multipart
```

To install dependencies, run:
```bash
pip install -r requirements.txt
```

## Logging

The application maintains detailed logs in:
- Console output
- `app.log` file
- `discrepancy.txt` for specific processing issues

Log files contain timestamps, log levels, and detailed error messages.

## Troubleshooting

1. Database Connection Issues:
   - Verify database credentials in `constants.py`
   - Ensure MySQL server is running
   - Check network connectivity

2. File Processing Issues:
   - Verify file naming convention
   - Check file permissions
   - Review `discrepancy.txt` for specific errors

3. API Connection Issues:
   - Confirm FastAPI server is running
   - Check port availability
   - Verify network/firewall settings

## Notes

- The application expects specific table naming conventions in the database
- Files are processed based on date information in filenames
- Database queries combine data from year-specific and future tables
- Files are moved to different folders based on validation results

## Support

For issues and questions:
- Check the application logs
- Review `discrepancy.txt`
- Verify database connectivity
- Ensure proper file naming conventions

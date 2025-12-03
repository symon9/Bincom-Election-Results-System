# ElectionScope

ElectionScope is a comprehensive web application built with Django for analyzing and managing election results in Delta State. It provides an intuitive interface for viewing individual polling unit results, calculating summed totals for Local Government Areas (LGAs), and entering new election data.

## Features

### 1. Polling Unit Results
*   **Granular Analysis**: View detailed election results for any specific polling unit.
*   **Smart Filtering**: Uses chained dropdown menus (LGA -> Ward -> Polling Unit) to easily locate specific units without overwhelming lists.
*   **Visual Data**: Presents party scores in a clear, readable table format.

### 2. LGA Summed Totals
*   **Dynamic Calculation**: Calculates the total votes for all parties within a Local Government Area in real-time.
*   **Accuracy**: Aggregates data directly from individual polling unit results, ensuring totals always reflect the most current data (bypassing potentially outdated pre-calculated tables).

### 3. Add New Results
*   **Data Entry**: A user-friendly form to input election results for new polling units.
*   **Validation**: Ensures all required fields are completed and party scores are valid.
*   **Seamless Integration**: New entries are immediately available for analysis in both Polling Unit and LGA Total views.

## Technology Stack

*   **Backend**: Python 3, Django 5
*   **Frontend**: HTML5, Bootstrap 5 (Premium UI with Glassmorphism), JavaScript (jQuery for AJAX)
*   **Database**: SQLite (Default), compatible with MySQL/PostgreSQL
*   **Styling**: Custom CSS variables, Inter & Outfit fonts, Responsive Design

## Setup Instructions

### Prerequisites
*   Python 3.8 or higher installed.
*   `pip` (Python package installer).

### Installation

1.  **Clone the Repository** (if applicable) or navigate to the project directory:
    ```bash
    cd ElectionScope
    ```

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**:
    Create a `.env` file in the project root directory and add your secret key:
    ```bash
    SECRET_KEY='your-secret-key-here'
    ```

5.  **Database Setup**:
    Initialize the database schema:
    ```bash
    python manage.py migrate
    ```

6.  **Import Legacy Data**:
    The project includes a custom management command to import data from the provided `bincom_test.sql` file.
    *   Ensure `bincom_test.sql` is in the project root directory.
    *   Run the import command:
    ```bash
    python manage.py import_legacy_db
    ```
    *This command parses the SQL dump, cleans the data, and populates the Django models.*

### Running the Application

1.  Start the development server:
    ```bash
    python manage.py runserver
    ```

2.  Open your web browser and visit:
    `http://127.0.0.1:8000`

## Usage Guide

*   **Home Page**: Dashboard with quick links to all main features.
*   **Navigation**: Use the top navigation bar to switch between views.
*   **Viewing Results**: Select your desired location (LGA/Ward) from the dropdowns. The application will automatically fetch the relevant sub-options.
*   **Adding Data**: Navigate to "Add Result", select the target polling unit, enter the scores for each party, and click "Save Results".

## Project Structure

*   `election_scope/`: Main Django project configuration settings.
*   `election_results/`: The core application.
    *   `models.py`: Database models matching the election data schema.
    *   `views.py`: Logic for processing requests and calculating results.
    *   `urls.py`: URL routing for the app.
    *   `templates/election_results/`: HTML templates for the UI.
    *   `management/commands/import_legacy_db.py`: Custom script for data import.
*   `bincom_test.sql`: Source SQL data file.
*   `db.sqlite3`: The local database file.
*   `manage.py`: Django's command-line utility.

## License
This project is for educational and assessment purposes.

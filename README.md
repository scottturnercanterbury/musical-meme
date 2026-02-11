# Musical Meme - Payroll Management System

A simple Flask-based payroll management application for managing employee records with salary tracking.

## Features

- Add employee records with name and salary
- View employee details
- Edit employee information
- Delete employee records
- Currency formatting (GBP) for all salary displays

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/scottturnercanterbury/musical-meme.git
cd musical-meme
```

### 2. Create a Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Using in Visual Studio Code

### 1. Open the Project

- Open VS Code
- Select **File > Open Folder**
- Navigate to the cloned `musical-meme` directory

### 2. Create and Activate Virtual Environment in VS Code

- Open Terminal: **Ctrl+`** (backtick) or **View > Terminal**
- Run the appropriate command from step 2 above

### 3. Select Python Interpreter

- Press **Ctrl+Shift+P** (or **Cmd+Shift+P** on Mac)
- Type "Python: Select Interpreter"
- Choose the one in `./venv/bin/python` (or `./venv/Scripts/python` on Windows)

### 4. Install Dependencies

In the VS Code terminal:
```bash
pip install -r requirements.txt
```

### 5. Run the Application

**Option A: Run from Terminal**
```bash
python app.py
```

**Option B: Use Debug Configuration**
- Click on **Run and Debug** (or press **Ctrl+Shift+D**)
- Click **"Create a launch.json file"** if prompted
- Select **Python**
- Run the debugger:

Press **F5** to start debugging

### 6. Access the Application

- Open your browser and go to `http://localhost:5000`

## Project Structure

```
musical-meme/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── payroll.db            # SQLite database (auto-created)
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Employee list
│   ├── add.html          # Add employee form
│   ├── edit.html         # Edit employee form
│   └── view.html         # View employee details
└── README.md             # This file
```

## Database

The application uses SQLite with a simple schema:

- **employees** table:
  - `id`: Integer primary key (auto-increment)
  - `name`: Employee name (text)
  - `salary_gbp_pence`: Salary in pence (integer)

The database file (`payroll.db`) is created automatically on first run.

## Development Tips

- The app runs in debug mode by default, so changes to code will auto-reload
- The Flask secret key should be changed in production (set via `FLASK_SECRET_KEY` environment variable)
- All salary values are stored in pence (integer) to avoid floating-point precision issues

## Troubleshooting

**Port 5000 is already in use:**
```bash
# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Or change the port in app.py
app.run(debug=True, port=5001)
```

**ModuleNotFoundError: No module named 'flask'**
- Make sure your virtual environment is activated
- Verify Flask is installed: `pip list`
- Reinstall: `pip install -r requirements.txt`

**Python not found:**
- Ensure Python is installed: `python --version`
- On Linux/Mac, you may need to use `python3` instead of `python`

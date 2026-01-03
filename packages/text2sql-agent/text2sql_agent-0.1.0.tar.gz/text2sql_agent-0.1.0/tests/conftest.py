"""
Shared pytest fixtures for SQL Agent Toolkit tests

This conftest.py includes:
- Command line options for LLM provider, model, and database type
- HTML report configuration and formatting
- Database fixtures for testing (SQLite and PostgreSQL)
- LLM fixtures (Ollama, Groq, Google Gemini)
- Parametrized fixtures for cross-database/LLM testing
- Helper function for attaching evaluation results to HTML reports
"""
import pytest
import sqlite3
import os
from datetime import datetime
from sql_agent_toolkit import SQLAgent, JSONSerializableSQLDatabase

# Create test databases directory
TEST_DB_DIR = os.path.join(os.path.dirname(__file__), "test_databases")
os.makedirs(TEST_DB_DIR, exist_ok=True)


def pytest_addoption(parser):
    """Add command line options for pytest"""
    parser.addoption(
        "--llm",
        action="store",
        default="ollama",
        help="LLM provider to use: ollama, groq, openai, gemini, anthropic"
    )
    parser.addoption(
        "--model",
        action="store",
        default="mistral:7b",
        help="Model name for LLM provider"
    )
    parser.addoption(
        "--database",
        action="store",
        default="all",
        choices=["all", "sqlite", "postgres"],
        help="Database type to test: all, sqlite, or postgres"
    )
    parser.addoption(
        "--llm-provider",
        action="store",
        default="all",
        choices=["all", "ollama", "groq", "gemini", "openai", "anthropic"],
        help="LLM provider to test: all, ollama, groq, gemini, openai, or anthropic"
    )
    parser.addoption(
        "--generate-comparison",
        action="store_true",
        default=True,
        help="Generate comparison report after tests"
    )


def pytest_configure(config):
    """Configure pytest with metadata and HTML report settings"""
    # Ensure reports directory exists and set HTML report path
    reports_dir = os.path.join(os.getcwd(), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # Set default HTML report path if not specified
    if not config.getoption('htmlpath'):
        config.option.htmlpath = os.path.join(reports_dir, "evaluation_report.html")
    
    # Add metadata to HTML report
    config._metadata = {
        "LLM Provider": config.getoption("--llm"),
        "Model": config.getoption("--model"),
        "Test Run Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Project": "SQL Agent Toolkit",
        "Version": "0.1.0",
    }


def pytest_html_report_title(report):
    """Customize HTML report title"""
    report.title = "SQL Agent Toolkit - Evaluation Report"


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def sqlite_employees_db():
    """
    Create SQLite database with employee test data

    Stored in: tests/test_databases/test_employees.db

    Schema:
    - employees (id, name, department, salary, hire_date)
    - departments (id, name, budget, location)
    - projects (id, name, department_id, start_date, status)
    """
    db_path = os.path.join(TEST_DB_DIR, "test_employees.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create employees table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT,
        salary INTEGER,
        hire_date TEXT
    )
    ''')

    # Create departments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        budget INTEGER,
        location TEXT
    )
    ''')

    # Create projects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department_id INTEGER,
        start_date TEXT,
        status TEXT,
        FOREIGN KEY (department_id) REFERENCES departments(id)
    )
    ''')

    # Insert sample data
    # Departments
    departments = [
        (1, 'Engineering', 500000, 'Building A'),
        (2, 'Sales', 300000, 'Building B'),
        (3, 'Marketing', 250000, 'Building B'),
        (4, 'HR', 150000, 'Building C'),
    ]
    cursor.executemany('INSERT OR REPLACE INTO departments VALUES (?, ?, ?, ?)', departments)

    # Employees
    employees = [
        (1, 'Alice Johnson', 'Engineering', 95000, '2022-01-15'),
        (2, 'Bob Smith', 'Engineering', 105000, '2021-06-20'),
        (3, 'Carol Williams', 'Sales', 75000, '2023-03-10'),
        (4, 'David Brown', 'Sales', 82000, '2022-11-05'),
        (5, 'Eve Davis', 'Marketing', 68000, '2023-07-01'),
        (6, 'Frank Miller', 'Marketing', 71000, '2022-09-15'),
        (7, 'Grace Wilson', 'HR', 62000, '2023-02-20'),
        (8, 'Henry Moore', 'Engineering', 98000, '2021-12-01'),
        (9, 'Ivy Taylor', 'Sales', 79000, '2023-05-12'),
        (10, 'Jack Anderson', 'Engineering', 110000, '2020-08-30'),
    ]
    cursor.executemany('INSERT OR REPLACE INTO employees VALUES (?, ?, ?, ?, ?)', employees)

    # Projects
    projects = [
        (1, 'Mobile App Redesign', 1, '2024-01-15', 'Active'),
        (2, 'Q1 Sales Campaign', 2, '2024-02-01', 'Active'),
        (3, 'Brand Refresh', 3, '2024-01-10', 'Active'),
        (4, 'Employee Portal', 1, '2023-11-01', 'Completed'),
        (5, 'Customer Survey', 3, '2024-03-01', 'Planning'),
    ]
    cursor.executemany('INSERT OR REPLACE INTO projects VALUES (?, ?, ?, ?, ?)', projects)

    conn.commit()
    conn.close()

    # Return JSONSerializableSQLDatabase instance
    db = JSONSerializableSQLDatabase.from_uri(f"sqlite:///{db_path}")
    return db


@pytest.fixture
def google_llm():
    """
    Create Google Gemini LLM for testing

    Requires GOOGLE_API_KEY environment variable to be set.
    Tests using this fixture will be skipped if the API key is not available.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        pytest.skip("GOOGLE_API_KEY not set")

    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        temperature=0.1,
        google_api_key=api_key
    )


@pytest.fixture(scope="session")
def test_cases_path():
    """Path to test cases JSON file"""
    return os.path.join(
        os.path.dirname(__file__),
        'evaluations',
        'data',
        'employee_test_cases.json'
    )


@pytest.fixture(scope="session")
def medical_test_cases_path():
    """Path to medical test cases JSON file"""
    return os.path.join(
        os.path.dirname(__file__),
        'evaluations',
        'data',
        'medical_test_cases.json'
    )


@pytest.fixture(scope="session")
def ecommerce_test_cases_path():
    """Path to e-commerce test cases JSON file"""
    return os.path.join(
        os.path.dirname(__file__),
        'evaluations',
        'data',
        'ecommerce_test_cases.json'
    )


@pytest.fixture(scope="session")
def sqlite_medical_db():
    """
    Create SQLite database with medical test data

    Stored in: tests/test_databases/test_medical.db

    Schema:
    - patients (patient_id, name, age, gender, date_of_birth)
    - conditions (condition_id, patient_id, condition_type, diagnosis_date, severity)
    - appointments (appointment_id, patient_id, doctor_id, appointment_date, status)
    - doctors (doctor_id, name, specialty)
    - medications (medication_id, name, dosage)
    - prescriptions (prescription_id, patient_id, medication_id, prescribed_date, duration_days)
    """
    db_path = os.path.join(TEST_DB_DIR, "test_medical.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        date_of_birth TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conditions (
        condition_id INTEGER PRIMARY KEY,
        patient_id INTEGER,
        condition_type TEXT,
        diagnosis_date TEXT,
        severity TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        specialty TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INTEGER PRIMARY KEY,
        patient_id INTEGER,
        doctor_id INTEGER,
        appointment_date TEXT,
        status TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medications (
        medication_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        dosage TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prescriptions (
        prescription_id INTEGER PRIMARY KEY,
        patient_id INTEGER,
        medication_id INTEGER,
        prescribed_date TEXT,
        duration_days INTEGER,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (medication_id) REFERENCES medications(medication_id)
    )
    ''')

    # Insert sample data
    patients = [
        (1, 'John Doe', 45, 'M', '1979-03-15'),
        (2, 'Jane Smith', 62, 'F', '1962-07-22'),
        (3, 'Bob Johnson', 38, 'M', '1986-11-30'),
        (4, 'Alice Williams', 55, 'F', '1969-05-10'),
        (5, 'Charlie Brown', 70, 'M', '1954-01-25'),
    ]
    cursor.executemany('INSERT OR REPLACE INTO patients VALUES (?, ?, ?, ?, ?)', patients)

    conditions = [
        (1, 1, 'diabetes', '2020-05-10', 'moderate'),
        (2, 1, 'hypertension', '2019-03-15', 'mild'),
        (3, 2, 'hypertension', '2018-11-20', 'moderate'),
        (4, 3, 'asthma', '2015-07-05', 'mild'),
        (5, 4, 'diabetes', '2021-02-28', 'severe'),
        (6, 5, 'cardiovascular', '2017-09-12', 'severe'),
    ]
    cursor.executemany('INSERT OR REPLACE INTO conditions VALUES (?, ?, ?, ?, ?)', conditions)

    doctors = [
        (1, 'Dr. Sarah Martinez', 'Cardiology'),
        (2, 'Dr. James Lee', 'Endocrinology'),
        (3, 'Dr. Emily Chen', 'General Practice'),
    ]
    cursor.executemany('INSERT OR REPLACE INTO doctors VALUES (?, ?, ?)', doctors)

    appointments = [
        (1, 1, 2, '2024-12-15', 'Scheduled'),
        (2, 2, 1, '2024-12-10', 'Completed'),
        (3, 3, 3, '2024-12-20', 'Scheduled'),
        (4, 4, 2, '2024-11-25', 'Completed'),
        (5, 5, 1, '2024-12-05', 'Completed'),
    ]
    cursor.executemany('INSERT OR REPLACE INTO appointments VALUES (?, ?, ?, ?, ?)', appointments)

    medications = [
        (1, 'Metformin', '500mg'),
        (2, 'Lisinopril', '10mg'),
        (3, 'Albuterol', '90mcg'),
    ]
    cursor.executemany('INSERT OR REPLACE INTO medications VALUES (?, ?, ?)', medications)

    prescriptions = [
        (1, 1, 1, '2020-05-10', 90),
        (2, 1, 2, '2019-03-15', 90),
        (3, 2, 2, '2018-11-20', 90),
        (4, 3, 3, '2015-07-05', 30),
        (5, 4, 1, '2021-02-28', 90),
    ]
    cursor.executemany('INSERT OR REPLACE INTO prescriptions VALUES (?, ?, ?, ?, ?)', prescriptions)

    conn.commit()
    conn.close()

    db = JSONSerializableSQLDatabase.from_uri(f"sqlite:///{db_path}")
    return db


@pytest.fixture(scope="session")
def sqlite_ecommerce_db():
    """
    Create SQLite database with e-commerce test data

    Stored in: tests/test_databases/test_ecommerce.db

    Schema:
    - customers (customer_id, name, email, signup_date)
    - products (product_id, name, price, category_id)
    - categories (category_id, name)
    - orders (order_id, customer_id, order_date, total_amount, status)
    - order_items (order_item_id, order_id, product_id, quantity, price)
    - inventory (inventory_id, product_id, stock_quantity)
    """
    db_path = os.path.join(TEST_DB_DIR, "test_ecommerce.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        signup_date TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TEXT,
        total_amount REAL,
        status TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price REAL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        inventory_id INTEGER PRIMARY KEY,
        product_id INTEGER,
        stock_quantity INTEGER,
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    ''')

    # Insert sample data
    customers = [
        (1, 'Michael Scott', 'mscott@example.com', '2023-01-15'),
        (2, 'Pam Beesly', 'pbeesly@example.com', '2023-02-20'),
        (3, 'Jim Halpert', 'jhalpert@example.com', '2023-03-10'),
        (4, 'Dwight Schrute', 'dschrute@example.com', '2023-04-05'),
        (5, 'Stanley Hudson', 'shudson@example.com', '2023-05-12'),
    ]
    cursor.executemany('INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?)', customers)

    categories = [
        (1, 'Electronics'),
        (2, 'Clothing'),
        (3, 'Books'),
        (4, 'Home & Garden'),
    ]
    cursor.executemany('INSERT OR REPLACE INTO categories VALUES (?, ?)', categories)

    products = [
        (1, 'Laptop', 999.99, 1),
        (2, 'Smartphone', 699.99, 1),
        (3, 'T-Shirt', 19.99, 2),
        (4, 'Jeans', 49.99, 2),
        (5, 'Python Programming Book', 39.99, 3),
        (6, 'Garden Tools Set', 79.99, 4),
        (7, 'Wireless Mouse', 29.99, 1),
        (8, 'Coffee Maker', 89.99, 4),
    ]
    cursor.executemany('INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?)', products)

    orders = [
        (1, 1, '2024-11-01', 1049.98, 'Completed'),
        (2, 2, '2024-11-05', 69.98, 'Completed'),
        (3, 3, '2024-11-10', 699.99, 'Shipped'),
        (4, 4, '2024-11-15', 159.96, 'Completed'),
        (5, 1, '2024-11-20', 89.99, 'Processing'),
        (6, 5, '2024-11-25', 39.99, 'Completed'),
    ]
    cursor.executemany('INSERT OR REPLACE INTO orders VALUES (?, ?, ?, ?, ?)', orders)

    order_items = [
        (1, 1, 1, 1, 999.99),
        (2, 1, 7, 1, 29.99),
        (3, 2, 3, 2, 19.99),
        (4, 2, 7, 1, 29.99),
        (5, 3, 2, 1, 699.99),
        (6, 4, 4, 2, 49.99),
        (7, 4, 3, 3, 19.99),
        (8, 5, 8, 1, 89.99),
        (9, 6, 5, 1, 39.99),
    ]
    cursor.executemany('INSERT OR REPLACE INTO order_items VALUES (?, ?, ?, ?, ?)', order_items)

    inventory = [
        (1, 1, 15),
        (2, 2, 25),
        (3, 3, 100),
        (4, 4, 50),
        (5, 5, 30),
        (6, 6, 8),
        (7, 7, 45),
        (8, 8, 12),
    ]
    cursor.executemany('INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)', inventory)

    conn.commit()
    conn.close()

    db = JSONSerializableSQLDatabase.from_uri(f"sqlite:///{db_path}")
    return db


# ============================================================================
# POSTGRESQL DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def postgres_employees_db():
    """
    PostgreSQL employees database fixture

    Requires DATABASE_URL_POSTGRES environment variable.
    Creates tables and inserts same data as sqlite_employees_db.

    Example: postgresql://user:password@localhost:5432/test_employees
    """
    db_url = os.getenv("DATABASE_URL_POSTGRES")
    if not db_url:
        pytest.skip("DATABASE_URL_POSTGRES not set")

    db = JSONSerializableSQLDatabase.from_uri(db_url)

    # Get raw connection to create tables
    from sqlalchemy import text

    with db._engine.connect() as conn:
        # Drop existing tables (for clean slate)
        conn.execute(text("DROP TABLE IF EXISTS projects CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS employees CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS departments CASCADE"))
        conn.commit()

        # Create departments table
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            budget INTEGER,
            location TEXT
        )
        '''))

        # Create employees table
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            salary INTEGER,
            hire_date TEXT
        )
        '''))

        # Create projects table
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department_id INTEGER,
            start_date TEXT,
            status TEXT,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
        '''))

        # Insert sample data - Departments
        departments = [
            (1, 'Engineering', 500000, 'Building A'),
            (2, 'Sales', 300000, 'Building B'),
            (3, 'Marketing', 250000, 'Building B'),
            (4, 'HR', 150000, 'Building C'),
        ]
        for dept in departments:
            conn.execute(text(
                "INSERT INTO departments (id, name, budget, location) VALUES (:id, :name, :budget, :location)"
            ), {"id": dept[0], "name": dept[1], "budget": dept[2], "location": dept[3]})

        # Employees
        employees = [
            (1, 'Alice Johnson', 'Engineering', 95000, '2022-01-15'),
            (2, 'Bob Smith', 'Engineering', 105000, '2021-06-20'),
            (3, 'Carol Williams', 'Sales', 75000, '2023-03-10'),
            (4, 'David Brown', 'Sales', 82000, '2022-11-05'),
            (5, 'Eve Davis', 'Marketing', 68000, '2023-07-01'),
            (6, 'Frank Miller', 'Marketing', 71000, '2022-09-15'),
            (7, 'Grace Wilson', 'HR', 62000, '2023-02-20'),
            (8, 'Henry Moore', 'Engineering', 98000, '2021-12-01'),
            (9, 'Ivy Taylor', 'Sales', 79000, '2023-05-12'),
            (10, 'Jack Anderson', 'Engineering', 110000, '2020-08-30'),
        ]
        for emp in employees:
            conn.execute(text(
                "INSERT INTO employees (id, name, department, salary, hire_date) VALUES (:id, :name, :dept, :salary, :hire_date)"
            ), {"id": emp[0], "name": emp[1], "dept": emp[2], "salary": emp[3], "hire_date": emp[4]})

        # Projects
        projects = [
            (1, 'Mobile App Redesign', 1, '2024-01-15', 'Active'),
            (2, 'Q1 Sales Campaign', 2, '2024-02-01', 'Active'),
            (3, 'Brand Refresh', 3, '2024-01-10', 'Active'),
            (4, 'Employee Portal', 1, '2023-11-01', 'Completed'),
            (5, 'Customer Survey', 3, '2024-03-01', 'Planning'),
        ]
        for proj in projects:
            conn.execute(text(
                "INSERT INTO projects (id, name, department_id, start_date, status) VALUES (:id, :name, :dept_id, :start_date, :status)"
            ), {"id": proj[0], "name": proj[1], "dept_id": proj[2], "start_date": proj[3], "status": proj[4]})

        conn.commit()

    yield db

    # Cleanup: Drop tables after tests
    with db._engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS projects CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS employees CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS departments CASCADE"))
        conn.commit()


# ============================================================================
# LLM FIXTURES
# ============================================================================

@pytest.fixture
def ollama_llm():
    """
    Create Ollama LLM for testing

    Uses mistral:7b model by default.
    Requires Ollama to be running locally.
    """
    from langchain_ollama import ChatOllama

    return ChatOllama(model="mistral:7b", temperature=0.1)


@pytest.fixture
def groq_llm():
    """
    Create Groq LLM for testing

    Requires GROQ_API_KEY environment variable to be set.
    Tests using this fixture will be skipped if the API key is not available.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        pytest.skip("GROQ_API_KEY not set")

    from langchain_groq import ChatGroq

    return ChatGroq(
        model="llama-3.1-70b-versatile",
        temperature=0.1,
        api_key=api_key
    )

@pytest.fixture(scope="session")
def postgres_medical_db():
    """PostgreSQL medical database fixture
    
    Requires DATABASE_URL_POSTGRES_MEDICAL or DATABASE_URL_POSTGRES environment variable.
    Creates tables and inserts same data as sqlite_medical_db.
    """
    db_url = os.getenv("DATABASE_URL_POSTGRES_MEDICAL") or os.getenv("DATABASE_URL_POSTGRES")
    if not db_url:
        pytest.skip("DATABASE_URL_POSTGRES_MEDICAL or DATABASE_URL_POSTGRES not set")
    
    db = JSONSerializableSQLDatabase.from_uri(db_url)
    from sqlalchemy import text
    
    with db._engine.connect() as conn:
        # Drop existing tables
        for table in ["prescriptions", "medications", "appointments", "doctors", "conditions", "patients"]:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
        conn.commit()
        
        # Create tables (same structure as SQLite)
        tables_sql = [
            """CREATE TABLE IF NOT EXISTS patients (
                patient_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                date_of_birth TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS conditions (
                condition_id INTEGER PRIMARY KEY,
                patient_id INTEGER,
                condition_type TEXT,
                diagnosis_date TEXT,
                severity TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )""",
            """CREATE TABLE IF NOT EXISTS doctors (
                doctor_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                specialty TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INTEGER PRIMARY KEY,
                patient_id INTEGER,
                doctor_id INTEGER,
                appointment_date TEXT,
                status TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
            )""",
            """CREATE TABLE IF NOT EXISTS medications (
                medication_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                dosage TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS prescriptions (
                prescription_id INTEGER PRIMARY KEY,
                patient_id INTEGER,
                medication_id INTEGER,
                prescribed_date TEXT,
                duration_days INTEGER,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (medication_id) REFERENCES medications(medication_id)
            )"""
        ]
        
        for sql in tables_sql:
            conn.execute(text(sql))
        
        # Insert sample data
        patients = [
            (1, 'John Doe', 45, 'M', '1979-03-15'),
            (2, 'Jane Smith', 62, 'F', '1962-07-22'),
            (3, 'Bob Johnson', 38, 'M', '1986-11-30'),
            (4, 'Alice Williams', 55, 'F', '1969-05-10'),
            (5, 'Charlie Brown', 70, 'M', '1954-01-25'),
        ]
        for p in patients:
            conn.execute(text("INSERT INTO patients VALUES (:id, :name, :age, :gender, :dob)"),
                        {"id": p[0], "name": p[1], "age": p[2], "gender": p[3], "dob": p[4]})
        
        conditions = [
            (1, 1, 'diabetes', '2020-05-10', 'moderate'),
            (2, 1, 'hypertension', '2019-03-15', 'mild'),
            (3, 2, 'hypertension', '2018-11-20', 'moderate'),
            (4, 3, 'asthma', '2015-07-05', 'mild'),
            (5, 4, 'diabetes', '2021-02-28', 'severe'),
            (6, 5, 'cardiovascular', '2017-09-12', 'severe'),
        ]
        for c in conditions:
            conn.execute(text("INSERT INTO conditions VALUES (:id, :pid, :type, :date, :sev)"),
                        {"id": c[0], "pid": c[1], "type": c[2], "date": c[3], "sev": c[4]})
        
        doctors = [
            (1, 'Dr. Sarah Martinez', 'Cardiology'),
            (2, 'Dr. James Lee', 'Endocrinology'),
            (3, 'Dr. Emily Chen', 'General Practice'),
        ]
        for d in doctors:
            conn.execute(text("INSERT INTO doctors VALUES (:id, :name, :spec)"),
                        {"id": d[0], "name": d[1], "spec": d[2]})
        
        appointments = [
            (1, 1, 2, '2024-12-15', 'Scheduled'),
            (2, 2, 1, '2024-12-10', 'Completed'),
            (3, 3, 3, '2024-12-20', 'Scheduled'),
            (4, 4, 2, '2024-11-25', 'Completed'),
            (5, 5, 1, '2024-12-05', 'Completed'),
        ]
        for a in appointments:
            conn.execute(text("INSERT INTO appointments VALUES (:id, :pid, :did, :date, :status)"),
                        {"id": a[0], "pid": a[1], "did": a[2], "date": a[3], "status": a[4]})
        
        medications = [
            (1, 'Metformin', '500mg'),
            (2, 'Lisinopril', '10mg'),
            (3, 'Albuterol', '90mcg'),
        ]
        for m in medications:
            conn.execute(text("INSERT INTO medications VALUES (:id, :name, :dosage)"),
                        {"id": m[0], "name": m[1], "dosage": m[2]})
        
        prescriptions = [
            (1, 1, 1, '2020-05-10', 90),
            (2, 1, 2, '2019-03-15', 90),
            (3, 2, 2, '2018-11-20', 90),
            (4, 3, 3, '2015-07-05', 30),
            (5, 4, 1, '2021-02-28', 90),
        ]
        for p in prescriptions:
            conn.execute(text("INSERT INTO prescriptions VALUES (:id, :pid, :mid, :date, :dur)"),
                        {"id": p[0], "pid": p[1], "mid": p[2], "date": p[3], "dur": p[4]})
        
        conn.commit()
    
    yield db
    
    # Cleanup
    with db._engine.connect() as conn:
        for table in ["prescriptions", "medications", "appointments", "doctors", "conditions", "patients"]:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
        conn.commit()


@pytest.fixture(scope="session")
def postgres_ecommerce_db():
    """PostgreSQL e-commerce database fixture
    
    Requires DATABASE_URL_POSTGRES_ECOMMERCE or DATABASE_URL_POSTGRES environment variable.
    Creates tables and inserts same data as sqlite_ecommerce_db.
    """
    db_url = os.getenv("DATABASE_URL_POSTGRES_ECOMMERCE") or os.getenv("DATABASE_URL_POSTGRES")
    if not db_url:
        pytest.skip("DATABASE_URL_POSTGRES_ECOMMERCE or DATABASE_URL_POSTGRES not set")
    
    db = JSONSerializableSQLDatabase.from_uri(db_url)
    from sqlalchemy import text
    
    with db._engine.connect() as conn:
        # Drop existing tables
        for table in ["inventory", "order_items", "orders", "products", "categories", "customers"]:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
        conn.commit()
        
        # Create tables
        tables_sql = [
            """CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                signup_date TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )""",
            """CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                order_date TEXT,
                total_amount REAL,
                status TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )""",
            """CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INTEGER PRIMARY KEY,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                price REAL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )""",
            """CREATE TABLE IF NOT EXISTS inventory (
                inventory_id INTEGER PRIMARY KEY,
                product_id INTEGER,
                stock_quantity INTEGER,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )"""
        ]
        
        for sql in tables_sql:
            conn.execute(text(sql))
        
        # Insert sample data
        customers = [
            (1, 'Michael Scott', 'mscott@example.com', '2023-01-15'),
            (2, 'Pam Beesly', 'pbeesly@example.com', '2023-02-20'),
            (3, 'Jim Halpert', 'jhalpert@example.com', '2023-03-10'),
            (4, 'Dwight Schrute', 'dschrute@example.com', '2023-04-05'),
            (5, 'Stanley Hudson', 'shudson@example.com', '2023-05-12'),
        ]
        for c in customers:
            conn.execute(text("INSERT INTO customers VALUES (:id, :name, :email, :date)"),
                        {"id": c[0], "name": c[1], "email": c[2], "date": c[3]})
        
        categories = [
            (1, 'Electronics'),
            (2, 'Clothing'),
            (3, 'Books'),
            (4, 'Home & Garden'),
        ]
        for cat in categories:
            conn.execute(text("INSERT INTO categories VALUES (:id, :name)"),
                        {"id": cat[0], "name": cat[1]})
        
        products = [
            (1, 'Laptop', 999.99, 1),
            (2, 'Smartphone', 699.99, 1),
            (3, 'T-Shirt', 19.99, 2),
            (4, 'Jeans', 49.99, 2),
            (5, 'Python Programming Book', 39.99, 3),
            (6, 'Garden Tools Set', 79.99, 4),
            (7, 'Wireless Mouse', 29.99, 1),
            (8, 'Coffee Maker', 89.99, 4),
        ]
        for p in products:
            conn.execute(text("INSERT INTO products VALUES (:id, :name, :price, :cat_id)"),
                        {"id": p[0], "name": p[1], "price": p[2], "cat_id": p[3]})
        
        orders = [
            (1, 1, '2024-11-01', 1049.98, 'Completed'),
            (2, 2, '2024-11-05', 69.98, 'Completed'),
            (3, 3, '2024-11-10', 699.99, 'Shipped'),
            (4, 4, '2024-11-15', 159.96, 'Completed'),
            (5, 1, '2024-11-20', 89.99, 'Processing'),
            (6, 5, '2024-11-25', 39.99, 'Completed'),
        ]
        for o in orders:
            conn.execute(text("INSERT INTO orders VALUES (:id, :cid, :date, :amount, :status)"),
                        {"id": o[0], "cid": o[1], "date": o[2], "amount": o[3], "status": o[4]})
        
        order_items = [
            (1, 1, 1, 1, 999.99),
            (2, 1, 7, 1, 29.99),
            (3, 2, 3, 2, 19.99),
            (4, 2, 7, 1, 29.99),
            (5, 3, 2, 1, 699.99),
            (6, 4, 4, 2, 49.99),
            (7, 4, 3, 3, 19.99),
            (8, 5, 8, 1, 89.99),
            (9, 6, 5, 1, 39.99),
        ]
        for item in order_items:
            conn.execute(text("INSERT INTO order_items VALUES (:id, :oid, :pid, :qty, :price)"),
                        {"id": item[0], "oid": item[1], "pid": item[2], "qty": item[3], "price": item[4]})
        
        inventory = [
            (1, 1, 15),
            (2, 2, 25),
            (3, 3, 100),
            (4, 4, 50),
            (5, 5, 30),
            (6, 6, 8),
            (7, 7, 45),
            (8, 8, 12),
        ]
        for inv in inventory:
            conn.execute(text("INSERT INTO inventory VALUES (:id, :pid, :qty)"),
                        {"id": inv[0], "pid": inv[1], "qty": inv[2]})
        
        conn.commit()
    
    yield db
    
    # Cleanup
    with db._engine.connect() as conn:
        for table in ["inventory", "order_items", "orders", "products", "categories", "customers"]:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
        conn.commit()


# ============================================================================
# PYTEST HOOKS FOR COMPARISON REPORT GENERATION
# ============================================================================

def pytest_sessionfinish(session, exitstatus):
    """
    Generate comparison report after all tests complete

    This hook is called after all tests have been executed and the session
    is about to end. It generates an HTML comparison report showing results
    across different database and LLM combinations.
    """
    # Skip if running in xdist worker process
    if hasattr(session.config, 'workerinput'):
        return

    # Check if comparison report generation is enabled
    if not session.config.getoption("--generate-comparison"):
        return

    try:
        from .comparison_report import generate_comparison_report

        # Generate the comparison report
        report_path = generate_comparison_report(session)

        if report_path:
            print(f"\n\n{'='*80}")
            print("📊 Comparison Report Generated")
            print(f"{'='*80}")
            print(f"Location: {report_path}")
            print(f"{'='*80}\n")

    except Exception as e:
        print(f"\nWarning: Could not generate comparison report: {e}")
        import traceback
        traceback.print_exc()

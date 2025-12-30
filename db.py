"""
Database Module for Employee Management System

This file handles all database operations like:
- Connecting to the database
- Creating new employees
- Reading employee information
- Updating employee details
- Deleting employees

Think of this as the "librarian" that helps us save and find employee information!
"""

import os
import psycopg
from psycopg.rows import dict_row
from typing import List, Optional, Dict, Any
import traceback
import logging

# Set up logging to help us see what's happening
# Logging is like a diary that writes down everything the program does
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get database connection URL from environment variable
# This is like the address of our database "house"
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://neondb_owner:npg_36MaJuyTbScI@ep-weathered-unit-ahc8hg3u-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require'
)

logger.info("📚 Database module loaded successfully!")
logger.info(f"🔗 Database URL configured (host hidden for security)")


def get_connection():
    """
    Get a connection to the database

    Think of this like opening a door to the database room.
    We need to open the door before we can look at or change anything inside!

    Returns:
        A connection object that lets us talk to the database
    """
    try:
        logger.info("🚪 Opening connection to database...")
        conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        logger.info("✅ Database connection opened successfully!")
        return conn
    except Exception as e:
        logger.error("❌ OOPS! Could not connect to database!")
        logger.error(f"   Error message: {str(e)}")
        logger.error(f"   Full error details:\n{traceback.format_exc()}")
        raise


def init_db():
    """
    Initialize the database and create the employees table if it doesn't exist

    This is like building a filing cabinet with different drawers for employee info:
    - Drawer 1: Employee ID (their unique number)
    - Drawer 2: Name
    - Drawer 3: Email
    - Drawer 4: Position (like "Teacher" or "Manager")
    - Drawer 5: Department (like "Sales" or "Engineering")
    - Drawer 6: Picture URL (web address where their photo is stored)
    - Drawer 7: Resume URL (web address where their resume is stored)
    - Drawer 8: When they were added to the system
    """
    try:
        logger.info("🏗️  Starting database initialization...")
        logger.info("   This will create the employees table if it doesn't exist")

        conn = get_connection()
        cursor = conn.cursor()

        logger.info("📝 Creating employees table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                position VARCHAR(255),
                department VARCHAR(255),
                picture_url TEXT,
                resume_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        logger.info("✅ Employees table is ready!")

        cursor.close()
        conn.close()
        logger.info("🚪 Database connection closed")

    except Exception as e:
        logger.error("❌ OOPS! Something went wrong while setting up the database!")
        logger.error(f"   Error message: {str(e)}")
        logger.error(f"   Full error details:\n{traceback.format_exc()}")
        raise


def create_employee(employee_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new employee in the database

    This is like filling out a new employee card and putting it in the filing cabinet.

    Args:
        employee_data: A dictionary with employee information like:
            - name: The employee's name
            - email: Their email address
            - position: Their job title
            - department: Which department they work in
            - picture_url: Web address of their photo
            - resume_url: Web address of their resume

    Returns:
        A dictionary with all the employee information, including their new ID number
    """
    try:
        logger.info("➕ Creating a new employee...")
        logger.info(f"   Employee name: {employee_data.get('name', 'Unknown')}")
        logger.info(f"   Employee email: {employee_data.get('email', 'Unknown')}")
        logger.info(f"   Position: {employee_data.get('position', 'Not specified')}")
        logger.info(f"   Department: {employee_data.get('department', 'Not specified')}")

        conn = get_connection()
        cursor = conn.cursor()

        logger.info("💾 Saving employee to database...")
        cursor.execute("""
            INSERT INTO employees (name, email, position, department, picture_url, resume_url)
            VALUES (%(name)s, %(email)s, %(position)s, %(department)s, %(picture_url)s, %(resume_url)s)
            RETURNING *
        """, employee_data)

        employee = cursor.fetchone()
        conn.commit()

        logger.info(f"✅ Employee created successfully with ID: {employee['id']}")

        cursor.close()
        conn.close()
        logger.info("🚪 Database connection closed")

        return employee

    except Exception as e:
        logger.error("❌ OOPS! Could not create the employee!")
        logger.error(f"   Error message: {str(e)}")
        logger.error(f"   Employee data that failed: {employee_data}")
        logger.error(f"   Full error details:\n{traceback.format_exc()}")
        raise


def get_all_employees() -> List[Dict[str, Any]]:
    """
    Get all employees from the database

    This is like opening the filing cabinet and looking at ALL employee cards.
    We'll get them in reverse order (newest employees first).

    Returns:
        A list of dictionaries, where each dictionary is one employee's information
    """
    try:
        logger.info("📋 Getting all employees from database...")

        conn = get_connection()
        cursor = conn.cursor()

        logger.info("🔍 Searching for employees (newest first)...")
        cursor.execute("SELECT * FROM employees ORDER BY id DESC")
        employees = cursor.fetchall()

        logger.info(f"✅ Found {len(employees)} employee(s) in the database!")

        cursor.close()
        conn.close()
        logger.info("🚪 Database connection closed")

        return employees

    except Exception as e:
        logger.error("❌ OOPS! Could not get employees from database!")
        logger.error(f"   Error message: {str(e)}")
        logger.error(f"   Full error details:\n{traceback.format_exc()}")
        raise


def get_employee(employee_id: int) -> Optional[Dict[str, Any]]:
    """
    Get one specific employee by their ID number

    This is like looking for one specific employee card in the filing cabinet.

    Args:
        employee_id: The unique ID number of the employee we're looking for

    Returns:
        A dictionary with the employee's information, or None if not found
    """
    try:
        logger.info(f"🔍 Looking for employee with ID: {employee_id}...")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM employees WHERE id = %s", (employee_id,))
        employee = cursor.fetchone()

        if employee:
            logger.info(f"✅ Found employee: {employee['name']}")
        else:
            logger.warning(f"⚠️  Could not find employee with ID: {employee_id}")

        cursor.close()
        conn.close()
        logger.info("🚪 Database connection closed")

        return employee if employee else None

    except Exception as e:
        logger.error(f"❌ OOPS! Error while looking for employee ID {employee_id}!")
        logger.error(f"   Error message: {str(e)}")
        logger.error(f"   Full error details:\n{traceback.format_exc()}")
        raise


def update_employee(employee_id: int, employee_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update an existing employee's information

    This is like taking out an employee card, erasing some info, and writing new info.

    Args:
        employee_id: The ID number of the employee to update
        employee_data: A dictionary with the new information

    Returns:
        A dictionary with the updated employee information, or None if employee not found
    """
    try:
        logger.info(f"✏️  Updating employee with ID: {employee_id}...")
        logger.info(f"   New name: {employee_data.get('name', 'Not changing')}")
        logger.info(f"   New email: {employee_data.get('email', 'Not changing')}")
        logger.info(f"   New position: {employee_data.get('position', 'Not changing')}")
        logger.info(f"   New department: {employee_data.get('department', 'Not changing')}")

        conn = get_connection()
        cursor = conn.cursor()

        logger.info("💾 Saving updated information to database...")
        cursor.execute("""
            UPDATE employees
            SET name = %(name)s,
                email = %(email)s,
                position = %(position)s,
                department = %(department)s,
                picture_url = COALESCE(%(picture_url)s, picture_url),
                resume_url = COALESCE(%(resume_url)s, resume_url)
            WHERE id = %(id)s
            RETURNING *
        """, {**employee_data, 'id': employee_id})

        employee = cursor.fetchone()
        conn.commit()

        if employee:
            logger.info(f"✅ Employee {employee_id} updated successfully!")
        else:
            logger.warning(f"⚠️  Could not find employee with ID {employee_id} to update")

        cursor.close()
        conn.close()
        logger.info("🚪 Database connection closed")

        return employee if employee else None

    except Exception as e:
        logger.error(f"❌ OOPS! Could not update employee ID {employee_id}!")
        logger.error(f"   Error message: {str(e)}")
        logger.error(f"   Data that failed: {employee_data}")
        logger.error(f"   Full error details:\n{traceback.format_exc()}")
        raise


def delete_employee(employee_id: int) -> bool:
    """
    Delete an employee from the database

    This is like taking an employee card out of the filing cabinet and throwing it away.
    Be careful - once deleted, it's gone forever!

    Args:
        employee_id: The ID number of the employee to delete

    Returns:
        True if the employee was deleted, False if employee was not found
    """
    try:
        logger.info(f"🗑️  Deleting employee with ID: {employee_id}...")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM employees WHERE id = %s RETURNING id", (employee_id,))
        deleted = cursor.fetchone()

        conn.commit()

        if deleted:
            logger.info(f"✅ Employee {employee_id} deleted successfully!")
        else:
            logger.warning(f"⚠️  Could not find employee with ID {employee_id} to delete")

        cursor.close()
        conn.close()
        logger.info("🚪 Database connection closed")

        return deleted is not None

    except Exception as e:
        logger.error(f"❌ OOPS! Could not delete employee ID {employee_id}!")
        logger.error(f"   Error message: {str(e)}")
        logger.error(f"   Full error details:\n{traceback.format_exc()}")
        raise


# When this file is loaded, log a message
logger.info("=" * 60)
logger.info("📚 Database module is ready to use!")
logger.info("=" * 60)

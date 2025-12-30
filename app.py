"""
FastAPI Backend for Employee Management System

This file is the "brain" of our web application! It handles all the requests
from the web browser and talks to the database.

Think of it like a restaurant waiter:
- Takes orders from customers (web browser)
- Brings those orders to the kitchen (database)
- Brings back the food (data) to the customers

Main things this file does:
1. Serve the website (index.html)
2. Create new employees
3. Get employee information
4. Update employee information
5. Delete employees
6. Upload files (pictures and resumes) to cloud storage
"""

import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
import db
import auth
import logging
import traceback

# Set up logging - like keeping a journal of everything that happens!
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("🚀 Starting Employee Management System Backend!")
logger.info("=" * 60)

# Create our FastAPI application
# This is like opening our restaurant for business!
app = FastAPI(title="Employee Management System", version="1.0.0")

logger.info("✅ FastAPI application created")

# CORS middleware - allows our website to talk to our backend
# CORS is like a security guard that checks if websites are allowed to talk to us
logger.info("🔒 Setting up CORS (Cross-Origin Resource Sharing)...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all websites (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers
)
logger.info("✅ CORS middleware configured")


# Initialize database when the application starts
@app.on_event("startup")
async def startup_event():
    """
    This runs when the application starts up
    It's like preparing the restaurant before opening!
    """
    logger.info("🏁 Application startup event triggered")
    logger.info("📚 Initializing database...")
    try:
        db.init_db()
        logger.info("✅ Database initialized successfully!")
    except Exception as e:
        logger.error("❌ OOPS! Failed to initialize database!")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Full details:\n{traceback.format_exc()}")
        raise


# Pydantic models - these are like forms that describe what data should look like
class EmployeeBase(BaseModel):
    """
    This describes what information we need for an employee
    Like a template for an employee card!
    """
    name: str  # Employee's name (required)
    email: EmailStr  # Employee's email (required, must be valid email format)
    position: Optional[str] = None  # Job title (optional)
    department: Optional[str] = None  # Which department (optional)


class EmployeeResponse(EmployeeBase):
    """
    This describes what we send back to the browser
    It includes everything from EmployeeBase plus extra info!
    """
    id: int  # The employee's unique ID number
    picture_url: Optional[str] = None  # Web address of their picture
    resume_url: Optional[str] = None  # Web address of their resume


# Authentication models
class RequestPinRequest(BaseModel):
    """Request to send a PIN to an email"""
    email: EmailStr


class VerifyPinRequest(BaseModel):
    """Request to verify a PIN"""
    email: EmailStr
    pin: str


# Dependency to verify authentication token
async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """
    Verify the user's access token

    Like checking someone's ID card at the door!
    If they have a valid token, we let them in.
    If not, we send them back to login.
    """
    if not authorization:
        logger.warning("⚠️  No authorization header provided")
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please login first."
        )

    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        logger.warning("⚠️  Invalid authorization header format")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication format"
        )

    # Verify the token
    email = auth.verify_token(token)
    if not email:
        logger.warning("❌ Invalid or expired token")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token. Please login again."
        )

    logger.info(f"✅ User authenticated: {email}")
    return email


# Vercel Blob upload function
async def upload_to_vercel_blob(file: UploadFile, token: str) -> str:
    """
    Upload a file to Vercel Blob Storage (cloud storage)

    This is like taking a photo or document and storing it in a special online filing cabinet!

    Args:
        file: The file to upload (picture or PDF)
        token: Secret password to access the cloud storage

    Returns:
        The web address (URL) where the file is now stored
    """
    try:
        logger.info(f"☁️  Uploading file to Vercel Blob Storage...")
        logger.info(f"   File name: {file.filename}")
        logger.info(f"   File type: {file.content_type}")

        # Read the file contents (like opening an envelope to see what's inside)
        file_content = await file.read()
        file_size = len(file_content)
        logger.info(f"   File size: {file_size} bytes ({file_size / 1024:.2f} KB)")

        # Upload to Vercel Blob Storage
        logger.info(f"   Sending file to cloud storage...")
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"https://blob.vercel-storage.com/{file.filename}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "x-content-type": file.content_type or "application/octet-stream"
                },
                content=file_content,
                timeout=30.0  # Wait up to 30 seconds
            )

            logger.info(f"   Upload response status: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"❌ File upload failed!")
                logger.error(f"   Status code: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                raise HTTPException(status_code=500, detail="File upload failed")

            result = response.json()
            uploaded_url = result.get("url", "")

            logger.info(f"✅ File uploaded successfully!")
            logger.info(f"   File URL: {uploaded_url}")

            return uploaded_url

    except Exception as e:
        logger.error(f"❌ OOPS! Error uploading file!")
        logger.error(f"   File name: {file.filename if file else 'Unknown'}")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Full details:\n{traceback.format_exc()}")
        raise


# === API ROUTES ===
# These are like different menu items at our restaurant!


@app.get("/")
async def read_root():
    """
    Serve the main webpage (index.html)

    When someone visits our website, this sends them the HTML page
    Like giving a customer a menu when they sit down!
    """
    logger.info("🏠 Someone requested the homepage!")
    logger.info("   Sending index.html file...")
    return FileResponse("index.html")


# === AUTHENTICATION ROUTES ===
# These handle login and security!


@app.post("/api/auth/request-pin")
async def request_pin(request: RequestPinRequest):
    """
    Request a PIN to be sent to an email address

    This is Step 1 of login:
    - User enters their email
    - We generate a random PIN
    - We send the PIN to their email
    - They can then use that PIN to login
    """
    logger.info("=" * 60)
    logger.info("📧 REQUEST PIN")
    logger.info("=" * 60)
    logger.info(f"   Email: {request.email}")

    try:
        # Clean up old expired PINs first
        auth.cleanup_expired_pins()

        # Generate a new PIN
        pin = auth.generate_pin()

        # Store the PIN
        auth.store_pin(request.email, pin)

        # Send PIN via email
        email_sent = auth.send_pin_email(request.email, pin)

        if email_sent:
            logger.info("✅ PIN generated and sent successfully")
            logger.info("=" * 60)
            return {
                "success": True,
                "message": f"PIN sent to {request.email}. Please check your email (and spam folder)."
            }
        else:
            logger.error("❌ Failed to send PIN email")
            logger.info("=" * 60)
            raise HTTPException(
                status_code=500,
                detail="Failed to send PIN. Please try again."
            )

    except Exception as e:
        logger.error(f"❌ Error requesting PIN: {str(e)}")
        logger.error(f"   Full details:\n{traceback.format_exc()}")
        logger.info("=" * 60)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/verify-pin")
async def verify_pin(request: VerifyPinRequest):
    """
    Verify a PIN and log the user in

    This is Step 2 of login:
    - User enters the PIN they received in email
    - We check if it matches what we sent
    - If correct, we give them an access token (like a key card)
    - They can use this token to access the employee forms
    """
    logger.info("=" * 60)
    logger.info("🔐 VERIFY PIN")
    logger.info("=" * 60)
    logger.info(f"   Email: {request.email}")

    try:
        # Verify the PIN
        is_valid = auth.verify_pin(request.email, request.pin)

        if is_valid:
            # Generate access token
            access_token = auth.create_access_token(request.email)

            logger.info("✅ PIN verified - User logged in successfully!")
            logger.info("=" * 60)

            return {
                "success": True,
                "message": "Login successful!",
                "access_token": access_token,
                "token_type": "bearer",
                "email": request.email
            }
        else:
            logger.warning("❌ Invalid or expired PIN")
            logger.info("=" * 60)
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired PIN. Please request a new PIN."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error verifying PIN: {str(e)}")
        logger.error(f"   Full details:\n{traceback.format_exc()}")
        logger.info("=" * 60)
        raise HTTPException(status_code=500, detail=str(e))


# === EMPLOYEE ROUTES ===
# These handle employee management (protected by authentication)


@app.post("/api/employees", response_model=EmployeeResponse)
async def create_employee(
    name: str = Form(...),
    email: str = Form(...),
    position: str = Form(None),
    department: str = Form(None),
    picture: Optional[UploadFile] = File(None),
    resume: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_user)
):
    """
    Create a new employee

    This is like adding a new employee card to our filing cabinet!
    It can also save their picture and resume to cloud storage.

    Args:
        name: Employee's name (required)
        email: Employee's email (required)
        position: Job title (optional)
        department: Department name (optional)
        picture: Employee photo file (optional)
        resume: Resume PDF file (optional)

    Returns:
        The newly created employee with all their info
    """
    logger.info("=" * 60)
    logger.info("➕ CREATE EMPLOYEE REQUEST")
    logger.info("=" * 60)
    logger.info(f"   Name: {name}")
    logger.info(f"   Email: {email}")
    logger.info(f"   Position: {position or 'Not specified'}")
    logger.info(f"   Department: {department or 'Not specified'}")
    logger.info(f"   Has picture: {'Yes' if picture and picture.filename else 'No'}")
    logger.info(f"   Has resume: {'Yes' if resume and resume.filename else 'No'}")

    try:
        # Get the secret token for cloud storage
        blob_token = os.getenv('BLOB_READ_WRITE_TOKEN', 'vercel_blob_rw_eoYKodv04u6VYgX4_R0lYcUOoOkIT2JBj8ZCL2aQ9AxXXPs')

        picture_url = None
        resume_url = None

        # Upload picture if provided
        if picture and picture.filename:
            logger.info("📸 Uploading employee picture...")
            picture_url = await upload_to_vercel_blob(picture, blob_token)

        # Upload resume if provided
        if resume and resume.filename:
            logger.info("📄 Uploading employee resume...")
            resume_url = await upload_to_vercel_blob(resume, blob_token)

        # Prepare employee data for database
        employee_data = {
            "name": name,
            "email": email,
            "position": position,
            "department": department,
            "picture_url": picture_url,
            "resume_url": resume_url
        }

        logger.info("💾 Saving employee to database...")
        employee = db.create_employee(employee_data)

        logger.info("✅ Employee created successfully!")
        logger.info(f"   Employee ID: {employee['id']}")
        logger.info("=" * 60)

        return employee

    except Exception as e:
        logger.error("❌ OOPS! Failed to create employee!")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Full details:\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/employees")
async def get_employees(current_user: str = Depends(get_current_user)):
    """
    Get all employees

    This is like opening the filing cabinet and looking at all employee cards!

    Returns:
        A list of all employees
    """
    logger.info("=" * 60)
    logger.info("📋 GET ALL EMPLOYEES REQUEST")
    logger.info("=" * 60)

    try:
        employees = db.get_all_employees()
        logger.info(f"✅ Returning {len(employees)} employee(s)")
        logger.info("=" * 60)
        return employees

    except Exception as e:
        logger.error("❌ OOPS! Failed to get employees!")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Full details:\n{traceback.format_exc()}")
        logger.info("=" * 60)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: int, current_user: str = Depends(get_current_user)):
    """
    Get one specific employee

    This is like looking for one specific employee card by their ID number!

    Args:
        employee_id: The unique ID number of the employee

    Returns:
        The employee's information
    """
    logger.info("=" * 60)
    logger.info(f"🔍 GET EMPLOYEE REQUEST (ID: {employee_id})")
    logger.info("=" * 60)

    try:
        employee = db.get_employee(employee_id)

        if not employee:
            logger.warning(f"⚠️  Employee ID {employee_id} not found!")
            logger.info("=" * 60)
            raise HTTPException(status_code=404, detail="Employee not found")

        logger.info(f"✅ Found employee: {employee['name']}")
        logger.info("=" * 60)
        return employee

    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ OOPS! Failed to get employee!")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Full details:\n{traceback.format_exc()}")
        logger.info("=" * 60)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    name: str = Form(...),
    email: str = Form(...),
    position: str = Form(None),
    department: str = Form(None),
    picture: Optional[UploadFile] = File(None),
    resume: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_user)
):
    """
    Update an employee's information

    This is like taking out an employee card, erasing old info, and writing new info!

    Args:
        employee_id: The ID of the employee to update
        name: New name
        email: New email
        position: New position (optional)
        department: New department (optional)
        picture: New picture file (optional)
        resume: New resume file (optional)

    Returns:
        The updated employee information
    """
    logger.info("=" * 60)
    logger.info(f"✏️  UPDATE EMPLOYEE REQUEST (ID: {employee_id})")
    logger.info("=" * 60)
    logger.info(f"   New name: {name}")
    logger.info(f"   New email: {email}")
    logger.info(f"   New position: {position or 'Not specified'}")
    logger.info(f"   New department: {department or 'Not specified'}")
    logger.info(f"   New picture: {'Yes' if picture and picture.filename else 'Keep existing'}")
    logger.info(f"   New resume: {'Yes' if resume and resume.filename else 'Keep existing'}")

    try:
        blob_token = os.getenv('BLOB_READ_WRITE_TOKEN', 'vercel_blob_rw_eoYKodv04u6VYgX4_R0lYcUOoOkIT2JBj8ZCL2aQ9AxXXPs')

        picture_url = None
        resume_url = None

        # Upload new picture if provided
        if picture and picture.filename:
            logger.info("📸 Uploading new employee picture...")
            picture_url = await upload_to_vercel_blob(picture, blob_token)

        # Upload new resume if provided
        if resume and resume.filename:
            logger.info("📄 Uploading new employee resume...")
            resume_url = await upload_to_vercel_blob(resume, blob_token)

        # Prepare updated employee data
        employee_data = {
            "name": name,
            "email": email,
            "position": position,
            "department": department,
            "picture_url": picture_url,
            "resume_url": resume_url
        }

        logger.info("💾 Updating employee in database...")
        employee = db.update_employee(employee_id, employee_data)

        if not employee:
            logger.warning(f"⚠️  Employee ID {employee_id} not found!")
            logger.info("=" * 60)
            raise HTTPException(status_code=404, detail="Employee not found")

        logger.info("✅ Employee updated successfully!")
        logger.info("=" * 60)
        return employee

    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ OOPS! Failed to update employee!")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Full details:\n{traceback.format_exc()}")
        logger.info("=" * 60)
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/employees/{employee_id}")
async def delete_employee(employee_id: int, current_user: str = Depends(get_current_user)):
    """
    Delete an employee

    This is like taking an employee card out of the filing cabinet and shredding it!
    Be careful - this cannot be undone!

    Args:
        employee_id: The ID of the employee to delete

    Returns:
        A success message
    """
    logger.info("=" * 60)
    logger.info(f"🗑️  DELETE EMPLOYEE REQUEST (ID: {employee_id})")
    logger.info("=" * 60)

    try:
        success = db.delete_employee(employee_id)

        if not success:
            logger.warning(f"⚠️  Employee ID {employee_id} not found!")
            logger.info("=" * 60)
            raise HTTPException(status_code=404, detail="Employee not found")

        logger.info("✅ Employee deleted successfully!")
        logger.info("=" * 60)
        return {"message": "Employee deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ OOPS! Failed to delete employee!")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Full details:\n{traceback.format_exc()}")
        logger.info("=" * 60)
        raise HTTPException(status_code=500, detail=str(e))


# This runs when we start the app directly (not when deployed to Vercel)
if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 60)
    logger.info("🎯 Starting development server...")
    logger.info("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)

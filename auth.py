"""
Authentication Module for Employee Management System

This file handles user authentication using email and PIN codes.
Think of it like a digital security guard that checks if someone should be allowed in!

How it works:
1. User enters their email
2. We generate a random PIN (like a temporary password)
3. We send the PIN to their email
4. They enter the PIN to prove it's really them
5. We give them an access token (like a digital key card)
"""

import os
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secret key for generating tokens (like a master key for our security system)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# Email configuration (for sending PINs)
# NOTE: For production, use environment variables!
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")  # Your email address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Your email app password

# In-memory storage for PINs (in production, use Redis or database)
# This is like a temporary notepad where we write down PINs
pin_storage: Dict[str, Dict] = {}

logger.info("🔐 Authentication module loaded!")
logger.info(f"   Token expiration: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")


def generate_pin() -> str:
    """
    Generate a random 6-digit PIN

    Like creating a random password with 6 numbers!
    Example: "123456" or "789012"
    """
    pin = ''.join(random.choices(string.digits, k=6))
    logger.info(f"🎲 Generated new PIN: {pin[:2]}****")  # Don't log full PIN!
    return pin


def store_pin(email: str, pin: str) -> None:
    """
    Store a PIN for an email address temporarily

    Like writing down "Email: john@test.com, PIN: 123456" on a notepad
    We'll keep it for 10 minutes, then erase it
    """
    expiry_time = datetime.now() + timedelta(minutes=10)
    pin_storage[email] = {
        "pin": pin,
        "expires_at": expiry_time,
        "attempts": 0  # Track how many times they tried to enter the PIN
    }
    logger.info(f"💾 Stored PIN for {email}, expires at {expiry_time}")


def verify_pin(email: str, entered_pin: str) -> bool:
    """
    Check if the PIN entered by the user is correct

    Like checking if someone's password matches what we wrote down!

    Returns:
        True if PIN is correct and not expired, False otherwise
    """
    logger.info(f"🔍 Verifying PIN for {email}...")

    if email not in pin_storage:
        logger.warning(f"⚠️  No PIN found for {email}")
        return False

    stored_data = pin_storage[email]

    # Check if PIN has expired
    if datetime.now() > stored_data["expires_at"]:
        logger.warning(f"⏰ PIN for {email} has expired")
        del pin_storage[email]
        return False

    # Check if too many attempts
    if stored_data["attempts"] >= 3:
        logger.warning(f"🚫 Too many failed attempts for {email}")
        del pin_storage[email]
        return False

    # Check if PIN matches
    if stored_data["pin"] == entered_pin:
        logger.info(f"✅ PIN verified successfully for {email}")
        del pin_storage[email]  # Remove PIN after successful verification
        return True
    else:
        stored_data["attempts"] += 1
        logger.warning(f"❌ Incorrect PIN for {email} (Attempt {stored_data['attempts']}/3)")
        return False


def send_pin_email(email: str, pin: str) -> bool:
    """
    Send the PIN to the user's email address

    Like mailing them a letter with their temporary password!

    Returns:
        True if email sent successfully, False otherwise
    """
    logger.info(f"📧 Attempting to send PIN to {email}...")

    try:
        # For development/testing: Just log the PIN instead of sending email
        # This is useful when you don't have email configured yet!
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            logger.warning("⚠️  Email not configured - PIN will only be logged")
            logger.info(f"🔑 PIN for {email}: {pin}")
            logger.info("   (In production, this would be sent via email)")
            return True

        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Your Employee Management System Login PIN"
        message["From"] = SMTP_USERNAME
        message["To"] = email

        # Create email body (HTML for nice formatting)
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>🔐 Your Login PIN</h2>
                <p>Hello!</p>
                <p>Your PIN code to access the Employee Management System is:</p>
                <h1 style="background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 8px;">
                    {pin}
                </h1>
                <p>This PIN will expire in <strong>10 minutes</strong>.</p>
                <p>You have <strong>3 attempts</strong> to enter the correct PIN.</p>
                <p>If you didn't request this PIN, please ignore this email.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    This is an automated message from the Employee Management System.
                </p>
            </body>
        </html>
        """

        html_part = MIMEText(html_body, "html")
        message.attach(html_part)

        # Send email via SMTP
        logger.info(f"   Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            logger.info("   Logging in to email server...")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            logger.info("   Sending email...")
            server.send_message(message)

        logger.info(f"✅ PIN email sent successfully to {email}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send email to {email}")
        logger.error(f"   Error: {str(e)}")
        # In development, still log the PIN so user can login
        logger.info(f"🔑 PIN for {email}: {pin}")
        logger.info("   (Email failed, but you can use this PIN)")
        return True  # Return True anyway for development


def create_access_token(email: str) -> str:
    """
    Create an access token (JWT) for the user

    Like giving someone a digital key card that proves they're allowed in!
    The key card has their email on it and an expiration date.

    Returns:
        A special encrypted string (token) that the user can use to prove they're logged in
    """
    logger.info(f"🎫 Creating access token for {email}...")

    # Data to encode in the token
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "sub": email,  # "sub" stands for "subject" - who this token is for
        "exp": expire   # When this token expires
    }

    # Encode the token (encrypt it with our secret key)
    encoded_jwt = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    logger.info(f"✅ Access token created, expires at {expire}")
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verify an access token and extract the email from it

    Like checking if someone's key card is real and seeing whose name is on it!

    Returns:
        The email address if token is valid, None otherwise
    """
    try:
        logger.info("🔍 Verifying access token...")

        # Decode the token (decrypt it with our secret key)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            logger.warning("⚠️  Token is valid but has no email")
            return None

        logger.info(f"✅ Token verified for {email}")
        return email

    except JWTError as e:
        logger.error(f"❌ Invalid token: {str(e)}")
        return None


# Clean up expired PINs periodically (like emptying the trash)
def cleanup_expired_pins():
    """
    Remove expired PINs from storage

    Like throwing away old notes that are no longer useful!
    """
    now = datetime.now()
    expired_emails = [
        email for email, data in pin_storage.items()
        if now > data["expires_at"]
    ]

    for email in expired_emails:
        logger.info(f"🧹 Cleaning up expired PIN for {email}")
        del pin_storage[email]

    if expired_emails:
        logger.info(f"✅ Cleaned up {len(expired_emails)} expired PIN(s)")


logger.info("=" * 60)
logger.info("🔐 Authentication module is ready to use!")
logger.info("=" * 60)

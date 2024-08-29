import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Database URL for MySQL (Sample Data)
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://username:password@localhost:3306/your_database_name")

# Secret Key for JWT (Ensure this is a strong, random key in a real application)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkeyforjwtencoding12345")

# Email Configuration (Sample Data)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.example.com")      # Example SMTP server
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))                  # Commonly used port for TLS
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "your-email@example.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-email-password")

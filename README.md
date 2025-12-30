# Employee Management System

A simple single-page application (SPA) for managing employee records with CRUD operations, file uploads for employee pictures and resumes.

## Tech Stack

- **Frontend**: HTML, CSS, jQuery
- **Backend**: Python FastAPI
- **Database**: Vercel Postgres (Neon)
- **File Storage**: Vercel Blob Storage
- **Deployment**: Vercel

## Features

- Create, Read, Update, Delete (CRUD) employee records
- Upload employee pictures (images)
- Upload employee resumes (PDF files)
- Responsive single-page application
- Real-time table updates
- File storage using Vercel Blob
- **PIN-based email authentication** for secure access
- **Extensive logging** for easy debugging (backend and frontend)
- **Detailed error messages** with full stack traces
- **Complete beginner's tutorial** explaining every concept for 5th graders
- **Child-friendly documentation** with simple analogies and examples

## Learning Resources

### For Absolute Beginners

**New to programming?** We have TWO learning resources for you:

1. **[tutorial.html](tutorial.html)** - Interactive HTML tutorial page with graphics, diagrams, and visual explanations! Open this in your browser for a beautiful learning experience.

2. **[BEGINNER_TUTORIAL.md](BEGINNER_TUTORIAL.md)** - Text-based comprehensive guide (same content as the HTML version)

These tutorials cover:
- What is a web application? (Restaurant analogy)
- All technologies explained (HTML, CSS, JavaScript, Python, etc.)
- How the internet works (Simple conversation model)
- Complete code walkthrough with line-by-line explanations
- How authentication works (PIN codes, tokens)
- How everything fits together
- Practice exercises and glossary
- Written for 5th graders with NO programming experience

### For Debugging

See **[LOGGING_GUIDE.md](LOGGING_GUIDE.md)** for:
- How to read logs
- Understanding error messages
- Common debugging patterns
- Tips and tricks

## Project Structure

```
test101_teach/
├── app.py                  # FastAPI backend application (with extensive logging)
├── auth.py                 # Authentication module (PIN-based email login)
├── db.py                   # Database persistence layer (with extensive logging)
├── index.html              # Frontend SPA with jQuery (with console logging)
├── tutorial.html           # Interactive HTML tutorial with graphics (open in browser!)
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel deployment configuration
├── .env.example            # Environment variables template
├── BEGINNER_TUTORIAL.md    # Complete tutorial for absolute beginners (text version)
├── LOGGING_GUIDE.md        # Comprehensive guide to understanding logs
└── README.md              # This file
```

## Database Schema

The `employees` table has the following structure:

```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    position VARCHAR(255),
    department VARCHAR(255),
    picture_url TEXT,
    resume_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## API Endpoints

### GET /
- Serves the index.html page

### POST /api/employees
- Create a new employee
- Form fields: `name`, `email`, `position`, `department`, `picture` (file), `resume` (file)
- Returns: Created employee object

### GET /api/employees
- Get all employees
- Returns: Array of employee objects

### GET /api/employees/{employee_id}
- Get a single employee by ID
- Returns: Employee object

### PUT /api/employees/{employee_id}
- Update an employee
- Form fields: `name`, `email`, `position`, `department`, `picture` (file, optional), `resume` (file, optional)
- Returns: Updated employee object

### DELETE /api/employees/{employee_id}
- Delete an employee
- Returns: Success message

## Environment Variables

The following environment variables are configured in `vercel.json`:

- `DATABASE_URL`: PostgreSQL connection string (Vercel Postgres/Neon)
- `BLOB_READ_WRITE_TOKEN`: Vercel Blob storage token for file uploads

## Local Development

### Prerequisites

- Python 3.9+ (including Python 3.13)
- pip

**Note**: This project uses `psycopg` (version 3) which fully supports Python 3.13, unlike the older `psycopg2` which has compatibility issues with newer Python versions.

### Setup

1. Clone the repository or navigate to the project directory:
```bash
cd test101_teach
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export DATABASE_URL="postgresql://neondb_owner:npg_36MaJuyTbScI@ep-weathered-unit-ahc8hg3u-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
export BLOB_READ_WRITE_TOKEN="vercel_blob_rw_eoYKodv04u6VYgX4_R0lYcUOoOkIT2JBj8ZCL2aQ9AxXXPs"
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:8000
```

## Deployment to Vercel

### Prerequisites

- Vercel account
- Vercel CLI installed (`npm install -g vercel`)

### Deployment Steps

1. Login to Vercel:
```bash
vercel login
```

2. Deploy the application:
```bash
vercel
```

3. Follow the prompts to complete deployment

4. For production deployment:
```bash
vercel --prod
```

### Configuration

The `vercel.json` file is already configured with:
- Python runtime for FastAPI
- Route handling for API and static files
- Environment variables for database and blob storage

### Important Notes

- The database URL and blob token are already configured in `vercel.json`
- Ensure your Vercel project has access to the Postgres database
- Vercel Blob storage must be enabled in your Vercel project

## Usage

### Adding an Employee

1. Fill in the employee details in the "Add New Employee" form
2. Optionally upload a picture (JPG, PNG) and/or resume (PDF)
3. Click "Add Employee"

### Viewing Employees

- All employees are displayed in the table below the form
- Pictures are shown as thumbnails
- Resume links are clickable to view/download

### Updating an Employee

1. Click the "Edit" button next to an employee
2. The update form will appear with pre-filled data
3. Modify the fields as needed
4. Optionally upload new files (leave empty to keep existing files)
5. Click "Update Employee"

### Deleting an Employee

1. Click the "Delete" button next to an employee
2. Confirm the deletion in the popup dialog

## File Upload Details

### Supported File Types

- **Picture**: Images (JPG, PNG, GIF, etc.)
- **Resume**: PDF files only

### Storage

Files are uploaded to Vercel Blob Storage and their URLs are stored in the database.

### File Size Limits

- Default Vercel Blob limit: 4.5 MB per file
- For larger files, consider upgrading your Vercel plan

## Security Considerations

- Email addresses must be unique
- Input validation is performed on both frontend and backend
- SQL injection prevention through parameterized queries
- CORS is enabled for development (configure appropriately for production)

## Error Handling

- User-friendly error messages are displayed in the UI
- Backend returns appropriate HTTP status codes
- Database constraint violations are caught and reported

## Debugging and Logging

This application includes **extensive logging** to help you understand what's happening and debug issues easily!

### Backend Logging (Python)

Every action is logged with clear messages:
- 🚀 Application startup
- 🏠 Page requests
- ➕ Creating employees
- 📋 Fetching employee lists
- ✏️ Updating employees
- 🗑️ Deleting employees
- ☁️ File uploads
- ❌ Errors with full stack traces

**View backend logs**: Check your terminal where you ran `python app.py`

### Frontend Logging (JavaScript)

The browser console shows detailed logs for:
- Page load events
- Form submissions
- AJAX requests and responses
- Button clicks
- Modal open/close
- Errors with details

**View frontend logs**:
1. Open browser Developer Tools (Press F12)
2. Go to Console tab
3. Watch the logs as you use the application

### Detailed Logging Guide

See **[LOGGING_GUIDE.md](LOGGING_GUIDE.md)** for:
- How to read logs
- Understanding error messages
- Debugging common issues
- Log symbols guide
- Example log patterns
- Tips and tricks

The logging guide is written in simple terms (5th-grade level) to help anyone understand and debug the application!

## Troubleshooting

### Database Connection Issues

If you see `password authentication failed` errors:

1. **Check the DATABASE_URL format**: Ensure it includes the correct region identifier (e.g., `.c-3.` in the hostname)
   ```
   Correct: ep-weathered-unit-ahc8hg3u-pooler.c-3.us-east-1.aws.neon.tech
   Wrong: ep-weathered-unit-ahc8hg3u-pooler.us-east-1.aws.neon.tech
   ```

2. **Get fresh credentials from Vercel/Neon**:
   - Log into your Vercel dashboard
   - Go to Storage → Postgres
   - Click on your database
   - Copy the connection string from the `.env.local` tab

3. **Update environment variables**:
   - For local development: Set `DATABASE_URL` in your environment
   - For Vercel deployment: Update in `vercel.json` or Vercel dashboard

### Email Validation Issues

If you see `email-validator is not installed`:
```bash
pip install email-validator
```

### Python 3.13 Compatibility

If you see errors with `psycopg2-binary`:
- This project uses `psycopg` (v3) which supports Python 3.13
- Make sure `requirements.txt` has `psycopg[binary]>=3.2.2` not `psycopg2-binary`

## Future Enhancements

- Add pagination for large employee lists
- Implement search and filter functionality
- Add user authentication and authorization
- Implement role-based access control
- Add employee photo cropping/resizing
- Support multiple file formats for resumes

## License

This project is provided as-is for educational and demonstration purposes.

## Support

For issues or questions, please refer to the FastAPI, Vercel, and PostgreSQL documentation.

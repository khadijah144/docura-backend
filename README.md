# Docura Backend

Backend API for Docura, a document handling and AI-powered document search system.

## Tech Stack

* Python
* FastAPI
* SQLAlchemy
* SQLite
* JWT Authentication
* bcrypt
* Uvicorn

## Setup

### 1. Create and activate virtual environment

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```cmd
pip install -r requirements.txt
```

### 3. Configure environment

Create a `.env` file:

```env
SECRET_KEY=replace-with-your-own-secret-key
```

### 4. Start the server

```cmd
uvicorn main:app
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Demo Accounts

### HR

Username:

```text
hr
```

Password:

```text
hr12345
```

### Employee

Username:

```text
employee
```

Password:

```text
employee123
```

These accounts are for local/demo use only.

## Main Endpoints

### Authentication

`POST /auth/login`

Login and receive a JWT access token.

`GET /auth/me`

Get the currently authenticated user's information.

### Documents

`POST /documents`

Upload a document.

Supported file types:

* PDF
* DOCX
* TXT
* MD
* JPEG
* JPG
* PNG

Maximum file size: **10 MB**

`GET /documents`

List documents.

Optional department filter:

`GET /documents?department=HR`

`GET /documents/{document_id}`

Get one document.

`DELETE /documents/{document_id}`

Delete a document.

Employees can delete their own documents. HR can delete documents uploaded by others.

### Search

`POST /search`

Search documents by title, filename, or department.

### AI / RAG

`POST /ask`

Currently returns a placeholder response.

The AI team should integrate document retrieval, RAG, and answer generation here.

## Departments

* Operations
* Finance
* HR
* Engineering/IT
* Marketing
* Sales

## Project Structure

```text
docura-backend/
│
├── uploads/
│   └── .gitkeep
│
├── main.py
├── database.py
├── models.py
├── schemas.py
├── auth.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Important Notes

* `.env` contains local secrets and must not be committed.
* `docura.db` is a local SQLite database and is ignored by Git.
* Uploaded files are stored in the `uploads/` directory.
* The AI/RAG integration should preserve the existing authentication and document storage logic.

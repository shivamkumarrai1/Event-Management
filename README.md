## NeoFi Event Management Backend API

A secure and extensible FastAPI backend for managing events, user authentication, and role-based permissions.

##  Live Demo

🌐 API Base URL: [https://event-management-gitk.onrender.com](https://event-management-gitk.onrender.com)  
📘 API Docs (Swagger): [https://event-management-gitk.onrender.com/docs](https://event-management-gitk.onrender.com/docs)

##  Features

- 🔐 JWT-based Authentication (Access & Refresh Tokens)
- 👥 User Roles: Owner, Editor, Viewer
- 📆 CRUD operations on Events
- 👨‍👨‍👦 Share Events with specific permissions
- 📜 Full History Tracking per Event
- 🧪 Postman / Swagger-compatible API
- 📂 Modular architecture (models, schemas, routes)

---

## ⚙️ Technologies

- **FastAPI** + **Pydantic**
- **SQLAlchemy** + PostgreSQL
- **Render** (deployment)
- **JWTAuth** (`python-jose`, `passlib`)
- **Dotenv**, **Alembic** (for migrations)

---

## 📦 Getting Started

### 🔧 Setup (Local)

1. Clone the repo  
   `git clone https://github.com/shivamkumarrai1/event-management.git`

2. Create `.env` file from example:

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080

Install dependencies:

--pip install -r requirements.txt
--Run the app:

-uvicorn app.main:app --reload

🔑 Authentication
Login (returns access + refresh tokens):

POST /api/auth/login:
Body (x-www-form-urlencoded): username, password

Register:
POST /api/auth/register
Body (JSON): { "username", "email", "password" }

Token Refresh:
POST /api/auth/refresh

Logout:
POST /api/auth/logout


⚠️ Protected endpoints require Authorization: Bearer <access_token>


📘 API Endpoints Summary

# 🔐 Authentication
Method  Endpoint  Description

POST	/api/auth/register	 -Register new user
POST	/api/auth/login	    -Login (get tokens)
POST	/api/auth/refresh     -Refresh token
POST	/api/auth/logout	    -Logout

📆 Events Management

GET	 /api/events 	      -Get user's events (list all events the user has access to with pagination and filteration)
POST	/api/events 	      -Create new event
GET	 /api/events/{id}	   -Get specific event
PUT	 /api/events/{id}	   -Update event (if editor)
DELETE	/api/events/{id}	-Delete event (if owner)
post  /api/events/batch    -Create multiple events in a single request

🔒 Permissions (collaborations)
##To change a users's role for an event, you must first share that event with the user. Attempting to update permissions before sharing will result in an error.

POST  /api/events/{id}/share                        -Share an event with other users
GET	 /api/events/{id}/permissions 	             -List shared users
PUT	 /api/events/{id}/permissions/{user_id}       -Update a user’s permission
DELETE	 /api/events/{id}/permissions/{user_id}	 -Revoke access

🕓 Version History

POST /api/events/{id}/rollback/{versionId}        -Rollback to a previous version
GET	/api/events/{id}/history	                 -Get event change history

# Changelog & Difference

GET /api/events/{id}/changelog                          -Get a log of all changes to an event
GET /api/events/{id}/diff/{versionId1}/{versionId2}     -Get a difference between two versions

🔐 Roles & Permissions
Role	 Can View	 Can Edit	 Can Delete

Owner   ✅         ✅          ✅
Editor  ✅         ✅          ❌
Viewer  ✅         ❌          ❌

✅ Deployment (Render)
Backend: FastAPI via Render Web Service

Database: PostgreSQL (managed via Render)

.env values added to Render Environment Group

🧪 Testing
Use Swagger UI: /docs
## while testing through the Swagger UI, fill in only the required fields marked with an asterisk (*).

Or use Postman with:

Auth: Bearer Token
Content-Type: JSON / Form as needed

📂 Project Structure

📁 app/
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── events.py
│   ├── permissions.py
│   ├── history.py
│   ├── utils.py
│   ├── schemas.py
│   └── main.py
├── start.sh
├── .env.example
├── requirements.txt
└── README.md

## ✅ API Reference Is Auto-Generated

No extra work needed for OpenAPI spec — it’s already available at:

https://event-management-gitk.onrender.com/docs

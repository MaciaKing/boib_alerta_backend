# BOIB Alerta Backend

A lightweight FastAPI application configured with a PostgreSQL database and Alembic migrations.

---

## 🛠️ Environment Configuration (`.env`)

Create a `.env` file in the root directory of the project with the following variables:

```env
# PostgreSQL Configuration
POSTGRES_DB=boib_db
POSTGRES_USER=user
POSTGRES_PASSWORD=user

# Database Connection URL
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@boib-postgres:5432/${POSTGRES_DB}

# JWT Authentication
SECRET_KEY=supersecretkey
ALGORITHM="HS256"

# Initial User Setup
FIRST_USER_NAME=your name
FIRST_USER_EMAIL=your email
FIRST_USER_PASSWORD=your password
```

### Environment Variables Breakdown

* **PostgreSQL Settings:** Configures the database name, username, and password.
* **`DATABASE_URL`:** Complete connection string used by SQLAlchemy to connect to the `boib-postgres` database host.
* **`SECRET_KEY` & `ALGORITHM`:** Credentials for generating and validating secure JWT access tokens.
* **`FIRST_USER_*`:** Seed data used to create the initial admin account on application startup.

---

## 🚀 Commands

### 1. Database Migrations (Alembic)

To manage database schema changes, use Alembic:

* **Generate a new migration script:**
  ```bash
  alembic revision --autogenerate -m "description"
  ```

* **Apply all pending migrations to the database:**
  ```bash
  alembic upgrade head
  ```

### 2. Running the Server (Uvicorn)

Start the local FastAPI development server with hot-reloading:

```bash
uvicorn app.api.api:app --host 0.0.0.0 --port 8000 --reload
```

Once running, access:
* **API Endpoint:** `http://localhost:8000`
* **Interactive Docs (Swagger UI):** `http://localhost:8000/docs`
# portal-content-visibility

## Overview

A backend API for a Shareholders Portal.

A content item is visible to a shareholder if:

- it is **public** (visible to all authenticated shareholders), or
- it is **restricted** and the shareholder belongs to **at least one** allowed group assigned to that item.

Authentication is faked with a `user_id` query parameter.

---

## Seed Data

### Users

| User ID | Name | Group |
|----------|------|------------------|
| 1 | Alice | Series A |
| 2 | Bob | Board Observers |
| 3 | Charlie | None |

### Groups

| Group ID | Group Name |
|----------|------------------|
| 1 | Series A |
| 2 | Board Observers |

### Content

| Content ID | Title | Public | Allowed Group |
|------------|------------------|--------|------------------|
| 1 | Series A Update | No | Series A |
| 2 | Board Minutes | No | Board Observers |
| 3 | Public News | Yes | Everyone |

### Visibility Matrix

| User | Series A Update (1) | Board Minutes (2) | Public News (3) |
|------|:-------------------:|:-----------------:|:---------------:|
| Alice (User 1) | ✅ | ❌ | ✅ |
| Bob (User 2) | ❌ | ✅ | ✅ |
| Charlie (User 3) | ❌ | ❌ | ✅ |

---

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pytest

---

## Setup

Clone the repository:

```bash
git clone https://github.com/Angelo148/portal-content-visibility.git
cd portal-content-visibility
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python -m uvicorn app.main:app --reload
```

Open Swagger documentation:

```
http://127.0.0.1:8000/docs
```

The SQLite database is automatically created and seeded on first startup.

---

## API Endpoints

### Get all visible content

```http
GET /contents?user_id=1&limit=10&offset=0
```

Returns all content visible to the specified user.

Parameters:

- `user_id` (required)
- `limit` (optional, default = 10)
- `offset` (optional, default = 0)

Possible responses:

- `200 OK`
- `404 User not found`

---

### Get a single content item

```http
GET /contents/{content_id}?user_id=1
```

Possible responses:

- `200 OK`
- `403 Forbidden`
- `404 Content not found`
- `404 User not found`

---

## Design Decisions

- Visibility filtering is performed by the database using SQL rather than loading every content item into Python.
- API responses use a dedicated Pydantic schema (`ContentOut`) instead of exposing SQLAlchemy models directly.
- Pagination (`limit` and `offset`) was chosen instead of search because it fits a portal where users browse their available announcements.
- Authentication is intentionally simplified using the `user_id` query parameter as required by the assignment.

---

## Running Tests

Run:

```bash
python -m pytest
```

The tests execute against an isolated in-memory SQLite database and never modify the application's `portal.db` file.

---

## Assumptions

- SQLite is used as the database.
- The database is automatically seeded with demo data.
- Authentication is intentionally simplified using `user_id`.
- A content item is either public or restricted to one or more groups.

---

## Time Spent

Approximately **110 minutes**.

# AI Workflow & Code Fix Journal

This document explains how the Mini Laundry Order Management System was built using AI assistance, the specific prompts used, how AI was used to fix issues, and the technology stack chosen for the project.

---

## 1. Project Overview

This project is a lightweight Order Management System for a laundry/dry-cleaning store. It uses:

- **FastAPI** for the backend API
- **Pydantic** for request validation and models
- **Vanilla HTML/CSS/JavaScript** for the frontend dashboard
- **In-memory storage** for quick prototyping and demo use

The frontend is served as a static single-page application from the backend. The project is intentionally small and easy to run locally.

---

## 2. AI Tools Used

The following AI tools were used during development:

- **GitHub Copilot Chat** — primary assistant for code scaffolding, endpoint design, and debugging ideas
- **Claude (via Copilot)** — used for architecture questions and validation of API design choices
- **Workspace search / semantic search** — used to inspect existing code and understand file context when fixing issues

---

## 3. How AI Was Used

AI was used in three main ways:

1. **Scaffolding**
   - Generated an initial FastAPI project structure
   - Created Pydantic models for order payloads
   - Generated frontend HTML/CSS layout ideas for the SPA dashboard

2. **Feature implementation**
   - Added billing calculation logic
   - Implemented order CRUD endpoints
   - Added dashboard and filter functionality in frontend JavaScript

3. **Debugging / Fixing broken code**
   - Provided diagnoses for runtime errors
   - Suggested correct static file serving patterns for FastAPI
   - Recommended semantic HTTP verb changes and validation improvements

---

## 4. Prompts Used

These are the real prompts used while building and fixing the project.

### 4.1 Initial scaffolding

> "Create a FastAPI laundry order app with in-memory storage and Pydantic models for orders, garments, and billing."

### 4.2 Billing logic

> "Write a Python function that totals a laundry order from a price list and item quantities."

### 4.3 Status flow validation

> "Enforce order status transitions RECEIVED → PROCESSING → READY → DELIVERED with validation in FastAPI."

### 4.4 Frontend dashboard

> "Build a dark SPA dashboard with stats, order table, modal details, and a new order form using vanilla JS."

### 4.5 Debugging missing static file error

> "Fix FastAPI when it cannot find `static/index.html` but `index.html` is in the repo root."

---

## 5. How AI Helped Fix the Code

### 5.1 File serving issue

Problem:
- FastAPI was configured to serve `static/index.html` but the file was placed at the repository root.

AI guidance:
- Recommend moving `index.html` into a `static/` directory or adjusting the FastAPI route to use the root file location.

Fix applied:
- Created `static/` folder
- Copied `index.html` into `static/index.html`
- Confirmed FastAPI could now load the frontend asset successfully

### 5.2 Data modelling improvements

Problem:
- Initial AI output sometimes used simple types like `List[str]` instead of structured garment objects.

AI output corrected by hand:
- Changed to `garments: List[GarmentItem]`
- Added explicit `name` and `quantity` fields for each garment
- Added validation to ensure quantity is positive and garment names are valid

### 5.3 HTTP semantics

Problem:
- AI suggested `PUT` for updating order status.

Decision:
- Use `PATCH /orders/{order_id}/status` instead because the endpoint updates only one field.

### 5.4 Status transition validation

Problem:
- AI scaffolding did not enforce valid order status sequence.

Fix applied:
- Added a `STATUS_TRANSITIONS` mapping
- Added validation logic to reject invalid state changes
- This prevents skipping or reversing order stages

### 5.5 Frontend UX refinement

Problem:
- AI-generated frontend patterns sometimes relied on browser form submission instead of SPA behavior.

Fix applied:
- Rewrote interactions to use `fetch()` calls
- Added state rendering for orders, dashboard stats, and modal actions
- Kept implementation framework-free for simplicity

---

## 6. Tech Stack and Why It Was Chosen

| Layer | Technology | Why it was chosen |
|------|------------|-------------------|
| Backend | FastAPI | Fast to build, async-ready, excellent developer experience |
| Validation | Pydantic | Strong request validation, clean model definitions |
| Frontend | Vanilla HTML/CSS/JS | No framework overhead, easy to run locally, ideal for demos |
| Server | Uvicorn | Fast, reliable ASGI server for FastAPI |
| Storage | In-memory Python data | Simple prototype/demo usage without database setup |

### Why this stack works for this project

- It keeps the repository minimal and easy to run
- It avoids extra build tools or frontend bundlers
- It lets the app be run immediately with a Python virtual environment
- It is a good fit for demoing a small service without production complexity

---

## 7. Development Workflow Summary

1. **Start with an AI scaffold** for the API and data models
2. **Use AI to create frontend wireframes** and UI structure
3. **Validate and test manually** by running the app and checking endpoints
4. **Use AI to debug specific runtime errors** from logs
5. **Apply manual corrections** for data validation, semantics, and architectural tradeoffs
6. **Document the process** in this separate file so the AI-driven workflow is explicit

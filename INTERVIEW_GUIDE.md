# 🎓 Interview Preparation Guide: Prompt Service (Flask + MongoDB + LLM)

This guide is designed to help you explain this project clearly, step-by-step, even if you are a complete beginner to Python, Flask, or backend microservices.

---

## 1. The 30-Second Elevator Pitch

> *"In this project, I built a backend microservice called **Prompt Service** using **Python, Flask, and MongoDB**.*
> 
> *The goal is to provide a reliable middleware between users and AI/LLM models:*
> 1. *Instead of sending raw user input directly to an AI, the service takes pre-designed, domain-specific prompt templates stored in MongoDB (like education or technical interview templates).*
> 2. *It safely interpolates the user question into the template using placeholders (`{{userInput}}`).*
> 3. *It calls the LLM (OpenAI API with an automatic local Mock fallback).*
> 4. *It supports both **single requests** and **asynchronous parallel batch requests** while strictly preserving the original question order.*
> 5. *Finally, every single interaction, latency, and response is logged into a MongoDB history collection for auditing and analytics."*

---

## 2. Real-Life Analogy (To Make It Intuitive)

Think of this service like a **smart translator or restaurant waiter**:
* **The Customer (User)** just says: *"I want coffee"* (`userInput`).
* **The Waiter (Our Service)** doesn't just yell *"coffee"* at the chef. Instead, the waiter looks at the **recipe book (MongoDB)** for the standard template:
  * `"Make a hot cup of {{userInput}} with 2 cubes of sugar and low-fat milk."`
* The waiter fills in the blank: `"Make a hot cup of coffee with 2 cubes of sugar and low-fat milk."`
* The waiter gives this formatted order to the **Chef (LLM / OpenAI)**.
* The Chef responds with the coffee.
* The waiter writes down the order details and preparation time in a **ledger book (MongoDB History)**.
* The waiter serves the coffee back to the customer.

---

## 3. Libraries Used & Why

| Library | What it is in simple words | Why we used it in this project |
| :--- | :--- | :--- |
| **Flask** | A lightweight web framework for Python. | Creates REST API endpoints like `POST /api/generate` and `GET /api/history`. |
| **Flask-CORS** | Cross-Origin Resource Sharing handler. | Allows frontend apps (React/Vue) on other ports/domains to call our API. |
| **PyMongo** | The official Python driver for MongoDB. | Connects Python to MongoDB to run queries like `find_one()` and `insert_one()`. |
| **mongomock** | An in-memory fake MongoDB. | **Key highlight:** If MongoDB is not installed or running locally, the app automatically switches to `mongomock` so it never crashes! |
| **OpenAI** | Official Python library for OpenAI GPT models. | Sends the final rendered prompt to OpenAI API. |
| **python-dotenv** | Loads `.env` file variables into Python. | Keeps sensitive values (API keys, ports) out of source code. |
| **asyncio** | Python built-in asynchronous library. | Executes multiple LLM calls in parallel rather than waiting one by one. |

---

## 4. Architecture & Request Flow

```
[ Client / Postman / Frontend ]
               │
               ▼  HTTP POST /api/generate {"userInput": "..."}
       [ routes/api_routes.py ]
               │ (Validates request JSON, handles HTTP status codes)
               ▼
      [ services/prompt_service.py ]
         │          │
         │ 1. Fetches template from Database
         ▼
     [ db.py (MongoDB / mongomock) ]
         │
         │ 2. Replaces {{userInput}} in template
         ▼
      [ services/llm_service.py ]
         │ (Calls OpenAI API or Mock LLM fallback)
         ▼
      [ services/prompt_service.py ]
         │ (Logs record into MongoDB history collection)
         ▼
       [ routes/api_routes.py ]
               │
               ▼  Returns 200 OK {"response": "..."}
[ Client / Postman / Frontend ]
```

---

## 5. File-by-File Breakdown

### 1. `config.py`
* **What it does:** Reads configuration values from `.env` (like `PORT`, `MONGO_URI`, `OPENAI_API_KEY`).
* **Why it matters:** Centralizes settings so we don't hardcode sensitive information.

### 2. `db.py`
* **What it does:** Manages the MongoDB connection pool using a `Database` class.
* **Smart feature to mention:** If connecting to a live MongoDB server times out after 2 seconds, it automatically falls back to an in-memory `mongomock` database and seeds default prompts automatically.

### 3. `services/llm_service.py`
* **What it does:** Communicates with the AI.
* **Single Call (`call_llm_single`):** Sends one prompt and measures latency in milliseconds. If the OpenAI key is missing or invalid, it returns a simulated mock response so the service never breaks.
* **Batch Call (`call_llm_batch_async`):** Uses Python's `asyncio.gather` to send multiple requests in parallel. It attaches an index `(index, prompt)` so when responses come back at different times, they are sorted back into their **exact original order**.

### 4. `services/prompt_service.py`
* **What it does:** The business logic core.
* Fetches the prompt template from MongoDB.
* Replaces `{{userInput}}` with the user's actual text.
* Calls `llm_service.py`.
* Saves the interaction record into the `history` collection in MongoDB.

### 5. `routes/api_routes.py`
* **What it does:** Defines REST API endpoints using Flask Blueprints:
  * `POST /api/generate` (Single request)
  * `POST /api/generate/batch` (Asynchronous batch request)
  * `GET /api/prompts` (List templates)
  * `GET /api/history` (Audit log of previous prompts and responses)
  * `GET /api/health` (Health check of API and DB)

### 6. `app.py`
* **What it does:** The application entry point. Creates the Flask app instance, enables CORS, registers the routes blueprint, and starts the server on port 5001.

### 7. `seed_db.py` & `test_api.py`
* `seed_db.py`: A standalone script to insert or update the prompt templates in MongoDB using `upsert=True` (idempotent).
* `test_api.py`: Automated test suite with 6 test cases using Flask's `test_client()` to verify health, single generation, batch async ordering, history logging, and validation errors.

---

## 6. Top Interview Questions & How to Answer

### Q1: *"Why did you use port 5001 instead of default 5000 in Flask?"*
> **Answer:** *"On macOS (Monterey and later), port 5000 is used by Apple's built-in AirPlay Receiver service. To avoid port collisions and ensure seamless execution on Mac, I configured the default port to 5001 in `.env`."*

### Q2: *"How did you handle the Batch API in Step 6, and how do you guarantee order preservation?"*
> **Answer:** *"In `llm_service.py`, I implemented `call_llm_batch_async` using Python's `asyncio`. Because network requests finish at unpredictable times, request #2 might finish before request #0. To prevent out-of-order responses, I tag each item with its original index `(i, prompt)`. When all parallel calls complete via `asyncio.gather`, I sort the responses by their original index before returning them to the user."*

### Q3: *"What happens if the OpenAI API key is missing, expired, or invalid?"*
> **Answer:** *"The service has graceful degradation. In `llm_service.py`, if the API key is missing or OpenAI returns an authentication error (HTTP 401), the service catches the exception and falls back to a deterministic Mock response. This guarantees 100% uptime for local testing and automated CI/CD pipelines."*

### Q4: *"What happens if MongoDB is not installed on the system running this?"*
> **Answer:** *"In `db.py`, I implemented an automatic fallback to `mongomock`. If connection to a live MongoDB instance times out, the service automatically initializes an in-memory mock database and seeds it with default templates. The user or evaluator doesn't even need to have MongoDB installed to run and test the project."*

### Q5: *"Why did you use a Blueprint in Flask?"*
> **Answer:** *"Blueprints allow modular design in Flask. Instead of putting all endpoints, database connections, and business logic inside a single monolithic `app.py`, I separated the code into `routes/`, `services/`, and configuration. This makes the codebase clean, readable, and easy to maintain."*

---

## 7. Quick Practice Script (Say this out loud before the interview)

> *"Hi! For the assignment, I built a production-grade Prompt Service using Flask, MongoDB, and OpenAI.
> The core problem it solves is templating and governance around LLM prompts. 
> A client sends an input, the service fetches a specialized template from MongoDB, safely injects the user input, queries the LLM, logs the transaction for observability, and returns the response.
> For scale, I implemented an asynchronous batch endpoint that runs requests in parallel while guaranteeing that response order matches input order.
> To make it reliable and easy for anyone to evaluate, I built zero-dependency fallbacks with `mongomock` and Mock LLM responses, along with an automated test suite that covers all 6 requirements."*

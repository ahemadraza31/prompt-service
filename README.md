# 🚀 Prompt Service (Flask + MongoDB + LLM)

## ⚙️ Setup & Installation

### 1. Clone & Navigate
```bash
git clone https://github.com/ahemadraza31/prompt-service.git
cd prompt-service
```

### 2. Create & Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` Configuration
Create a `.env` file in the root folder with:
```env
PORT=5001
DEBUG=True
MONGO_URI=mongodb://localhost:27017/
DB_NAME=prompt_service_db
OPENAI_API_KEY=
DEFAULT_PROMPT_ID=Education_Prompt
```
*(Note: If `OPENAI_API_KEY` is blank or invalid, the service automatically falls back to Mock LLM mode.)*

---

## 🏃 How to Run the Project

### Step 1: Seed Initial Database Templates
```bash
python seed_db.py
```

### Step 2: Start the Flask Server
```bash
python app.py
```
The server will start running on: `http://localhost:5001`

---

## 🧪 How to Run Automated Tests

Run the test suite to verify all single, batch async, and validation tests:
```bash
python test_api.py
```

---

## 📡 Testing Endpoints with cURL

### 1. Health Check
```bash
curl -X GET http://localhost:5001/api/health
```

### 2. List Available Prompt Templates
```bash
curl -X GET http://localhost:5001/api/prompts
```

### 3. Single Prompt Generation (Step 1-5)
```bash
curl -X POST http://localhost:5001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"userInput": "How much should I score in each subject to pass CA final?"}'
```

### 4. Batch Prompt Generation (Step 6 - Async Parallel)
```bash
curl -X POST http://localhost:5001/api/generate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      "Question 1: Explain gravity",
      "Question 2: Explain photosynthesis",
      "Question 3: Explain quantum physics"
    ]
  }'
```

### 5. View History Logs
```bash
curl -X GET http://localhost:5001/api/history?limit=5
```

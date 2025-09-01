
# 🎫 Freshservice RAG Assistant

A **Retrieval-Augmented Generation (RAG) system** that integrates with **Freshservice API** to scrape documentation, build embeddings, and allow users to ask **natural language questions** about Freshservice.

It also supports **ticket creation and search** with a simple **Flask web interface**.

---

## 🚀 Problem Statement

We want to:

1. **Scrape the Freshservice API documentation**.
2. **Embed the docs** into a vector database for semantic search.
3. **Use a Large Language Model (LLM)** (via OpenAI) to answer queries based on these docs.
4. **Provide a web UI** for users to interact with the system.

---

## 📌 Features

✅ Secure API key management via `.env`

✅ Scrape Freshservice API docs automatically

✅ Build **RAG pipeline** with FAISS vector search

✅ Ask questions in **plain English** → get doc-based answers

✅ Create & fetch Freshservice support tickets

✅ Flask-powered UI (no React, only HTML + CSS)

✅ Handles OpenAI quota errors & API key issues

---

## 🏗️ Tech Stack

| Tool / Library     | Why Used                                        |
| ------------------ | ----------------------------------------------- |
| **Python 3.10+**   | Core programming language                       |
| **Flask**          | Lightweight web framework for serving UI + API  |
| **OpenAI API**     | GPT models for text generation + embeddings     |
| **FAISS**          | Vector similarity search for RAG                |
| **Requests**       | REST API calls to Freshservice                  |
| **Dotenv**         | Load `.env` environment variables securely      |
| **BeautifulSoup4** | Web scraping the Freshservice API documentation |
| **HTML + CSS**     | User interface (Flask templates, no React)      |

---

## ⚙️ Project Structure

```
freshservice-rag/
│── app.py              # Flask web app (UI + routes)
│── rag.py              # RAG logic: embeddings, retrieval, answering
│── scraper.py          # Scrapes Freshservice docs & saves text
│── ingest.py           # Converts scraped docs into FAISS embeddings
│── freshservice_api.py # Helper functions for Freshservice API (tickets, search, etc.)
│── requirements.txt    # Python dependencies
│── .env                # API keys (ignored in git)
│── templates/          # HTML files (Flask templates)
│   └── index.html
│── static/
|   └── style.css       # CSS styling
```

---

## 🔑 Environment Variables

Create a `.env` file in the root folder:

```ini
# OpenAI API keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx
OPENAI_PROJECT_ID=proj_xxxxxxxxxxxxxxxx

```

---

## 📦 Installation & Setup

1. **Clone repo**

   ```bash
   git clone https://github.com/yourusername/freshservice-rag.git
   cd freshservice-rag
   ```

2. **Create & activate virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set API keys**

   * Add them to `.env` file (see above).
   * Or set manually:

     ```powershell
     setx OPENAI_API_KEY "sk-proj-xxxx"
     setx FRESHSERVICE_API_KEY "xxxx"
     ```

---

## 🧩 Workflow – When to Run Which File

### 🔹 1. Scrape Freshservice docs

```bash
python scraper.py
```

📌 **Why:** Downloads Freshservice API documentation from `https://api.freshservice.com/#ticket_attributes`.
📌 **After run:** Saves raw text into a `.txt` file (e.g., `docs/freshservice_docs.txt`).

---

### 🔹 2. Convert scraped docs into embeddings

When you run

```bash
python ingest.py
```

### ✅ What happens

1. `ingest.py` loads your scraped Freshservice docs (from `scraper.py` output).
2. Converts each chunk of text into **vector embeddings** using OpenAI’s `text-embedding-3-small` or similar.
3. Saves these embeddings + metadata for later retrieval.

---

### 📂 Files Generated

By default (from your description), two files get created inside the `data/` folder:

1. **`embeddings.npy`**

   * Format: NumPy array.
   * Content: Dense vectors (usually 1,536 dimensions if `text-embedding-3-small` is used).
   * Each row corresponds to a chunk of text from your docs.
   * Example (simplified):

     ```python
     [
       [0.012, -0.234, 0.543, ...],   # embedding for doc chunk 1
       [0.876,  0.123, -0.456, ...],  # embedding for doc chunk 2
       ...
     ]
     ```

2. **`metadata.json`**

   * Format: JSON list.
   * Content: Metadata that maps each embedding back to the **original text chunk**.
   * Usually contains:

     * The raw chunk of documentation text.
     * The source file / section it came from.
   * Example (simplified):

     ```json
     [
       {"text": "Tickets are the primary object in Freshservice...", "source": "tickets.html#attributes"},
       {"text": "You can create a ticket by POST /api/v2/tickets...", "source": "tickets.html#create"},
       ...
     ]
     ```

---

### ❓ Why don’t you see `vectorstore/faiss_index`?

That’s because your `ingest.py` is saving **raw embeddings** (`.npy`) and metadata (`.json`) instead of persisting them in a FAISS index.

👉 Two possibilities:

1. Your code is written to **load embeddings directly** into FAISS at runtime (`rag.py` or `app.py`).

   * That means FAISS isn’t pre-saved as `vectorstore/faiss_index`.
   * Instead, embeddings + metadata are reloaded each time into FAISS.

2. Or, if the repo intended FAISS persistence, the saving step was skipped in `ingest.py`.

---

### 🔑 TL;DR

* `embeddings.npy` → NumPy matrix of vector embeddings.
* `metadata.json` → Mapping of those vectors to original docs.
* No `vectorstore/faiss_index` because your pipeline is **embedding → npy/json → load into FAISS dynamically**, not persistently.

---


---

### 🔹 3. Ask questions with RAG pipeline

```bash
python rag.py
```

📌 **Why:** Test RAG pipeline directly from CLI.
📌 **After run:** You can type a question like *“How do I create a Freshservice ticket?”* → it retrieves docs + GPT answer.

---

### 🔹 4. Run web app

```bash
python app.py
```

📌 **Why:** Starts Flask server for UI.
📌 **After run:** Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) → Ask questions, view answers, or create tickets.

---

## 🛠️ Troubleshooting

### 🔑 Wrong API key still showing?

```powershell
[System.Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
```

Remove from GUI:
👉 `Win + R → SystemPropertiesAdvanced → Environment Variables → Delete OPENAI_API_KEY`

---
### ⚠️ Troubleshooting OpenAI API Key Issues
Sometimes you may notice your project is still using an old OpenAI API key (even after updating .env).
This happens because Windows stores persistent environment variables.

**✅ Steps to Fix**

1. Check which key is being used:

```
In PowerShell:
[System.Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
[System.Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "Machine")

```
2. If an old key is found → Delete it:

- Open Run → SystemPropertiesAdvanced

- Click Environment Variables

- Under User variables, find OPENAI_API_KEY → Delete it

- Restart your terminal

3. Verify it’s gone:
  ```
Powershell
echo $env:OPENAI_API_KEY   # should show nothing

   ```
4. Rely only on your .env file for new keys:
   ```
   Rely only on your .env file for new keys:
   ```
   Now the project will always pick the latest key from `.env`.

   
### ⚠️ Error 429 – "insufficient\_quota"

* Means your OpenAI key is valid but **no credits left**.
* Fix:

  * Add payment method → [OpenAI Billing](https://platform.openai.com/settings/organization/billing/overview)
  * Or use **different account / Azure OpenAI / local LLM**

---

### ❌ Flask not starting?

Reinstall dependencies:

```bash
pip install flask openai python-dotenv faiss-cpu requests beautifulsoup4
```

---

## 📄 Example Freshservice API Call

```bash
curl -u "FRESHSERVICE_API_KEY:x" \
     -X POST 'https://yourdomain.freshservice.com/api/v2/tickets' \
     -H "Content-Type: application/json" \
     -d '{
       "subject": "Sample Ticket",
       "description": "This is a test ticket",
       "email": "user@example.com",
       "priority": 1,
       "status": 2
     }'
```
### OUTPUTS 
**🔹 When to run each script**

`scraper.py`

Runs only when you want to collect **fresh docs** (from web or source).

Example: If the knowledge base changes.

`ingest.py`

Runs only after scraping, or **when you want to rebuild embeddings (vector DB).**

Example: You added new docs, so you need new embeddings.

`app.py`

**This is your actual Flask web app.**

Once `scraper.py` and `ingest.py` have been run at **least once** and data is prepared, you only need to run this one.

Use it every time you want to start the chatbot.


*output for* `python scraper.py`  # will create data/docs.json

<img width="1629" height="524" alt="scraper- ingest - app " src="https://github.com/user-attachments/assets/0dd38f69-1d18-4a42-b315-48c01dfbdf38" />

*output for* `python ingest.py`  # will compute embeddings -> data/embeddings.npy & data/metadata.json

<img width="874" height="138" alt="ingest-" src="https://github.com/user-attachments/assets/70376f30-03c2-4717-a7c8-7d9a21aeb107" />

*output for* `python rag.py`  

<img width="1648" height="626" alt="rag-" src="https://github.com/user-attachments/assets/606de97a-96d7-4c53-b34b-955bebd153ff" />

*output for* `python app.py`  # open http://127.0.0.1:5000


<img width="1202" height="695" alt="app " src="https://github.com/user-attachments/assets/5ebb8d86-efde-4098-bb7d-7cb8d7c358af" />


<img width="1640" height="146" alt="scraper-" src="https://github.com/user-attachments/assets/4c8ae873-7590-4b25-b626-d4c99df73160" />




https://github.com/user-attachments/assets/9a3d32cf-b25b-42ee-8e21-1761bf71b17e


https://github.com/user-attachments/assets/c15d0ece-a529-490f-bf61-a61ce4421c32


---

## 🛡️ Security Notes

* ❌ Never commit `.env` file.
* 🔑 Rotate keys if leaked.
* 🖥️ Use `setx` or GUI to clear old env vars.

---

**Soumya K C**

**soumya.kc161@gmail.com**

---



# Enterprise AI Knowledge Agent

A local-first Retrieval-Augmented Generation (RAG) application based on the supplied project report. It indexes PDF, DOCX and TXT documents, retrieves semantically relevant passages with `all-MiniLM-L6-v2` + FAISS, and uses Google Gemini 2.5 Flash to answer questions with inline source references.

## Features

- Streamlit web UI with employee chat and an admin dashboard
- PDF, DOCX and TXT text extraction (including DOCX tables)
- Text cleaning and overlapping recursive chunks (1000 characters, 200 overlap)
- Local sentence-transformer embeddings and a persistent FAISS index
- Top-4 semantic retrieval using normalized vectors / cosine similarity
- Gemini-grounded answers, temperature 0, and source excerpts displayed with each answer
- Separate configured admin and employee logins
- Local index maintenance and document listing

> **Important accuracy note:** RAG and temperature 0 do not guarantee zero hallucinations. Always verify critical answers against cited source documents. Scanned PDFs need OCR, which is not included in this version.

## Requirements

- Windows 10/11, macOS or Linux
- Python 3.11 recommended
- Internet access for installing packages, downloading the embedding model the first time, and calling Gemini
- A Google Gemini API key. API usage may incur charges or be subject to quotas.

## Run on Windows / VS Code

1. Extract the ZIP file to a folder, then open that folder in VS Code.
2. Open Terminal in VS Code (`Terminal` → `New Terminal`).
3. Create and activate a virtual environment:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run `.venv\\Scripts\\activate.bat`, or continue with `.venv\\Scripts\\python.exe` explicitly.

4. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` and edit `.env`:
   - Set `GEMINI_API_KEY` to your own Google Gemini API key.
   - Change both admin and employee passwords.
   - Keep `.env` private; it is excluded by `.gitignore`.

6. Start the app:

   ```powershell
   streamlit run app.py
   ```

7. Open the local URL printed in the terminal (normally `http://localhost:8501`). Sign in with the credentials you set in `.env`.

## First use

1. Sign in as the configured admin.
2. Open **Admin Dashboard**.
3. Upload PDF/DOCX/TXT documents and click **Save uploads**.
4. Click **Build / Rebuild Index**. The first run downloads the embedding model and may take a while.
5. Sign out and sign in as the employee, then ask questions in **AI Knowledge Chat**.
6. Expand **Sources used** to inspect the source filename, chunk number and retrieved text.

Documents are stored in `data/documents/`. The FAISS index and chunk metadata are stored in `data/index/`. These are local files; back them up if needed. Rebuild the index after changing or removing documents.

## Project structure

```text
enterprise_ai_knowledge_agent/
├── app.py                 # Streamlit UI and navigation
├── src/
│   ├── auth.py            # Configured admin/employee sign-in
│   ├── ingestion.py       # Parsing, cleaning, chunking, embeddings and FAISS
│   └── rag.py              # Retrieval and Gemini answer generation
├── data/
│   ├── documents/         # Uploaded source files (not included in ZIP)
│   └── index/             # Persisted FAISS index and chunk metadata
├── tests/
├── .env.example           # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `GEMINI_API_KEY` | Gemini API key (required to answer questions) | unset |
| `GEMINI_MODEL` | Generation model | `gemini-2.5-flash` |
| `EMBEDDING_MODEL` | Sentence-transformer model | `sentence-transformers/all-MiniLM-L6-v2` |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Admin login | `admin` / must be set |
| `EMPLOYEE_USERNAME` / `EMPLOYEE_PASSWORD` | Employee login | `employee` / must be set |

## Troubleshooting

- **Missing API key:** Ensure `.env` exists beside `app.py`, contains `GEMINI_API_KEY=...`, and restart Streamlit.
- **Quota / 429 error:** Check your Google AI Studio / Gemini API project quota and billing eligibility. This is separate from local indexing.
- **FAISS installation failure:** Use a supported Python 3.11 environment and update pip before installing requirements.
- **Index not ready:** Sign in as admin, upload files, and build the index.
- **PDF has no text:** It may be scanned/image-only. OCR is not included in this version.
- **Changes to documents not reflected:** Rebuild the index after uploading or replacing source documents.
- **Model download fails:** Check network access and available disk space; the embedding model is downloaded on first use.

## Security and production hardening

This is a runnable educational project/prototype, not a production-certified enterprise security system. The login uses credentials stored in environment variables and Streamlit session state; it does not provide user provisioning, password hashing at rest, MFA, audit logging, or robust per-document access controls. Anyone with server filesystem access may be able to read stored documents and the index. Use only approved data, restrict host/network access, rotate secrets, and implement your organization's identity provider, RBAC, audit logs, encrypted storage, and retention rules before production deployment. Retrieved excerpts are sent to the Gemini API for generation, so confirm your organization's data-processing requirements before uploading sensitive documents.

## Architecture

```text
PDF / DOCX / TXT
       │
       ▼
Extract text → Clean → Recursive chunks (1000 / 200 overlap)
       │
       ▼
all-MiniLM-L6-v2 embeddings (384 dimensions)
       │
       ▼
FAISS local index ────────────────┐
                                  │
User question → query embedding → top-4 relevant chunks
                                  │
                                  ▼
                      Grounded prompt → Gemini 2.5 Flash
                                  │
                                  ▼
                    Answer with [1], [2] citations
```

## License

For educational/project use. Add a license file if redistributing under specific terms.

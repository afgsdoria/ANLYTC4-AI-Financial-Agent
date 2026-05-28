# finAI: An AI Financial Planning Agent 🇵🇭

> **"Turn financial goals into step-by-step action plans with AI-driven tracking, automated forecasting, and continuous budget analysis."**

finAI is an intelligent, autonomous personal finance agent engineered specifically to bridge the financial literacy gap for Filipino demographics—including students, minimum-wage earners, and freelancers. Unlike passive expense tracking systems, finAI interprets plain-language aspirations, dynamically resolves pricing information gaps via live web search utilities, evaluates personal spending risks against deterministic algorithms, and synthesizes strategic action plans alongside on-demand PDF report generation.

---

![finAI Landing Page Dashboard](./finAI%20Home%20Page.png)

---

## Tech Stack & Project Dependencies

The application is written natively in **Python 3.12** and leverages the following core ecosystem packages:

### Core Framework & Analytics
*   **Streamlit**: Dictates application routing, active view layout states, and session-guided multi-stage container updates.
*   **Pandas**: Drives background data aggregation, multi-row transactional group mappings, and dataframe matrix alignments[cite: 2].
*   **python-dateutil**: Manages calendar arithmetic parsing, user age constraints, and dynamic milestone target offsets[cite: 2].

### Generative AI & Autonomous Web Tools
*   **OpenAI Python SDK**: Transmits unformatted context strings securely to the `gpt-4o-mini` engine via encrypted HTTPS TLS channels[cite: 2].
*   **DuckDuckGo API / Scraper**: Empowers the agent to autonomously fetch current market, ticket, or retail pricing details across the web when information gaps occur[cite: 2].
*   **PyPDF2 / python-docx / openpyxl**: Parses text parameters and ledger cells from unstructured file streams or legacy spreadsheet imports[cite: 2].

### Storage, Safety, & Document Compilation
*   **SQLite3**: Provides local multi-tenant database row isolation secured cleanly under unique username filters[cite: 2].
*   **ReportLab**: Compiles validated metrics and narrative plans into clean, physical, downloadable PDF portfolios (`reports.py`)[cite: 2].
*   **python-dotenv**: Loads server-side configuration profiles and critical API credentials silently at initial setup[cite: 2].

---

## Installation & Local Environment Setup

Follow this sequential terminal script to isolate dependencies, configure environment access tokens, and initialize the Streamlit interface locally.

### 1. Clone the Repository & Initialize Environment
```bash
# Clone the repository
git clone [https://github.com/afgsdoria/anlytc4-ai-financial-agent_4.git](https://github.com/afgsdoria/anlytc4-ai-financial-agent_4.git)
cd anlytc4-ai-financial-agent_4

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Project Dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Configure Your Environment Variables
Create a file named .env in the root project directory and paste your configuration credentials:
OPENAI_API_KEY=your_actual_openai_api_key_here

# Run the Application Workspace
python -m streamlit run app.py
```
---


## How It Works

finAI delivers data-driven, privacy-centric financial analysis through an automated pipeline directly on your dashboard:

* **File Upload & Privacy Isolation**: You begin by uploading a legacy financial spreadsheet or tracker file directly via the Streamlit interface. Before processing, the application automatically scrubs and anonymizes all sensitive transactional entries to protect your identity.
* **Lightweight Metadata Extraction**: To guarantee strict data privacy and save dramatically on API context token usage, the system extracts a lightweight metadata summary instead of passing massive raw log sheets to the network.
* **Data Quality Evaluation**: The local system evaluates this clean summary to check layout alignment, baseline totals, and entry quality against deterministic financial constraints.
* **Unified Intelligence Engine**: The agent dispatches this clean metadata context securely via the OpenAI Python SDK. A single **gpt-4o-mini** model running at a low temperature handles all smart features—including mapping out dynamic dashboard charts, leading conversational chat coach interactions, and generating personalized 5-step action plans simultaneously.

## Limitations
To maintain operational structural safety and keep calculations clean, finAI operates within strict systemic boundaries:

* The system has no backend capability to cross-verify the absolute real-world validity of manually entered ledger transactions. Analytical accuracy relies completely on data-entry honesty from the user.
* The predictive 12-month savings forecast tool relies on static linear models using your current tracking baseline margin. It cannot predict sudden inflation adjustments, currency fluctuations, or emergency cash surges.
* The system serves entirely as a personal finance companion. It does not integrate directly with real digital banks, credit cards, or local mobile wallets, ensuring total isolation from your real liquid funds.

## Disclaimer
finAI is an advisory tool designed to guide you, not manage your money. You always maintain full control over your spending decisions and data. Your information is kept completely private and secure locally, with zero direct connection to your real bank accounts or digital wallets.
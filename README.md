# AI CV to LinkedIn Job Matcher & Tailor

This application helps you find relevant LinkedIn job postings based on your CV, provides AI-driven insights, and even helps you tailor your CV for specific roles!

**Features:**

*   Upload your CV (PDF, DOCX, DOC, TXT).
*   AI analyzes your CV to understand your skills, experience, and ideal job types.
*   Searches LinkedIn for jobs that match your profile and chosen location.
*   AI scores how well each job matches your CV.
*   Provides links to search for potential contacts (recruiters, managers) at the hiring companies on LinkedIn.
*   Uses AI to rewrite and tailor your CV specifically for a selected job posting.
*   Gives you actionable recommendations on how to improve your CV for that job.

---

##  Running the Application: Step-by-Step Guide

This guide will walk you through setting up and running the application on your own computer.

**Prerequisites:**

*   **Python 3.8 or newer:** This application is written in Python. If you don't have Python installed, you'll need to install it first.
    *   **How to check if you have Python:** Open your computer's command line tool (Terminal on macOS/Linux, Command Prompt or PowerShell on Windows) and type `python --version` or `python3 --version`.
    *   **How to install Python:** Go to the official Python website: [python.org/downloads/](https://www.python.org/downloads/) and download the installer for your operating system. Make sure to check the box that says "Add Python to PATH" during installation (especially on Windows).

---

**Setup Instructions:**

**Step 1: Get the Code**

1.  **Download the Code:**
    *   If you have Git installed: Open your terminal/command prompt and run:
        ```bash
        git clone https://github.com/AbdullahAbuHassann/ai-job-finder.git
        ```
    *   If you don't have Git: Go to the GitHub page ([https://github.com/AbdullahAbuHassann/ai-job-finder](https://github.com/AbdullahAbuHassann/ai-job-finder)), click the green "Code" button, and select "Download ZIP". Extract the ZIP file to a folder on your computer.

2.  **Navigate into the Project Folder:**
    Open your terminal/command prompt and change your directory to the folder where you downloaded or cloned the code. For example, if it's in a folder named `ai-job-finder` on your Desktop:
    ```bash
    # On macOS or Linux:
    cd Desktop/ai-job-finder

    # On Windows:
    cd Desktop\ai-job-finder
    ```
    You should now be inside the `ai-job-finder` (or `cv_job_matcher` if you renamed it) folder.

**Step 2: Create a Python Virtual Environment**

A virtual environment keeps the Python packages for this project separate from other Python projects on your computer. This is highly recommended.

1.  **Create the virtual environment:**
    While inside your project folder (`ai-job-finder`), run this command in your terminal:
    ```bash
    python3 -m venv venv
    ```
    (If `python3` doesn't work, try `python -m venv venv`)
    This will create a new folder named `venv` inside your project directory.

2.  **Activate the virtual environment:**
    *   **On macOS and Linux:**
        ```bash
        source venv/bin/activate
        ```
    *   **On Windows (Command Prompt):**
        ```bash
        venv\Scripts\activate.bat
        ```
    *   **On Windows (PowerShell):**
        ```bash
        .\venv\Scripts\Activate.ps1
        ```
        (If you get an error about script execution on PowerShell, you might need to run: `Set-ExecutionPolicy Unrestricted -Scope Process` first, then try activating again. You can set it back to `Restricted` later if you wish.)

    You'll know the virtual environment is active because your terminal prompt will usually change to show `(venv)` at the beginning.

**Step 3: Install Required Python Packages**

With the virtual environment active, you need to install the Python libraries the application depends on. These are listed in the `requirements.txt` file.

1.  **Install packages:**
    Run the following command in your terminal (make sure `(venv)` is still visible in your prompt):
    ```bash
    pip install -r requirements.txt
    ```
    This will download and install all the necessary libraries.

**Step 4: Set Up API Keys and Configuration (Important!)**

This application needs API keys for OpenAI (for AI features) and a password for Bright Data (for searching LinkedIn). These are like secret passwords that allow the application to use these services. You need to store them in a special file.

1.  **Create the `.env` file:**
    *   In your project's main folder (e.g., `ai-job-finder/`), create a new file and name it exactly `.env` (it starts with a dot and has no other extension like `.txt`).
    *   You can use a simple text editor (like Notepad on Windows, TextEdit on Mac - make sure TextEdit is in "Plain Text" mode, not "Rich Text").

2.  **Add your keys to the `.env` file:**
    Open the `.env` file you just created and paste the following lines into it:

    ```env
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
    BRIGHTDATA_ACTUAL_PASSWORD="YOUR_BRIGHTDATA_PROXY_PASSWORD_HERE"
    FLASK_DEBUG=True
    ```

3.  **Replace the placeholders with your actual keys:**

    *   **`YOUR_OPENAI_API_KEY_HERE`**:
        *   **What it is:** This key allows the app to use OpenAI's AI models (like GPT-4o) for analyzing your CV, scoring jobs, and tailoring your CV.
        *   **How to get it:**
            1.  Go to the OpenAI API platform: [platform.openai.com](https://platform.openai.com/)
            2.  Sign up for an account or log in if you already have one.
            3.  Navigate to the "API keys" section (usually in the left sidebar or under your account settings).
            4.  Click "Create new secret key". Give it a name (e.g., "CVJobMatcher").
            5.  **Copy the key immediately.** OpenAI will only show it to you once.
            6.  Paste this key into your `.env` file in place of `YOUR_OPENAI_API_KEY_HERE`.
        *   **Note:** Using the OpenAI API may incur costs depending on your usage. New accounts often come with some free credits.

    *   **`YOUR_BRIGHTDATA_PROXY_PASSWORD_HERE`**:
        *   **What it is:** This application is configured to use a specific Bright Data proxy username (`brd-customer-hl_158e0070-zone-mcp_unlocker`). This password is for that specific proxy user.
        *   **How to get it:**
            1.  This proxy username and password setup would typically be provided to you if you are using a pre-configured Bright Data account or zone for this project.
            2.  If you have your own Bright Data account, you would go to your "Proxies & Scraping Infrastructure" dashboard, find or create a zone that uses "Username-Password" authentication for datacenter or ISP proxies (the username in the code suggests a specific setup). The password would be associated with the username `brd-customer-hl_158e0070-zone-mcp_unlocker`.
            3.  **Important:** If you don't have this specific Bright Data setup or password, the LinkedIn job searching part of the application will not work. You might need to replace the hardcoded username in `app.py` (in the `BRIGHT_DATA_CONFIG` section) and use your own Bright Data proxy credentials.
            4.  Paste the correct password for the `brd-customer-hl_158e0070-zone-mcp_unlocker` user into your `.env` file.

    *   **`FLASK_DEBUG=True`**: This runs the app in debug mode, which is helpful for development as it provides more error details and auto-reloads when you save code changes. You can set it to `False` or remove this line for "production" use.

4.  **Save the `.env` file.** Make sure it's in the main project directory.

**Step 5: Run the Application!**

You're all set! Now you can start the web application.

1.  **Make sure your virtual environment is still active** (you should see `(venv)` in your terminal prompt). If not, reactivate it (see Step 2).
2.  **Run the main Python script:**
    While in your project folder, type the following command in your terminal and press Enter:
    ```bash
    python app.py
    ```
3.  **Look for output in the terminal:**
    You should see some messages, including something like:
    ```
    🚀 Starting CV Job Matcher Application...
    ✅ OpenAI Client (from ai_services.py) appears initialized.
    🌐 Bright Data: ✅ Proxy Password configured for user brd-customer-hl_158e0070.
    📝 Flow: Upload CV → AI Analysis → LinkedIn Search → Job URLs & People Search → AI CV Tailoring
     * Serving Flask app 'app'
     * Debug mode: on
    WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
     * Running on http://127.0.0.1:8080
    Press CTRL+C to quit
    ```
    The important part is `Running on http://127.0.0.1:8080` (the port might be different, but 8080 is common).

4.  **Open the application in your web browser:**
    Open your favorite web browser (Chrome, Firefox, Safari, Edge) and go to the address shown in the terminal:
    [http://127.0.0.1:8080](http://127.0.0.1:8080)

You should now see the application interface! You can upload your CV, enter a location, and start finding jobs.

**To Stop the Application:**
Go back to your terminal window where the application is running and press `Ctrl+C` (hold down the Control key and press C).

---

## How It Works (Brief Architecture & Components)

This application combines several technologies to provide its features:

1.  **Frontend (User Interface - `templates/index.html`):**
    *   This is what you see and interact with in your web browser.
    *   It's built with HTML (structure), CSS (styling), and JavaScript (interactivity, like handling file uploads and sending requests to the backend).
    *   When you upload a CV or click "Find Matches", the JavaScript in your browser sends this information to the backend.

2.  **Backend (The "Brain" - Python & Flask - `app.py`):**
    *   **Flask:** A Python web framework that receives requests from your browser (e.g., "here's a CV, find jobs") and sends back responses (e.g., "here are the matched jobs").
    *   **`app.py`:** The main file that defines the web routes (URLs) like `/` (the homepage), `/search_jobs`, and `/tailor_cv`. It coordinates the work.
    *   **Environment Variables (`.env`):** Securely stores your API keys so they are not written directly into the code. `python-dotenv` library helps load these.

3.  **CV Processing (`cv_utils.py`):**
    *   Handles file uploads, making sure they are allowed types (PDF, DOCX, etc.).
    *   Extracts the plain text content from your CV using libraries like `PyPDF2` (for PDFs) and `python-docx` (for Word documents).

4.  **AI Services (`ai_services.py`):**
    *   This module communicates with the **OpenAI API**.
    *   **OpenAI Client:** The official Python library for interacting with OpenAI.
    *   **CV Analysis:**
        *   *Prompt Used (Simplified):* "Analyze this CV: [CV Text]. Extract current role, experience, skills, industry, career level, and 5 target job titles. Respond in JSON."
        *   The extracted text from your CV is sent to an OpenAI model (GPT-4o).
        *   The AI returns structured information (JSON) about your CV.
    *   **Job Match Scoring:**
        *   *Prompt Used (Simplified):* "Candidate Profile: [CV Analysis Results]. Job Posting: [Job Title, Company, Description Snippet]. Score the match from 0.0 to 1.0 and give a brief reason. Is it relevant? Respond in JSON."
        *   For each job found, its details and your CV profile are sent to OpenAI (GPT-4o).
        *   The AI provides a match score and a reason.
    *   **CV Tailoring:**
        *   *Prompt Used (Simplified):* "Act as a resume expert. Original CV: [CV Text]. Job Info: [Job Details]. Create a new CV tailored for this job. Also, provide bullet-point recommendations on what to highlight. Respond in JSON with 'tailored_cv' and 'recommendations'."
        *   Your original CV text and the details of a specific job are sent to OpenAI (GPT-4o).
        *   The AI rewrites your CV to better fit the job and gives you tips.

5.  **LinkedIn Job Searching (`linkedin_services.py`):**
    *   **Bright Data Proxy:** To search LinkedIn for jobs without being quickly blocked, the application uses a proxy service from Bright Data. Your requests to LinkedIn go through Bright Data's servers.
        *   The `BRIGHT_DATA_CONFIG` in `app.py` (using your `BRIGHTDATA_ACTUAL_PASSWORD` from `.env`) sets up this proxy connection.
    *   **Smart Search Terms:** Uses the roles and skills identified by the AI from your CV to create effective search queries for LinkedIn.
    *   **Web Scraping (`requests` & `BeautifulSoup4`):**
        *   The `requests` library makes the actual HTTP requests to LinkedIn (via the proxy).
        *   `BeautifulSoup4` is used to parse the HTML content returned by LinkedIn, extracting job details like title, company, location, and URL from the messy web page code.
    *   **People Search Links:** Constructs direct LinkedIn search URLs to help you find people (recruiters, hiring managers) at the companies of the matched jobs.

**Overall Flow:**

1.  You upload a CV and enter a location on the webpage.
2.  Browser sends this to `app.py` (`/search_jobs` route).
3.  `cv_utils.py` extracts text from your CV.
4.  `ai_services.py` sends CV text to OpenAI for analysis.
5.  `linkedin_services.py` uses AI analysis and your location to search LinkedIn via Bright Data, then parses results.
6.  `ai_services.py` scores each found job against your CV using OpenAI.
7.  `app.py` sends the processed, scored, and enhanced job list back to your browser to be displayed.
8.  If you click "Tailor CV", your browser sends the original CV text and job details to `app.py` (`/tailor_cv` route).
9.  `ai_services.py` sends this to OpenAI to generate a tailored CV and recommendations.
10. `app.py` sends this back to your browser for display in a modal.

---

## Troubleshooting Common Issues

*   **"OpenAI API key not found" / "OpenAI client not initialized":**
    *   Double-check your `.env` file is in the project root and correctly named (`.env`).
    *   Ensure `OPENAI_API_KEY="your_key"` is in the `.env` file with your actual key.
    *   Make sure you restarted the `python app.py` command after creating/editing `.env`.
*   **"Bright Data: Proxy Password NOT configured":**
    *   Ensure `BRIGHTDATA_ACTUAL_PASSWORD="your_password"` is in your `.env` file with the correct password for the proxy user `brd-customer-hl_158e0070-zone-mcp_unlocker`.
    *   Restart `python app.py`.
*   **No jobs found / LinkedIn search errors:**
    *   The Bright Data proxy might be having issues, or your password might be incorrect.
    *   LinkedIn may have changed its website structure, which can break the scraping part. This is a common challenge with web scraping.
*   **`ModuleNotFoundError`:**
    *   Make sure your virtual environment is active (`(venv)` in prompt).
    *   Ensure you ran `pip install -r requirements.txt` successfully while the virtual environment was active.
*   **Permission errors (especially on PowerShell for `Activate.ps1`):**
    *   Try running `Set-ExecutionPolicy Unrestricted -Scope Process` in PowerShell before activating the virtual environment.

We hope you find this tool helpful in your job search!
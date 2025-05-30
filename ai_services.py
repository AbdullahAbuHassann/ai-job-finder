# ai_services.py
import openai
import os
import json
from dotenv import load_dotenv
from pathlib import Path # For easier path manipulation

# --- Enhanced .env loading and debugging ---
# This section tries to locate and load the .env file robustly.
# It assumes ai_services.py is in the root of your project (e.g., cv_job_matcher/ai_services.py)
# and your .env file is also in the root (cv_job_matcher/.env).

# Get the directory where this ai_services.py file is located.
# Path(__file__) gives the path to the current file (ai_services.py).
# .parent gives its directory.
current_script_directory = Path(__file__).resolve().parent
# Assume the .env file is in the same directory as this script.
# This is a common setup if your project root contains both ai_services.py and .env
dotenv_path_to_try = current_script_directory / ".env"

print(f"DEBUG [ai_services.py]: Current Working Directory (os.getcwd()): {os.getcwd()}")
print(f"DEBUG [ai_services.py]: Path to this script (__file__): {Path(__file__).resolve()}")
print(f"DEBUG [ai_services.py]: Calculated current_script_directory: {current_script_directory}")
print(f"DEBUG [ai_services.py]: Attempting to load .env from specific path: {dotenv_path_to_try}")

if dotenv_path_to_try.exists():
    print(f"DEBUG [ai_services.py]: Found .env file at: {dotenv_path_to_try}")
    # Load the .env file from the specific path.
    # override=True means if variables are already in the environment (e.g. system-wide),
    # the ones from .env will take precedence. Useful for ensuring .env is respected.
    load_dotenv(dotenv_path=dotenv_path_to_try, override=True)
    print(f"DEBUG [ai_services.py]: load_dotenv() called with specific path: {dotenv_path_to_try}")
else:
    print(f"DEBUG [ai_services.py]: .env file NOT found at specific path: {dotenv_path_to_try}")
    print(f"DEBUG [ai_services.py]: Attempting fallback load_dotenv() (will search CWD and parent dirs).")
    # If the specific path didn't work, try the default behavior of load_dotenv(),
    # which searches the current working directory and then parent directories.
    # This is a fallback in case the path calculation was incorrect for your setup.
    load_dotenv(override=True)
    print(f"DEBUG [ai_services.py]: Fallback load_dotenv() called.")


# Now, try to get the API key from the environment after attempting to load .env
OPENAI_API_KEY_FROM_ENV = os.getenv('OPENAI_API_KEY')
print(f"DEBUG [ai_services.py]: Value of OPENAI_API_KEY after all load attempts: '{OPENAI_API_KEY_FROM_ENV}'")
# --- End of enhanced .env loading ---

# Initialize OpenAI client within this module
openai_client = None # Default to None

if OPENAI_API_KEY_FROM_ENV:
    try:
        # Use the key retrieved from the environment
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY_FROM_ENV)
        print("✅ OpenAI client initialized successfully (ai_services.py)")
    except Exception as e:
        print(f"❌ Error initializing OpenAI client in ai_services.py: {e}")
        openai_client = None # Ensure client is None if initialization fails
else:
    # This message means OPENAI_API_KEY_FROM_ENV was None or empty
    print("⚠️ OpenAI API key was NOT found in the environment by ai_services.py.")
    print("   Please ensure:")
    print("   1. Your .env file is in the project root directory (e.g., alongside app.py).")
    print("   2. The .env file contains the line: OPENAI_API_KEY=\"your_actual_key_here\"")
    print("   3. The script has permissions to read the .env file.")
    print("   (AI services will not function without the API key.)")


# --- Your working AI functions (copied from your provided code) ---

def analyze_cv_with_ai(cv_text):
    if not openai_client:
        # This exception will be caught by the calling route in app.py
        raise Exception("OpenAI client is not initialized in ai_services. Cannot analyze CV.")
    
    prompt = f"""
    Analyze this CV and extract information for LinkedIn job search:
    CV TEXT:
    {cv_text}
    Extract:
    1. Current job title/role (be very specific)
    2. Years of experience
    3. Top 5 technical skills (only explicitly mentioned skills)
    4. Industry/field (based on actual experience)
    5. Career level (Junior/Mid/Senior/Executive)
    6. What job titles they should search for on LinkedIn (5 realistic titles matching experience)
    IMPORTANT: 
    - Only suggest job titles directly related to their experience.
    - Be precise and accurate based on the CV content.
    Respond ONLY with valid JSON:
    {{
        "current_role": "Current job title",
        "experience_years": 5,
        "technical_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
        "industry": "Industry name",
        "career_level": "Senior",
        "target_job_titles": ["title1", "title2", "title3", "title4", "title5"]
    }}
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a career analyst. Extract job search information from CVs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as e:
        print(f"AI analysis failed: {e}")
        # Re-raise the exception so the calling function in app.py can handle it and return a proper JSON error
        raise

def calculate_job_match_score(job, cv_analysis):
    if not openai_client:
        print("⚠️ OpenAI client not initialized (ai_services) - cannot calculate match scores, returning default 0.5")
        job['match_reasoning'] = 'OpenAI client not available for scoring (ai_services).'
        return 0.5 # Return a default float score
    
    job_description_for_scoring = job.get('description', f"{job.get('title')} at {job.get('company')}")
    if "Details for" in job_description_for_scoring and "available on LinkedIn" in job_description_for_scoring:
        job_description_for_scoring = f"Seeking a {job.get('title')} at {job.get('company')} in {job.get('location', 'specified location')}."

    prompt = f"""
    Analyze if this job is a good match for this candidate:
    CANDIDATE PROFILE:
    - Current Role: {cv_analysis.get('current_role', 'N/A')}
    - Years of Experience: {cv_analysis.get('experience_years', 'N/A')}
    - Technical Skills: {', '.join(cv_analysis.get('technical_skills', []))}
    - Industry: {cv_analysis.get('industry', 'N/A')}
    - Career Level: {cv_analysis.get('career_level', 'N/A')}
    - Target Roles: {', '.join(cv_analysis.get('target_job_titles', []))}
    JOB POSTING (brief summary):
    - Title: {job.get('title', 'N/A')}
    - Company: {job.get('company', 'N/A')}
    - Location: {job.get('location', 'N/A')}
    - Description Snippet: {job_description_for_scoring[:300]} 
    Evaluate the match. Respond with ONLY a JSON object:
    {{
        "match_score": 0.85,
        "reasoning": "Brief explanation (max 20 words).",
        "is_relevant": true
    }}
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o", # Consistent with your working file
            messages=[
                {"role": "system", "content": "You are a highly efficient career matching expert. Evaluate job-candidate fit and provide a concise score and reasoning. Be strict with `is_relevant` if the job is clearly unsuitable."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.05, max_tokens=150,
            response_format={"type": "json_object"}
        )
        result_content = response.choices[0].message.content.strip()
        match_data = json.loads(result_content)
        job['match_reasoning'] = match_data.get('reasoning', 'AI could not provide a reason.') # Set reasoning on the job object
        
        print(f"🤖 AI Match for '{job.get('title')}': {match_data.get('match_score', 0):.0%} - {match_data.get('reasoning', '')} (Relevant: {match_data.get('is_relevant', True)})")
        
        if not match_data.get('is_relevant', True): 
            return 0.0 # Return float score
        return float(match_data.get('match_score', 0.3)) # Return float score
    except Exception as e:
        print(f"❌ AI matching error for job '{job.get('title', 'Unknown Job')}': {e}. Returning default score 0.4")
        job['match_reasoning'] = 'Error during AI scoring.' # Set reasoning on error
        return 0.4 # Return default float score

def tailor_cv_with_ai(original_cv_text, job_details):
    if not openai_client:
        raise Exception("OpenAI client is not initialized in ai_services. Cannot tailor CV.")

    job_description_for_prompt = f"""
    Title: {job_details.get('title', 'N/A')}
    Company: {job_details.get('company', 'N/A')}
    Location: {job_details.get('location', 'N/A')}
    URL: {job_details.get('url', 'N/A')}
    Description: {job_details.get('description', 'No detailed description provided. Focus on title, company, and infer requirements.')}
    """
    prompt_content = f"""
    Act like a seasoned career consultant and resume expert specializing in crafting tailor-made resumes for job seekers.
    You have a deep understanding of what hiring managers in various industries look for in candidates, particularly for roles advertised on LinkedIn. Your expertise includes transforming LinkedIn job descriptions into compelling CV content.
    Here’s my original CV:
    <CV>
    {original_cv_text}
    </CV>
    Feel free to be creative & expand it based on the job.
    Your task is to help me land this specific job advertised on LinkedIn. It's very important for my career.
    Here's the job information:
    <job_information>
    {job_description_for_prompt}
    </job_information>
    Based on my CV and the job information, please perform the following two tasks:
    1.  **Generate a Tailored CV**: Write a whole new CV, based on my original one, but meticulously tailored to the provided job information. Use professional CV formatting (use newline characters \\n for line breaks and structure). Make it comprehensive and impactful, highlighting how my experience and skills align with the job requirements. Do not explain what you are doing in this part, just provide the CV text. Make it as strong as possible.
    2.  **Provide Actionable Recommendations**: Give me back recommendations in bullet points on what specific aspects, skills, or experiences from my original CV I absolutely NEED to highlight, expand upon, or quantify to make my application stand out for THIS particular job. Also, suggest if there are any key things from the job information that I should try to address in my CV, even if they are not explicitly in my original CV.
    Take a deep breath and work on this problem step-by-step.
    Respond ONLY with a valid JSON object in the following format, with no explanations or markdown formatting before or after the JSON:
    {{
        "tailored_cv": "The full text of the tailored CV, with appropriate formatting (e.g., using newline characters \\n for line breaks).",
        "recommendations": [
            "Bullet point recommendation 1...",
            "Bullet point recommendation 2...",
            "..."
        ]
    }}
    """
    try:
        print(f"🤖 Starting AI CV tailoring for job: {job_details.get('title')}")
        response = openai_client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": "You are an expert career consultant and resume writer. Follow instructions precisely and provide output in the specified JSON format."},
                {"role": "user", "content": prompt_content}
            ],
            temperature=0.4,
            max_tokens=3800,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content.strip()
        print(f"✅ AI CV tailoring complete for: {job_details.get('title')}")
        return json.loads(content)
    except Exception as e:
        print(f"❌ AI CV tailoring failed for job '{job_details.get('title', 'Unknown')}': {e}")
        # Check if it's an OpenAI specific error type for more detailed logging if needed
        # For example, if using an older SDK, openai.error.APIError might be relevant
        # For newer SDK (>=1.0.0), errors are like openai.APIError, openai.AuthenticationError, etc.
        if hasattr(e, 'http_status') or "OpenAI" in str(type(e)): # A heuristic check
             print(f"   OpenAI API Related Error: Status {getattr(e, 'http_status', 'N/A')} - Message: {getattr(e, 'message', str(e))}")
        # Re-raise so app.py can catch it and return a JSON error to the client
        raise
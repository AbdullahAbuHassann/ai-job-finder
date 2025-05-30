#!/usr/bin/env python3
"""
CV Job Matcher - Main Application (Simplified Config)
"""
from flask import Flask, request, jsonify, render_template # render_template_string removed
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
import urllib3
import traceback
from urllib.parse import quote # For people search URL
from datetime import datetime # For health check

# Ensure environment variables are loaded AT THE VERY TOP
# This is critical for other modules that might initialize using os.getenv() at import time.
load_dotenv()
print("DEBUG [app.py]: load_dotenv() called.") # For checking if this line runs

# Import from our modules AFTER load_dotenv()
# The 'openai_client' from ai_services will be the one initialized within that module
from cv_utils import save_uploaded_file, extract_cv_text_from_file, cleanup_file
# Import specific functions and the client instance
from ai_services import analyze_cv_with_ai, calculate_job_match_score, tailor_cv_with_ai, openai_client as ai_services_openai_client
from linkedin_services import search_linkedin_jobs, parse_linkedin_html # Import parse_linkedin_html if still needed here, though likely only in linkedin_services

# Disable SSL warnings for proxy
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__) # Flask app instance
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads' # cv_utils uses 'uploads' directly for now, or pass app.config['UPLOAD_FOLDER']
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# --- Bright Data Configuration ---
# Load password from .env. Use a specific variable name like BRIGHTDATA_ACTUAL_PASSWORD
# to avoid confusion with any other Bright Data tokens.
BRIGHTDATA_PROXY_PASSWORD_FROM_ENV = os.getenv('BRIGHTDATA_ACTUAL_PASSWORD')

BRIGHT_DATA_CONFIG = {
    'host': 'brd.superproxy.io',
    'port': '33335',
    'username': 'brd-customer-hl_158e0070-zone-mcp_unlocker', # This is from your original code
    'password': BRIGHTDATA_PROXY_PASSWORD_FROM_ENV # Use the loaded password
}

# --- Initial Checks and Prints (After all initializations) ---
print("🚀 Starting CV Job Matcher Application...")

# Check the OpenAI client that was initialized in ai_services.py
if ai_services_openai_client: # Check the imported client instance
    print("✅ OpenAI Client (from ai_services.py) appears initialized.")
else:
    print("❌ OpenAI Client (from ai_services.py) FAILED to initialize.")
    print("   Check OPENAI_API_KEY in .env and initialization logic in ai_services.py.")

# Check Bright Data Password
if BRIGHT_DATA_CONFIG.get('password') and BRIGHT_DATA_CONFIG['password'] != 'YOUR_BRIGHTDATA_PASSWORD_PLACEHOLDER': # Add a distinct placeholder
    print(f"🌐 Bright Data: ✅ Proxy Password configured for user {BRIGHT_DATA_CONFIG['username'].split('-zone-')[0]}.")
else:
    print("❌ Bright Data: Proxy Password NOT configured. Check BRIGHTDATA_ACTUAL_PASSWORD in .env.")
print("📝 Flow: Upload CV → AI Analysis → LinkedIn Search → Job URLs & People Search → AI CV Tailoring")


@app.route('/')
def index_route(): # Renamed from 'index' to avoid conflict if any built-in 'index' exists
    """Serve the main HTML page from templates folder"""
    return render_template('index.html') # This will look for templates/index.html

@app.route('/search_jobs', methods=['POST'])
def search_jobs_route_handler(): # Renamed function
    filepath = None
    raw_cv_text_for_response = "CV text not extracted due to an early error."

    try:
        if 'cv_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['cv_file']
        location_input = request.form.get('location', 'Worldwide')
        
        if not file or file.filename == '': # Check if file object exists and has a filename
            return jsonify({'success': False, 'error': 'No file selected or file object missing.'}), 400
        
        # Pass app.config['UPLOAD_FOLDER'] to ensure it uses the Flask configured path
        filepath, unique_filename = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        if not filepath:
            return jsonify({'success': False, 'error': 'File could not be saved or is not allowed.'}), 400

        raw_cv_text = extract_cv_text_from_file(filepath, unique_filename)
        raw_cv_text_for_response = raw_cv_text # Update for successful extraction

        if not raw_cv_text or len(raw_cv_text.strip()) < 30:
            cleanup_file(filepath) # Cleanup before returning
            return jsonify({'success': False, 'error': 'Could not extract sufficient text from CV. Please ensure it has readable content.'}), 400
        
        print(f"📄 CV text extracted: {len(raw_cv_text)} characters from {unique_filename}")

        # Use the imported ai_services_openai_client for check
        if not ai_services_openai_client:
            raise Exception("OpenAI client (from ai_services) is not initialized. Cannot proceed with CV analysis.")
        
        cv_analysis = analyze_cv_with_ai(raw_cv_text) # Uses client from ai_services
        print(f"🤖 CV analysis: {cv_analysis.get('current_role', 'N/A')} with {cv_analysis.get('experience_years', 0)} years")
        
        # Pass the BRIGHT_DATA_CONFIG from app.py
        linkedin_jobs_raw = search_linkedin_jobs(cv_analysis, location_input, BRIGHT_DATA_CONFIG, max_results=20)
        print(f"🎯 Found {len(linkedin_jobs_raw)} LinkedIn jobs initially (app.py)")
        
        relevant_jobs = []
        jobs_to_score = linkedin_jobs_raw[:30]

        print("\n🤖 AI Scoring job matches...")
        for job in jobs_to_score:
            try:
                # Check client again just before use, though it should be the same instance
                if not ai_services_openai_client:
                    print(f"  ⚠️ OpenAI client not available for scoring job '{job.get('title','Untitled Job')}'. Assigning default score.")
                    job['match_score'] = 0.3 
                    job['match_reasoning'] = 'OpenAI client unavailable for scoring.'
                    # Fall through to append if you still want to show it, or skip
                else:
                    # calculate_job_match_score uses the client from ai_services
                    match_score = calculate_job_match_score(job, cv_analysis) 
                
                if match_score > 0.35:
                    job['match_score'] = match_score
                    relevant_jobs.append(job)
                else:
                    print(f"  🗑️ Filtered out (low score/not relevant): {job.get('title','Untitled Job')} (Score: {match_score:.0% if isinstance(match_score, float) else 'N/A'})")
            except Exception as match_err:
                print(f"  ⚠️ Error scoring job '{job.get('title','Untitled Job')}': {match_err}. Assigning default.")
                job['match_score'] = 0.3 
                job['match_reasoning'] = 'Error during AI scoring process.'
                relevant_jobs.append(job) # Add with default if scoring failed but we want to show it
        
        relevant_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        relevant_jobs = relevant_jobs[:15]
        print(f"\n✅ Kept {len(relevant_jobs)} relevant jobs after AI scoring.")

        for job_info in relevant_jobs:
            job_company_search = job_info.get('company', '')
            job_loc_for_people = job_info.get('location', location_input)
            if job_loc_for_people and job_loc_for_people.lower() == "remote":
                job_loc_for_people = location_input

            if job_company_search and job_loc_for_people:
                contacts_terms = f"Recruiter OR \"Talent Acquisition\" OR \"Hiring Manager\" OR Manager"
                query_company_contacts = f"({contacts_terms}) AND \"{job_company_search}\" AND \"{job_loc_for_people}\""
                job_info['linkedin_people_search_company_contacts_url'] = \
                    f"https://www.linkedin.com/search/results/people/?keywords={quote(query_company_contacts)}&origin=GLOBAL_SEARCH_HEADER&sid=)"
            else:
                job_info['linkedin_people_search_company_contacts_url'] = None
        
        cleanup_file(filepath) # Cleanup successful processing
        return jsonify({
            'success': True, 'jobs': relevant_jobs,
            'cv_analysis': cv_analysis,
            'raw_cv_text': raw_cv_text,
            'filtered_count': len(jobs_to_score) - len(relevant_jobs)
        })
            
    except Exception as e:
        cleanup_file(filepath) # Ensure cleanup on any exception
        print(f"❌ Error in /search_jobs: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': f'An error occurred during processing: {str(e)}',
            'raw_cv_text': raw_cv_text_for_response 
        }), 500

@app.route('/tailor_cv', methods=['POST'])
def tailor_cv_route_handler(): # Renamed function
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid request: No JSON payload.'}), 400

        original_cv_text = data.get('original_cv_text')
        job_details = data.get('job_details')

        if not original_cv_text or not job_details:
            return jsonify({'success': False, 'error': 'Missing original_cv_text or job_details.'}), 400
        
        if not job_details.get('title') or not job_details.get('company'):
             return jsonify({'success': False, 'error': 'Job details missing title or company.'}), 400

        # Use the imported client instance
        if not ai_services_openai_client:
             return jsonify({'success': False, 'error': 'OpenAI client (from ai_services) not configured on server.'}), 500
        
        print(f"⚡ Request to tailor CV for job: {job_details.get('title')} at {job_details.get('company')}")
        # tailor_cv_with_ai uses the client from ai_services
        tailoring_results = tailor_cv_with_ai(original_cv_text, job_details)
        return jsonify({'success': True, 'data': tailoring_results})

    except Exception as e:
        print(f"❌ Error during CV tailoring in /tailor_cv: {e}")
        traceback.print_exc()
        error_message = str(e)
        # A simple check for OpenAI related errors
        if "OpenAI" in str(type(e)) or (hasattr(e, 'http_status') and e.http_status in [401, 429]):
            error_message = f"OpenAI API Error: {getattr(e, 'message', str(e))}"
        return jsonify({'success': False, 'error': f'Failed to tailor CV: {error_message}'}), 500

@app.route('/health')
def health_route(): # Renamed function
    """Health check"""
    # Use the password from BRIGHT_DATA_CONFIG which was populated from .env
    bd_password_is_set = bool(BRIGHT_DATA_CONFIG.get('password') and \
                              BRIGHT_DATA_CONFIG['password'] != 'YOUR_BRIGHTDATA_PASSWORD_PLACEHOLDER' and \
                              BRIGHT_DATA_CONFIG['password'] is not None) # More robust check

    return jsonify({
        'status': 'healthy',
        'openai_client_initialized_in_ai_services': bool(ai_services_openai_client),
        'bright_data_proxy_password_configured': bd_password_is_set,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Read FLASK_DEBUG from .env, default to False if not set or invalid
    flask_debug_env = os.getenv("FLASK_DEBUG", "False").lower()
    debug_mode = True if flask_debug_env == "true" else False
    
    port = int(os.environ.get("PORT", 8080))
    print(f"Running Flask app in {'DEBUG' if debug_mode else 'PRODUCTION (default)'} mode on port {port}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
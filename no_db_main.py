"""
No-database Flask application for the Remote Work Job Board.
This version has no database dependencies to ensure fast startup.
"""
from flask import Flask, render_template_string

# Create a simple Flask app with no DB dependencies
app = Flask(__name__)

# Sample jobs data for display
SAMPLE_JOBS = [
    {
        'id': 1,
        'title': 'Remote Software Engineer',
        'company': 'TechCorp',
        'location': 'Worldwide',
        'job_type': 'Full-time',
        'category': 'Technology',
        'posted_date': '2025-03-20'
    },
    {
        'id': 2,
        'title': 'Content Writer',
        'company': 'ContentHub',
        'location': 'Remote - US',
        'job_type': 'Contract',
        'category': 'Creative',
        'posted_date': '2025-03-22'
    },
    {
        'id': 3,
        'title': 'Product Manager',
        'company': 'ProductLabs',
        'location': 'Remote - Europe',
        'job_type': 'Full-time',
        'category': 'Management',
        'posted_date': '2025-03-23'
    }
]

@app.route('/')
def index():
    """Homepage with static sample jobs"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Remote Work Job Board</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .job-list {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
            }
            .job-card {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .job-title {
                color: #4a6ee0;
                margin-top: 0;
            }
            .job-company {
                font-weight: bold;
            }
            .job-meta {
                color: #666;
                font-size: 0.9em;
                margin: 10px 0;
            }
            .button {
                display: inline-block;
                background-color: #4a6ee0;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                text-decoration: none;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Remote Work Job Board</h1>
            <p>Find the best remote jobs from around the world</p>
        </div>
        
        <div class="job-list">
            {% for job in jobs %}
            <div class="job-card">
                <h3 class="job-title">{{ job.title }}</h3>
                <div class="job-company">{{ job.company }}</div>
                <div class="job-meta">
                    📍 {{ job.location }} <br>
                    🔖 {{ job.category }} <br>
                    💼 {{ job.job_type }} <br>
                    📅 Posted: {{ job.posted_date }}
                </div>
                <a href="/job/{{ job.id }}" class="button">View Details</a>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html, jobs=SAMPLE_JOBS)

@app.route('/health')
def health():
    """Health check endpoint"""
    return '{"status":"ok"}', 200, {'Content-Type': 'application/json'}

# For direct execution
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
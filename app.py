from flask import Flask, request, redirect, url_for, jsonify, render_template
from database import engine
from sqlalchemy import text
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

app = Flask(__name__)
# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'ha5403905@gmail.com'
app.config['MAIL_PASSWORD'] = 'cvzv flth kksx ohjr'
app.config['MAIL_DEFAULT_SENDER'] = 'ha5403905@gmail.com'


mail = Mail(app)

app.config['RESUME'] = os.path.join(os.getcwd(), 'UPLOADS')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_jobs_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("select * from jobs"))
        jobs = []
        for row in result.all():
            jobs.append(row)
    return jobs


def add_application_to_db(job_id, data):
    try:
        with engine.connect() as conn:
            with conn.begin():
                query = text("INSERT INTO applications (job_id, full_name, email, linkedin_url, education, work_experience, resume_name) VALUES (:job_id, :full_name, :email, :linkedin_url, :education, :work_experience, :resume_name)")
                conn.execute(query, {
                    'job_id': job_id,
                    'full_name': data['full_name'],
                    'email': data['email'],
                    'linkedin_url': data['linkedin_url'],
                    'education': data['education'],
                    'work_experience': data['work_experience'],
                    'resume_name': data['resume_name']
                })
        return True
    except Exception as e:
        print(f"Database Exception: {e}")
        return False
    
def send_contact_email(name, email, content):
    print("Attempting to send email...")

    # Set up the email message
    subject = 'New Contact Form Submission'
    body = f'Name: {name}\nEmail: {email}\nContent: {content}'
    recipients = ['ha5403905@gmail.com']

    try:
        # Debugging statements
        print(f"Subject: {subject}")
        print(f"Recipients: {recipients}")
        print(f"Body: {body}")

        # Send the email
        msg = Message(subject, recipients=recipients, body=body)
        mail.send(msg)
        print("Email sent successfully")

    except Exception as e:
        # Log the exception or print it for debugging
        print(f"Error sending email: {e}")
        raise  # Re-raise the exception to propagate it up the call stack


@app.route('/')
def home():
    jobs=load_jobs_from_db()
    return render_template('home.html', jobs=jobs)

@app.route('/job_details/<job_title>')
def job_details(job_title):
    jobs = load_jobs_from_db()
    
    # Find the job details based on the job_title
    job = next((job for job in jobs if job[1] == job_title), None)
    print(job)
    if job:
        # Assuming job is a tuple, you can convert it to a dictionary
        job_dict = {
            'id': job[0],
            'title': job[1],
            'location': job[2],
            'salary': job[3],
            'responsibilities': job[4],
            'requirements': job[5],
            # Add other columns as needed
        }
        return render_template('job_details.html', job=job_dict)
    else:
        # Handle the case where the job title is not found
        return render_template('job_not_found.html', job_title=job_title)

@app.route('/submit_application/<int:job_id>', methods=['POST'])
def submit_application(job_id):
    try:
        data = {
            'full_name': request.form.get('name'),
            'email': request.form.get('email'),
            'linkedin_url': request.form.get('linkedin'),
            'education': request.form.get('education'),
            'work_experience': request.form.get('experience'),
            'resume_name': '',
        }

        # Check if the post request has the file part
        if 'resume' in request.files:
            file = request.files['resume']
            # If the user does not select a file, the browser submits an empty file without a filename
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['RESUME'], filename))
                data['resume_name'] = filename
            else:
                return "Invalid file format for resume"
            
        print("Data before DB insert:", data)

        if add_application_to_db(job_id, data):
            print("Application submitted successfully")
            # Redirect to the success URL
            return redirect(url_for('success'))
        else:
            print("Failed to submit application to the database")
            # Handle the case where data couldn't be saved
            return "Failed to submit application"

    except Exception as e:
        # Log the exception or handle it as needed
        print(f"Exception: {e}")
        return "An error occurred"


@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        email = request.form.get('email')
        content = request.form.get('content')

        # Perform any processing or validation as needed

        try:
            # Send email
            send_contact_email(name, email, content)
            print("Email sent successfully")
            return redirect(url_for('home'))

        except Exception as e:
            # Log the exception or handle it as needed
            print(f"Error sending email: {e}")
            return "An error occurred while sending the email"

    # Handle cases where the form is not submitted via POST
    return "Invalid request"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

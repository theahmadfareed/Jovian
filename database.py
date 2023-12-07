from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

host = os.environ['host']
user = os.environ['user']
password = os.environ['password']
db = os.environ['db']

# Create the connection URL
db_url = f"mysql+pymysql://{user}:{password}@{host}/{db}"

# Create the SQLAlchemy engine
engine = create_engine(db_url)

if engine.connect():
    print("DB Connected")


def load_jobs_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("select * from jobs"))
    jobs = []
    for row in result.all():
      jobs.append(dict(row))
    return jobs

def load_job_from_db(id):
  with engine.connect() as conn:
    result = conn.execute(
      text("SELECT * FROM jobs WHERE id = :val"),
      val=id
    )
    rows = result.all()
    if len(rows) == 0:
      return None
    else:
      return dict(rows[0])


def add_application_to_db(job_id, data):
  with engine.connect() as conn:
    query = text("INSERT INTO applications (job_id, full_name, email, linkedin_url, education, work_experience, resume_url) VALUES (:job_id, :full_name, :email, :linkedin_url, :education, :work_experience, :resume_url)")

    conn.execute(query, 
                job_id=job_id, 
                full_name=data['full_name'],
                email=data['email'],
                linkedin_url=data['linkedin_url'],
                education=data['education'],
                work_experience=data['work_experience'],
                resume_url=data['resume_url'])
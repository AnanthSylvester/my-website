import smtplib
import re
import time
import csv
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from PyPDF2 import PdfReader
import os

# ---------------- CONFIG (UPDATED FILENAMES) ----------------
PDF_PATH = "STS_Job Poster Emails_Dec-2025.pdf"
RESUME_PATH = "Ananthraj.pdf"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = "ananthrajm14@gmail.com"
APP_PASSWORD = "ylgnpgjxxaieqxam"

MAX_EMAILS_PER_DAY = 200      # safer as suggested in the PDF
DELAY_SECONDS = 8

SENT_FILE = "sent_emails.txt"
REPORT_FILE = "report.csv"
# -----------------------------------------------------------

SUBJECT = "QA / Automation Tester – Immediate Joiner"

BODY = """Hi,

Got to know that you are hiring. I am looking for a  Automation or manual position.

Current Role: Technical consultant  
Current Location: Chennai  
Experience: Nearly 4 Years  
Skills: Selenium, Java, Cucumber, Manual & Automation Testing  
Tools: Selenium, TestNG, Jira, Postman, Jenkins  

Attached is my resume for your reference.
Please share it with your colleagues if relevant.

Thanks & regards,
Ananthraj
"""

# -------- Extract Emails from PDF --------
def extract_emails_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    return list(set(re.findall(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)))

# -------- Load Sent Emails --------
def load_sent_emails():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r") as f:
        return set(line.strip() for line in f)

# -------- Save Sent Email --------
def save_sent_email(email):
    with open(SENT_FILE, "a") as f:
        f.write(email + "\n")

# -------- Write Report --------
def write_report(email, status, error=""):
    file_exists = os.path.exists(REPORT_FILE)
    with open(REPORT_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Email", "Status", "Error", "DateTime"])
        writer.writerow([email, status, error, datetime.now()])

# -------- Send Email --------
def send_email(server, to_email):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = SUBJECT

    msg.attach(MIMEText(BODY, "plain"))

    with open(RESUME_PATH, "rb") as f:
        attachment = MIMEApplication(f.read(), _subtype="pdf")
        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename="Ananthraj_Resume.pdf"
        )
        msg.attach(attachment)

    server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

# ---------------- MAIN ----------------
if __name__ == "__main__":
    all_emails = extract_emails_from_pdf(PDF_PATH)
    sent_emails = load_sent_emails()

    pending_emails = [e for e in all_emails if e not in sent_emails]
    today_emails = pending_emails[:MAX_EMAILS_PER_DAY]

    print(f"📧 Total emails found: {len(all_emails)}")
    print(f"⏳ Pending emails: {len(pending_emails)}")
    print(f"🚀 Sending today: {len(today_emails)}")

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, APP_PASSWORD)

    for email in today_emails:
        try:
            send_email(server, email)
            save_sent_email(email)
            write_report(email, "SUCCESS")
            print(f"✅ Sent → {email}")
            time.sleep(DELAY_SECONDS)
        except Exception as e:
            write_report(email, "FAILED", str(e))
            print(f"❌ Failed → {email}")

    server.quit()
    print("🎯 Done. Run again tomorrow to auto-resume.")





# SUBJECTS = [
#   "Test Automation Engineer| 4 Yrs",
#   "QA / Automation Tester – Immediate Joiner",
#   "Selenium Automation Tester Resume"
# ]

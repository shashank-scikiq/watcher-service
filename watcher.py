import asyncio
import aiohttp
import smtplib
from email.mime.text import MIMEText
import schedule
import time
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, send_file
from dotenv import load_dotenv
import os
import configs as cfg
import sys

try:
    load_dotenv(".env")
except Exception as e:
    print(e.args[0])
else:
    print("Env Loaded Successfully")


endpoints = [
    cfg.server_ips["Stage"],
    cfg.server_ips["Prod"],
    cfg.server_ips["EC2_8082"]
]

SMTP_SERVER = os.getenv("SMTP_SERVER", default=None)
SMTP_PORT = os.getenv("SMTP_PORT", default=None)
SMTP_USER = os.getenv("SMTP_USER", default=None)
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", default=None)
TO_EMAIL = os.getenv("TO_EMAIL", default=None)

MAX_RETRIES = int(os.getenv("MAX_RETRIES"))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL")) *60

if os.path.exists("endpoint_checker.log"):
    os.remove("endpoint_checker.log")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("endpoint_checker.log"),
                              logging.StreamHandler()])

# Send Email
# ===========================================================================

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = TO_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, TO_EMAIL, msg.as_string())

# Check Endpoints
# ===========================================================================
async def check_endpoint(session, url, retries=0, results=None):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                logging.info(f"Endpoint {url} is up.")
            else:
                logging.warning(f"Endpoint {url} returned status code {response.status}.")
                results.append((url, response.status))
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logging.error(f"Error checking {url}: {e}")
        if retries < MAX_RETRIES:
            logging.info(f"Retrying {url} ({retries+1}/{MAX_RETRIES})...")
            await asyncio.sleep(2)  # Wait before retrying
            await check_endpoint(session, url, retries + 1, results)
        else:
            logging.error(f"Max retries reached for {url}. Adding to alert list.")
            results.append((url, 'Max retries reached'))

async def check_all_endpoints():
    logging.info("Starting endpoint check.")
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = [check_endpoint(session, url, results=results) for url in endpoints]
        await asyncio.gather(*tasks)

    if results:
        error_summary = '\n'.join([f"{url}: {status}" for url, status in results])
        send_email(
            subject="Endpoint Issues Detected",
            body=f"The following endpoints returned errors:\n{error_summary}"
        )

    logging.info("Endpoint check complete.")

# Schedule Checks
# ===========================================================================

def schedule_checks():
    next_run_time = datetime.now() + timedelta(seconds=CHECK_INTERVAL)
    logging.info(f"Scheduled next check at {next_run_time}.")
    asyncio.run(check_all_endpoints())

# Main application
# ===========================================================================
def main():
    logging.info("Starting endpoint checker script.")
    schedule.every(CHECK_INTERVAL).seconds.do(schedule_checks)

    while True:
        schedule.run_pending()
        time.sleep(1)

# Flask application
# ===========================================================================
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Welcome to the Endpoint Checker API. Access logs at /logs."
    })

@app.route('/logs', methods=['GET'])
def get_logs():
    return send_file('endpoint_checker.log', mimetype='text/plain')

if __name__ == "__main__":
    import threading
    threading.Thread(target=main, daemon=True).start()

    app.run(host='0.0.0.0', port=8080)

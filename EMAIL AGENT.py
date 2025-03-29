# supabase_email_agent.py
import os
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from supabase import create_client
import schedule
import time

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_ONE = os.getenv("TABLE_ONE")  # bitcoin_prices
TABLE_TWO = os.getenv("TABLE_TWO")  # econews

# Email configuration
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_data_from_bitcoin_prices():
    """Fetch data from the bitcoin_prices table"""
    try:
        # Without created_at, we'll just fetch the most recent records
        # You may want to use another column for ordering if available
        response = supabase.table(TABLE_ONE).select("*").limit(100).execute()
        if hasattr(response, 'error') and response.error is not None:
            raise Exception(f"Error in Supabase query: {response.error}")
        return response.data
    except Exception as e:
        print(f"Error fetching data from {TABLE_ONE}: {str(e)}")
        return None


def fetch_data_from_econews():
    """Fetch data from the econews table"""
    try:
        # Without created_at, we'll just fetch the most recent records
        # You may want to use another column for ordering if available
        response = supabase.table(TABLE_TWO).select("*").limit(100).execute()
        if hasattr(response, 'error') and response.error is not None:
            raise Exception(f"Error in Supabase query: {response.error}")
        return response.data
    except Exception as e:
        print(f"Error fetching data from {TABLE_TWO}: {str(e)}")
        return None


def format_table_data(data, table_name):
    """Format the data from a table into an HTML table"""
    if not data or len(data) == 0:
        return f"<p>No data available for {table_name}.</p>"

    html_content = f"<h3>Data from {table_name}</h3>"
    html_content += '<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">'

    # Add table headers
    html_content += '<tr style="background-color: #f2f2f2;">'
    for key in data[0].keys():
        html_content += f'<th style="text-align: left;">{key}</th>'
    html_content += '</tr>'

    # Add table rows
    for idx, row in enumerate(data):
        bg_color = '#ffffff' if idx % 2 == 0 else '#f9f9f9'
        html_content += f'<tr style="background-color: {bg_color};">'
        for value in row.values():
            # Format the value based on its type
            if value is None:
                formatted_value = ''
            elif isinstance(value, (dict, list)):
                # Handle JSON objects or arrays
                formatted_value = json.dumps(value)
            else:
                formatted_value = str(value)
            html_content += f'<td style="text-align: left;">{formatted_value}</td>'
        html_content += '</tr>'

    html_content += '</table>'
    html_content += f"<p>Total records: {len(data)}</p>"

    return html_content


def compile_email_content(bitcoin_data, econews_data):
    """Compile all data into a single HTML email"""
    html_content = '<h2>Supabase Database Report</h2>'
    html_content += f'<p>Report generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>'

    # Add Bitcoin price data
    html_content += format_table_data(bitcoin_data, TABLE_ONE)

    # Add some spacing
    html_content += '<br><hr><br>'

    # Add economic news data
    html_content += format_table_data(econews_data, TABLE_TWO)

    return html_content


def send_email(html_content):
    """Send an email with the compiled HTML content"""
    try:
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Supabase Database Report - Bitcoin Prices and Economic News'
        msg['From'] = f'Database Reporter <{EMAIL_USER}>'
        msg['To'] = RECIPIENT_EMAIL

        # Attach HTML content
        part = MIMEText(html_content, 'html')
        msg.attach(part)

        # Connect to server and send
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, RECIPIENT_EMAIL, msg.as_string())

        print('Email sent successfully!')
        return True
    except Exception as e:
        print(f'Error sending email: {str(e)}')
        return False


def run_agent():
    """Main function to run the agent"""
    print('Running Supabase Email Agent...')

    # Fetch data from both tables
    bitcoin_data = fetch_data_from_bitcoin_prices()
    econews_data = fetch_data_from_econews()

    if bitcoin_data is None and econews_data is None:
        print('Failed to fetch data from both tables. Aborting email send.')
        return

    # Compile the data for email
    html_content = compile_email_content(bitcoin_data, econews_data)

    # Send the email
    email_sent = send_email(html_content)

    if email_sent:
        print('Agent completed successfully!')
    else:
        print('Agent failed to send email.')


if __name__ == "__main__":
    # Run once immediately
    run_agent()

    # Uncomment the following lines to schedule the agent to run daily at 8 AM
    # schedule.every().day.at("08:00").do(run_agent)
    #
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)
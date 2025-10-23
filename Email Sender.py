import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime
import pandas as pd
import os
import json

# Load lookback_days from config
with open("Data/config.json", "r") as f:
    config = json.load(f)
lookback_days = config.get("lookback_days", None)

# Email details
sender_email = "goldencrossemailsender@gmail.com"
password = "grsb oohc kiru ayyi"  # Use App Password

# Read email addresses from CSV
email_csv_path = "Data/email_list.csv"  # CSV must contain a column named 'email'
emails_df = pd.read_csv(email_csv_path)
receiver_emails = emails_df['email'].dropna().astype(str).tolist()

# Subject
subject = "Stock data of NIFTY500 Companies: Golden Cross Dates, Drop Cross Dates"

# Dated result file
date_string = datetime.now().strftime("%Y_%m_%d")
result_csv_path = f"Data/Results/MA Cross results on {date_string}.csv"

# Determine if we have results to attach
has_rows = False
attachment_error = None
if os.path.exists(result_csv_path):
    try:
        df = pd.read_csv(result_csv_path)
        # We consider "has_rows" if there is at least one data row (headers alone don't count)
        has_rows = (df is not None) and (not df.empty)
    except pd.errors.EmptyDataError:
        has_rows = False
    except Exception as e:
        # If there's some other error reading, treat as no data and keep the error for logging
        has_rows = False
        attachment_error = f"Error reading results CSV: {e}"
else:
    has_rows = False

# Compose email body depending on data availability
if has_rows:
    lookback_phrase = f"the last {lookback_days} days" if lookback_days is not None else "the recent lookback window"
    body_text = (
        "Hello,\n\n"
        "Please find attached the daily stock data for NIFTY500 companies that formed a Golden Cross or Drop Cross within {lookback_phrase}.\n"
        f"Attachment: {os.path.basename(result_csv_path)}\n\n"
        "Regards,\nStockFinder"
    )
else:
    # Fall back to a generic message if lookback_days is missing
    lookback_phrase = f"the last {lookback_days} days" if lookback_days is not None else "the recent lookback window"
    body_text = (
        "Hello,\n\n"
        f"There are no NIFTY500 companies that formed a Golden Cross or Drop Cross within {lookback_phrase}.\n"
        "No attachment is included.\n\n"
        "Regards,\nStockFinder"
    )

if attachment_error:
    print(attachment_error)

# Send email to each recipient
for receiver_email in receiver_emails:
    try:
        # Build message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject

        # Add text body
        message.attach(MIMEText(body_text, 'plain'))

        # Attach CSV only if we have data
        if has_rows:
            try:
                with open(result_csv_path, 'rb') as file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={os.path.basename(result_csv_path)}'
                    )
                    message.attach(part)
            except Exception as e:
                print(f"Error attaching {result_csv_path}: {e}")

        # Send
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Email sent successfully to {receiver_email}!")

    except Exception as e:
        print(f"Error sending to {receiver_email}: {e}")

    finally:
        try:
            server.quit()
        except Exception:
            pass

print("All emails processed.")
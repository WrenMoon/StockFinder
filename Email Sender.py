import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import pandas as pd

# Email details
sender_email = "goldencrossemailsender@gmail.com"
password = "grsb oohc kiru ayyi"  # Use App Password if needed

# Read email addresses from CSV
# Assumes CSV has a column named 'email' - adjust column name as needed
email_csv_path = "Data/email_list.csv"  # Change this to your CSV file path
emails_df = pd.read_csv(email_csv_path)
receiver_emails = emails_df['email'].tolist()  # Change 'email' to your column name

# Email subject
subject = "Stock data of NIFTY500 Companies: Golden Cross Dates, Drop Cross Dates, Mutual Fund Holding Monthly Change %"

# List of file paths to attach
date = datetime.now().date()
date_string = date.strftime("%Y_%m_%d")

file_paths = [
    'Data/MA Cross results on '+date_string+'.csv'
]

# Send email to each recipient
for receiver_email in receiver_emails:
    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Iterate through each file in the list and attach them
    for file_path in file_paths:
        try:
            with open(file_path, 'rb') as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={file_path.split("/")[-1]}')  
                message.attach(part)
        except Exception as e:
            print(f"Error attaching {file_path}: {e}")

    # Set up the SMTP server and send
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        
        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Email sent successfully to {receiver_email}!")
        
    except Exception as e:
        print(f"Error sending to {receiver_email}: {e}")

    finally:
        server.quit()

print("All emails sent!")
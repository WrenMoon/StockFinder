import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta

# Email details
sender_email = "goldencrossemailsender@gmail.com"
receiver_email = "aparnasgnio@gmail.com"
password = "grsb oohc kiru ayyi"  # Use App Password if needed

# Email subject
subject = "Golden cross data of NIFTY500 companies in the last 5 days"

# File to attach
date = datetime.now().date()
date_string = date.strftime("%Y_%m_%d")
file_path = 'golden_cross_results_on_'+date_string+'.csv' 

# Set up the MIME
message = MIMEMultipart()
message['From'] = sender_email
message['To'] = receiver_email
message['Subject'] = subject

# Open the file to send as an attachment
with open(file_path, 'rb') as file:
    part = MIMEBase('application', 'octet-stream')  # MIME type for binary files
    part.set_payload(file.read())  # Attach file content
    encoders.encode_base64(part)  # Encode the attachment
    part.add_header('Content-Disposition', f'attachment; filename={file_path.split("/")[-1]}')  
    message.attach(part)

# Set up the SMTP server
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  # Secure connection
    server.login(sender_email, password)  # Log in to the Gmail account
    
    # Send the email
    server.sendmail(sender_email, receiver_email, message.as_string())
    print("Email sent successfully!")
    
except Exception as e:
    print(f"Error: {e}")

finally:
    server.quit()  # Close the connection to the server

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Email details
sender_email = "goldencrossemailsender@gmail.com"
receiver_email = "aparnasgnio@gmail.com"
password = "grsb oohc kiru ayyi"  # Use App Password if needed

# Email subject
subject = "Stock data of NIFTY500 Companies: Golden Cross Dates, Drop Cross Dates, Mutual Fund Holding Monthly Change %"

# List of file paths to attach
date = datetime.now().date()
date_string = date.strftime("%Y_%m_%d")

file_paths = [
    'Data/MA Cross results on '+date_string+'.csv'
]

# Set up the MIME
message = MIMEMultipart()
message['From'] = sender_email
message['To'] = receiver_email
message['Subject'] = subject

# Iterate through each file in the list and attach them
for file_path in file_paths:
    try:
        with open(file_path, 'rb') as file:
            part = MIMEBase('application', 'octet-stream')  # MIME type for binary files
            part.set_payload(file.read())  # Attach file content
            encoders.encode_base64(part)  # Encode the attachment
            part.add_header('Content-Disposition', f'attachment; filename={file_path.split("/")[-1]}')  
            message.attach(part)
            print(f"Attached {file_path}")
    except Exception as e:
        print(f"Error attaching {file_path}: {e}")

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

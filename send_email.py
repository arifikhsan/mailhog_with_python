import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP Configuration
SMTP_HOST = "localhost"
SMTP_PORT = 1025

# Email details
sender_email = "sender@example.com"
receiver_email = "receiver@example.com"
subject = "Test Email from MailHog"

# Create message
message = MIMEMultipart("alternative")
message["Subject"] = subject
message["From"] = sender_email
message["To"] = receiver_email

# Email body
text = "This is a plain text email sent to MailHog."
html = """\
<html>
  <body>
    <h1>Test Email</h1>
    <p>This is an <strong>HTML email</strong> sent to MailHog.</p>
    <p>Check the web UI at <a href="http://localhost:8025">http://localhost:8025</a></p>
  </body>
</html>
"""

# Attach parts
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")
message.attach(part1)
message.attach(part2)

# Send email
try:
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.sendmail(sender_email, receiver_email, message.as_string())
    print(f"✓ Email sent successfully!")
    print(f"✓ View it at: http://localhost:8025")
except Exception as e:
    print(f"✗ Failed to send email: {e}")

import os
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# Load ENV variables
load_dotenv()


# --------------------------------------------
# PDF Generator (your function)
# --------------------------------------------
def generate_pdf_from_text(text):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter
    x = 40
    y = height - 40

    p.setFont("Helvetica", 11)

    for line in text.split("\n"):
        p.drawString(x, y, line)
        y -= 14
        if y < 40:
            p.showPage()
            p.setFont("Helvetica", 11)
            y = height - 40

    p.save()
    buffer.seek(0)
    return buffer.read()


# --------------------------------------------
# Email Sender (your function)
# --------------------------------------------
def send_email_report(to_email, subject, body, attachment_content=None, attachment_name=None):
    try:
        sender_email = "vijayasatya369@gmail.com"
        sender_password = os.getenv("EMAIL_APP_PASSWORD")

        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        if attachment_content and attachment_name:
            # PDF attachment
            pdf_bytes = generate_pdf_from_text(attachment_content)
            msg.add_attachment(
                pdf_bytes,
                maintype="application",
                subtype="pdf",
                filename=attachment_name + ".pdf"
            )

            # Markdown attachment
            msg.add_attachment(
                attachment_content.encode("utf-8"),
                maintype="text",
                subtype="markdown",
                filename=attachment_name + ".md"
            )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        return True, "✅ Email sent successfully!"

    except Exception as e:
        return False, f"❌ Failed to send email: {e}"


# --------------------------------------------
# TEST THE FUNCTION
# --------------------------------------------
if __name__ == "__main__":
    print("\n=== Email Sending Test Started ===\n")

    to_email = "vijayasatyad@gmail.com"
    subject = "Test Email with PDF + Markdown Attachments"

    body = "Hello! This is a test email sent using your send_email_report() function."

    # This is the content to convert to PDF and MD
    test_report_text = """
    # Test Blog Report

    This is a dummy blog report used to test PDF and Markdown email attachments.

    - Item 1
    - Item 2
    - Item 3

    End of test.
    """

    attachment_name = "test_blog_report"

    print("➡ Sending email...")

    success, message = send_email_report(
        to_email,
        subject,
        body,
        attachment_content=test_report_text,
        attachment_name=attachment_name
    )

    print("\n=== RESULT ===")
    print("Success:", success)
    print("Message:", message)
    print("\n=== Test Completed ===\n")

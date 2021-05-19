import email, smtplib, ssl

from tabulate import tabulate

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(angels):
    subject = "Today's Fallen Angels Report"
    sender_email = "sp500.fallenangels@gmail.com"
    receiver_email = "danielbacubs@yahoo.com"
    password = "smartman1!"
    # Create a multipart message and set headers
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    html_list = tabulate(angels, headers=["The Angels:"], tablefmt="html")
    # print(html_list)
    # message["Bcc"] = receiver_email  # Recommended for mass emails

    # Create the plain-text and HTML version of your message
    text = """\
    Hi there,

    This is your daily report of all stocks indentified as Fallen Angels. In the attatched csv file you will find price information about each stock in the S&P 500, with additional information about all stocks that meet the Fallen Angel criteria.

    Here are the Angels:
    under construction

    Invest in value, and have a nice day!


    Sincerely,
    Benjamin Graham"""
    html = (
        """\
    <html>
    <body>
    <p style="color: #2e6c80;"><span style="color: #000000;">Hi there,</span></p>
    <p>This is your daily report of all stocks indentified as <span style="text-decoration: underline;">Fallen Angels</span>. In the attatched csv file you will find price information&nbsp; about each stock in the S&amp;P 500, with additional information about all stocks that meet the&nbsp;<span style="text-decoration: underline;">Fallen Angel</span> criteria.</p>
    <p>Here are the Angels:&nbsp;</p>
    <p>"""
        + html_list
        + """</p>
    <p>&nbsp;</p>
    <p>Invest in value, and have a nice day!</p>
    <p>&nbsp;</p>
    <p>Sincerely,</p>
    <p>Benjamin Graham</p>
    <p style="color: #2e6c80;">&nbsp;</p>
    <p>&nbsp;</p>
    <p>&nbsp;</p>
    <p><strong>&nbsp;</strong></p>
    </body>
    </html>
    """
    )

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    filename = "stock-stats.csv"  # In same directory as script

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        file_part = MIMEBase("application", "octet-stream")
        file_part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(file_part)

    # Add header as key/value pair to attachment part
    file_part.add_header(
        "Content-Disposition", f"attachment; filename= {filename}",
    )

    message.attach(part1)
    message.attach(part2)
    # Add attachment to message and convert message to string
    message.attach(file_part)

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

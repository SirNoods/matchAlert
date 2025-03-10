import argparse
import smtplib
import requests
from email.mime.text import MIMEText
from datetime import datetime

def get_football_matches(api_key, date):
    """
    Fetch football matches for a given date using football-data.org

    Args:
        api_key (str): API key for the football match service.
        date (str): Date in YYYY-MM-DD format.

    Returns:
        list: A list of football matches happening on the given date.
    """
    url = f"https://api.football-data.org/v4/matches?dateFrom={date}&dateTo={date}"
    headers = {"X-Auth-Token": api_key}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("matches", [])
    else:
        print(f"Error fetching matches: {response.status_code} - {response.text}")
        return []


def send_email_smtp(smtp_username, smtp_password, sender_email, recipient_email, message):
    """
    Sends the email out

    Args:
        smtp_username (str): SendGrid SMTP username (usually "apikey").
        smtp_password (str): SendGrid SMTP API key.
        sender_email (str): Verified sender email address.
        recipient_email (str): Recipient email address.
        message (str): Email message body.
    """
    msg = MIMEText(message)
    msg["Subject"] = "Football Match Alert"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP("smtp.sendgrid.net", 587) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")


def main():
    """
    Parses command-line arguments and runs the script.
    """
    parser = argparse.ArgumentParser(description="Football match alert script.")
    parser.add_argument("--api-key", required=True, help="API key for the football match service")
    parser.add_argument("--smtp-user", default="apikey", help="SendGrid SMTP username (always 'apikey')")
    parser.add_argument("--smtp-pass", required=True, help="SendGrid SMTP password (your API key)")
    parser.add_argument("--sender-email", required=True, help="Verified SendGrid sender email")
    parser.add_argument("--recipient-email", required=True, help="Recipient email address")
    parser.add_argument("--date", default=datetime.today().strftime('%Y-%m-%d'), help="Date for football matches (YYYY-MM-DD)")

    args = parser.parse_args()

    matches = get_football_matches(args.api_key, args.date)

    if matches:
        match_times = [f"{match['utcDate']} - {match['homeTeam']['name']} vs {match['awayTeam']['name']}" for match in matches]
        message = "Avoid public transport during these match times:\n\n" + "\n".join(match_times)
        send_email_smtp(args.smtp_user, args.smtp_pass, args.sender_email, args.recipient_email, message)
    else:
        print("No matches found for today.")

if __name__ == "__main__":
    main()


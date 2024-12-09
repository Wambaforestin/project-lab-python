import content
import datetime
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv # Import the load_dotenv function from the python-dotenv module
import os   


load_dotenv() # Load environment variables from the .env file


class DailyEmail:
    def __init__(self):
        self.content = {
            "quote": {"include": True, "content": content.get_random_quote()},
            "weather": {"include": True, "content": content.get_weather_forecast()},
            "wikipedia": {"include": True, "content": content.get_wikipedia_article()}
        }
        
        self.recipient_list = {
            "email1": os.getenv('RECIPIENT_EMAIL1'),   # Get the recipient email address from environment variables
            "email2": os.getenv('RECIPIENT_EMAIL2')  # Get the recipient email address from environment variables
        } 
        
        self.sender_credentials = {
            "email": os.getenv('SENDER_EMAIL'),  # Get the sender email address from environment variables
            "password": os.getenv('SENDER_PASSWORD')  # Get the sender email password from environment variables
        }
        
    
    """
        Generate email message body as plain text and HTML content.
     """

    def format_email(self):
        # Enhanced text formatting with more visual separation and emphasis
        message = f"🌞 Daily Digest - {datetime.datetime.now().strftime('%d %B %Y')} 🌞\n"
        message += "=" * 50 + "\n\n"

        # Quote section with decorative borders
        if self.content['quote']['include']:
            quote = self.content['quote']['content']
            message += "📜 Quote of the Day 📜\n"
            message += "-" * 25 + "\n"
            message += f"❝{quote['quote']}❞\n"
            message += f"    - {quote['author']}\n\n"

        # Weather section with emoji and detailed formatting
        if self.content['weather']['include']:
            weather = self.content['weather']['content']
            message += f"🌦️ Weather Forecast: {weather['city']}, {weather['country']} 🌦️\n"
            message += "-" * 50 + "\n"
            for period in weather['forecast']:
                message += f"• {period['timestamp']}: {period['description']} | {period['temperature']}°C\n"
            message += "\n"

        # Wikipedia section with engaging header
        if self.content['wikipedia']['include']:
            article = self.content['wikipedia']['content']
            message += "🧠 Did You Know? 🧠\n"
            message += "-" * 25 + "\n"
            message += f"{article['extract']}\n"
            message += f"(Source: {article['url']})\n\n"

        message += "✨ Have a Fantastic Day! ✨"

        # Enhanced HTML with more sophisticated styling and responsive design
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Daily Digest - {datetime.datetime.now().strftime('%d %B %Y')}</title>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Roboto', Arial, sans-serif;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    padding: 30px;
                }}
                h1 {{
                    color: #2c3e50;
                    text-align: center;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }}
                .section {{
                    margin-bottom: 20px;
                    padding: 15px;
                    border-radius: 5px;
                }}
                .quote {{
                    background-color: #f9e79f;
                    font-style: italic;
                }}
                .weather {{
                    background-color: #e6f2ff;
                }}
                .wikipedia {{
                    background-color: #e8f6f3;
                }}
                .footer {{
                    text-align: center;
                    color: #7f8c8d;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌞 Daily Digest</h1>
                <p style="text-align: center; color: #7f8c8d;">
                    {datetime.datetime.now().strftime('%d %B %Y')}
                </p>

                {f'''
                <div class="section quote">
                    <h2>📜 Quote of the Day</h2>
                    <blockquote>
                        <i>{quote['quote']}</i>
                        <footer>— {quote['author']}</footer>
                    </blockquote>
                </div>''' if self.content['quote']['include'] else ''}

                {f'''
                <div class="section weather">
                    <h2>🌦️ Weather Forecast</h2>
                    <p><strong>Location:</strong> {weather['city']}, {weather['country']}</p>
                    <ul>
                        {''.join([f"<li>{period['timestamp']}: {period['description']}, {period['temperature']}°C</li>" for period in weather['forecast']])}
                    </ul>
                </div>''' if self.content['weather']['include'] else ''}

                {f'''
                <div class="section wikipedia">
                    <h2>🧠 Did You Know?</h2>
                    <p>{article['extract']}</p>
                    <p><em>Source: <a href="{article['url']}">{article['url']}</a></em></p>
                </div>''' if self.content['wikipedia']['include'] else ''}

                <div class="footer">
                    <p>✨ Have a Fantastic Day! ✨</p>
                </div>
            </div>
        </body>
        </html>
        """

        return message, html

    """
    Send the formatted email to the recipient.
    """
    def send_email(self):
        # Build the email message
        message = EmailMessage()
        message['Subject'] = f"🌞 Daily Digest - {datetime.datetime.now().strftime('%d %B %Y')} 🌞"
        message['From'] = self.sender_credentials['email']
        message['To'] = ', '.join(self.recipient_list.values()) # since we have multiple recipients, we join them with a comma
        
        # Add plain text and HTML content
        message_body_text, message_body_html = self.format_email()
        message.set_content(message_body_text)
        message.add_alternative(message_body_html, subtype='html')
        
        # Send the email with the SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(self.sender_credentials['email'], self.sender_credentials['password'])
            server.send_message(message)
            server.quit()
        print("Email sent successfully!")

if __name__ == '__main__':
    # Create a DailyEmail instance
    email = DailyEmail()

    # Format the email content
    message, html = email.format_email()

    # Print the email content
    print(message)
    print("\n--- HTML Content ---")
    print(html)
    
    # Save the email content to files
    with open('email.html', 'w', encoding='utf-8') as file:
        file.write(html)
    with open('email.txt', 'w', encoding='utf-8') as file:
        file.write(message)
        
    # Send the email
    print("\n--- Sending Email ---")
    email.send_email()
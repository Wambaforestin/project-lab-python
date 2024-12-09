import content
import datetime

class DailyEmail:
    # Define the structure of the daily email content
    def __init__(self):
        self.content = {
            "quote": {"include": True, "content": content.get_random_quote()},
            "weather": {"include": True, "content": content.get_weather_forecast()},
            "wikipedia": {"include": True, "content": content.get_wikipedia_article()}
        }

    # Format the general message of the email
    def format_email(self):
        # Define the plain text email message structure
        message = f"Good morning!\n\nHere's your daily email for {datetime.datetime.now().strftime('%d-%m-%Y')}:\n\n"

        # Add the quote to the message
        if self.content['quote']['include']:
            quote = self.content['quote']['content']
            message += f"Quote of the day: '{quote['quote']}' - {quote['author']}\n\n"

        # Add the weather forecast to the message
        if self.content['weather']['include']:
            weather = self.content['weather']['content']
            message += f"Today's weather forecast for {weather['city']}, {weather['country']}:\n"
            for period in weather['forecast']:
                message += f" - {period['timestamp']}: {period['description']}, {period['temperature']}°C\n"
            message += "\n"

        # Add the Wikipedia article to the message
        if self.content['wikipedia']['include']:
            article = self.content['wikipedia']['content']
            message += f"Did you know? {article['extract']} (source: {article['url']})\n\n"

        # Add a closing message
        message += "Have a great day!"

        # Generate HTML content for the email
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                h1 {{
                    color: #2c3e50;
                }}
                p {{
                    margin: 10px 0;
                }}
                .quote {{
                    font-style: italic;
                    color: #e74c3c;
                }}
                .weather {{
                    background-color: #ecf0f1;
                    padding: 10px;
                    border-radius: 5px;
                }}
                .wikipedia {{
                    background-color: #f9e79f;
                    padding: 10px;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <h1>Good Morning!</h1>
            <p>Here's your daily email for {datetime.datetime.now().strftime('%d-%m-%Y')}:</p>

            {f"<p class='quote'><b>Quote of the day:</b> '{quote['quote']}' - {quote['author']}</p>" if self.content['quote']['include'] else ""}

            {f"<div class='weather'><b>Today's weather forecast for {weather['city']}, {weather['country']}:</b><ul>" + 
            "".join([f"<li>{period['timestamp']}: {period['description']}, {period['temperature']}°C</li>" for period in weather['forecast']]) + 
            "</ul></div>" if self.content['weather']['include'] else ""}

            {f"<div class='wikipedia'><b>Did you know?</b> {article['extract']}<br>Source: <a href='{article['url']}'>{article['url']}</a></div>" if self.content['wikipedia']['include'] else ""}

            <p>Have a great day!</p>
        </body>
        </html>
        """

        return message, html

    def send_email(self):
        pass
    
    
    
    
    

if __name__ == '__main__':
    # Create a DailyEmail instance
    email = DailyEmail()

    # Format the email content
    message, html = email.format_email()

    # Print the email content
    print(message)
    print(html)
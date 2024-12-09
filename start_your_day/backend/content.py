import csv
import random
import os
from dotenv import load_dotenv 
from urllib import request
import json
import datetime

load_dotenv()

"""
Load a random quote from a CSV file and return it as a dictionary.
"""
def get_random_quote(quotes_file='quotes.csv'):
    try: #load the quotes from the csv file
        with open(quotes_file, 'r') as file:
            quotes = [{'author': line[0], 'quote': line[1]} for line in csv.reader(file, delimiter='|')]
    except Exception as e: # if there is an exception, return a default quote
        print(f'Error loading quotes: {e}')
        quotes = [{'author': 'Unknown', 'quote': 'An error occurred while loading the quotes. Please try again later.'}]
    
    return random.choice(quotes) # return a random quote

"""
Get the weather forecast for a specific location using the OpenWeatherMap API.
"""
def get_weather_forecast(my_coords={'lat': 48.9881, 'lon': 2.2339}):
    try:
        # Retrieve the weather forecast from the OpenWeatherMap API
        api_key = os.getenv('WEATHER_API_KEY')  # Get the API key from environment variables
        url = f'https://api.openweathermap.org/data/2.5/forecast?lat={my_coords["lat"]}&lon={my_coords["lon"]}&exclude=minutely,hourly&appid={api_key}&units=metric'
        response = json.load(request.urlopen(url))
        
        # Process the API response into a clean structure
        forecast = {
            "city": response['city']['name'],
            "country": response['city']['country'],
            "forecast": []  # List to store the forecast for the next periods
        }

        for period in response['list'][:9]:  # Get the first 9 forecast periods
            forecast['forecast'].append({
                'timestamp': datetime.datetime.fromtimestamp(period['dt']).strftime('%Y-%m-%d %H:%M:%S'),
                'temperature': period['main']['temp'],
                'description': period['weather'][0]['description'].title(),
                'icon': f"https://openweathermap.org/img/wn/{period['weather'][0]['icon']}@2x.png"
            })

        return forecast

    except Exception as e:
        # Handle errors and return a default structure
        print(f'Error loading weather forecast: {e}')
        return {
            "city": "Unknown",
            "country": "Unknown",
            "forecast": []
        }
        
"""
Get a random summary of  Wikipedia articles.
"""
def get_wikipedia_article():
    try:
        # Retrieve a random Wikipedia article summary using the Wikipedia API
        url = 'https://en.wikipedia.org/api/rest_v1/page/random/summary'
        response = json.load(request.urlopen(url))
        
        # Process the API response into a clean structure
        article = {
            "title": response['title'],
            "extract": response['extract'],
            "url": response['content_urls']['desktop']['page']
        }

        return article

    except Exception as e:
        # Handle errors and return a default structure
        print(f'Error loading Wikipedia article: {e}')
        return {
            "title": "Unknown",
            "extract": "An error occurred while loading the Wikipedia article. Please try again later.",
            "url": "#"
        }


if __name__ == '__main__':
    # Test the get_random_quote function
    print("Testing the get_random_quote function")
    quote = get_random_quote()
    print(f"Quote: {quote['quote']}, Author: {quote['author']}")
    
    quote = get_random_quote('quotes2.csv')
    print(f"Quote: {quote['quote']} Author: {quote['author']}")

    # Test the get_weather_forecast function
    print("\nTesting the get_weather_forecast function")

    # Test the default location
    forecast = get_weather_forecast()  # Default location
    print(f"City: {forecast['city']}, Country: {forecast['country']}")
    for period in forecast['forecast']:
        print(f"Timestamp: {period['timestamp']}, Temperature: {period['temperature']}, "
              f"Description: {period['description']}, Icon: {period['icon']}")

    # Test the get_weather_forecast function with a custom location in Paris
    print("\nTesting with a custom location: Paris, France")
    forecast = get_weather_forecast({'lat': 48.8566, 'lon': 2.3522})  # Paris, France
    print(f"City: {forecast['city']}, Country: {forecast['country']}")
    for period in forecast['forecast']:
        print(f"Timestamp: {period['timestamp']}, Temperature: {period['temperature']}, "
              f"Description: {period['description']}, Icon: {period['icon']}")

    # Test the error handling with an invalid location
    print("\nTesting with an invalid location: (0, 0)")
    forecast = get_weather_forecast({'lat': 0, 'lon': 0})  # Invalid location
    print(f"City: {forecast['city']}, Country: {forecast['country']}")
    for period in forecast['forecast']:
        print(f"Timestamp: {period['timestamp']}, Temperature: {period['temperature']}, "
              f"Description: {period['description']}, Icon: {period['icon']}")

    # Test the get_wikipedia_article function
    print("\nTesting the get_wikipedia_article function")
    article = get_wikipedia_article()
    print(f"Title: {article['title']}")
    print(f"Extract: {article['extract']}")
    print(f"URL: {article['url']}")


    
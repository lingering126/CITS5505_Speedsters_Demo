import requests

def fetch_car_news(api_key):
    url = f'https://newsapi.org/v2/everything?q=car&apiKey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        return []

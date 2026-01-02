import requests

class RestWrapper:
    def __init__(self, url):
        self.url = url
        self.last_data = None

    def fetch_data(self):
        """
        Fetches data from the REST API.
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            data = response.json()
            self.last_data = data
            return data
        except Exception as e:
            print(f"Error fetching from API {self.url}: {e}")
            return {"error": str(e)}

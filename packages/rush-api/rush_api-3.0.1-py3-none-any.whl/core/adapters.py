import requests
from bs4 import BeautifulSoup

class WebAdapter:
    def fetch_data(self, url):
        """
        Fetches data from a URL.
        Returns a dictionary with title and header/table info.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.title.string if soup.title else "No Title"
            
            # Find first h1 or first table
            header = "No Header Found"
            h1 = soup.find('h1')
            if h1:
                header = h1.get_text(strip=True)
            else:
                table = soup.find('table')
                if table:
                    header = "Table Found"
            
            return {
                "title": title,
                "header": header,
                "status": response.status_code,
                "raw_content": response.text[:500] # Return first 500 chars for inspection
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": 500
            }

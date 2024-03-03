import requests
import redis
import json
import matplotlib.pyplot as plt

class DataProcessor:
    """Class for processing JSON data"""

    def __init__(self, api_url, redis_host, redis_port, redis_password=None):
        """ Initialize the DataProcessor"""
        self.api_url = "https://api.coincap.io/v2/assets"
        self.redis_client = redis.StrictRedis(
            host="redis-12090.c267.us-east-1-4.ec2.cloud.redislabs.com", port=12090, password= "Q6pujlP1Z7ROW9gazwTHaDbWmhvRcCYG"
        )

    def fetch_data_from_api(self):
        """Fetch JSON data from the API"""
        response = requests.get(self.api_url)
        return response.json()

    def insert_into_redis(self, data):
        """Insert JSON data into RedisJSON"""
        json_data = json.dumps(data)  # Serialize the dictionary to JSON string
        self.redis_client.set("data", json_data)

    def get_price(self, coin_id):
        """Get the price of a specific cryptocurrency"""
        data = self.fetch_data_from_api()
        if 'data' in data:
            for entry in data['data']:
                if entry['id'] == coin_id:
                    return float(entry['priceUsd'])
        return None

    def calculate_price_difference(self, coin1_id, coin2_id):
        """Calculate the difference between the prices of two cryptocurrencies"""
        coin1_price = self.get_price(coin1_id)
        coin2_price = self.get_price(coin2_id)
        if coin1_price is not None and coin2_price is not None:
            return coin1_price - coin2_price
        return None
        
    def search_data(self, key):
        """Search data stored in Redis"""
        json_data = self.redis_client.get("data")
        if json_data:
            data = json.loads(json_data)
            for entry in data['data']:
                if entry.get('name') == key:
                    return entry
        return None
    def process_data(self, data):
        """Process JSON data"""
        # Extracting relevant information
        names = [entry['name'] for entry in data['data'][:10]]
        market_caps = [float(entry['marketCapUsd']) for entry in data['data'][:10]]
        
        # Generating a matplotlib chart
        plt.bar(names, market_caps)
        plt.xlabel('Cryptocurrency')
        plt.ylabel('Market Cap (USD)')
        plt.title('Market Cap of Top 10 Cryptocurrencies')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
        plt.show()

def main():
    """Main function"""
    # Define constants
    API_URL = "https://api.coincap.io/v2/assets"
    REDIS_HOST = " redis-12090.c267.us-east-1-4.ec2.cloud.redislabs.com"
    REDIS_PORT = 12090
    REDIS_PASSWORD ="Q6pujlP1Z7ROW9gazwTHaDbWmhvRcCYG"

    # Initialize DataProcessor
    processor = DataProcessor(API_URL, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)

    # Fetch data from API
    data = processor.fetch_data_from_api()

    # Insert data into RedisJSON
    processor.insert_into_redis(data)

    # Process data
    processor.process_data(data)
    search_key = "Bitcoin"
    result = processor.search_data(search_key)
    if result:
        print(f"Found data for {search_key}: {result}")
    else:
        print(f"No data found for {search_key}")
    bitcoin_id = "bitcoin"
    ethereum_id = "ethereum" 
    price_difference = processor.calculate_price_difference(bitcoin_id, ethereum_id)
    if price_difference is not None:
        print(f"Difference between Bitcoin and Ethereum prices: {price_difference} USD")
    else:
        print("Failed to calculate the price difference")    

if __name__ == "__main__":
    main()

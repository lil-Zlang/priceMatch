from bs4 import BeautifulSoup
from googlesearch import search
import requests

# Function to search for product online using Google
def search_product_online(product_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    search_results = []
    
    # Perform Google search and get URLs
    for url in search(f"{product_name} site:amazon.com OR site:bestbuy.com", num_results=3):
        search_results.append(url)
    
    return search_results

# Function to scrape the price from a given product URL
def check_price(product_name, product_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find price element (this depends on the website structure)
    price = None
    if "amazon" in product_url:
        price_tag = soup.find('span', {'id': 'priceblock_ourprice'}) or soup.find('span', {'id': 'priceblock_dealprice'})
        if price_tag:
            price = price_tag.get_text().strip()
    elif "bestbuy" in product_url:
        price_tag = soup.find('div', {'class': 'priceView-hero-price priceView-customer-price'})
        if price_tag:
            price = price_tag.find('span').get_text().strip()
    
    # Clean up price and convert to float
    if price:
        price = price.replace('$', '').replace(',', '').strip()
        price = float(price)
        print(f"Product: {product_name}, Price: ${price}")
        return price
    else:
        print(f"Unable to find price for {product_name} at {product_url}")
        return None

# Mock data for testing
products = [
    {
        'product_name': 'Apple - 11-inch iPad Pro M4 chip Built for Apple Intelligence Wi-Fi 256GB with OLED - Space Black',
        'purchased_price': 1000
    },
    {
        'product_name': 'Triple Strength Omega 3 Fish Oil Supplement',
        'purchased_price': 50
    }
]

# Function to compare current price with the purchased price
def compare_prices():
    for product in products:
        product_name = product['product_name']
        purchased_price = product['purchased_price']
        
        # Search for product online to get URLs
        urls = search_product_online(product_name)
        
        # Check price for each URL until a valid price is found
        for url in urls:
            current_price = check_price(product_name, url)
            if current_price is not None:
                if current_price > purchased_price:
                    print(f"Higher Price: The current price for '{product_name}' is ${current_price}, which is higher than the purchased price of ${purchased_price}.")
                elif current_price < purchased_price:
                    print(f"Cheaper Price: The current price for '{product_name}' is ${current_price}, which is cheaper than the purchased price of ${purchased_price}.")
                else:
                    print(f"Same Price: The current price for '{product_name}' is the same as the purchased price of ${purchased_price}.")
                break  # Stop searching once we get a valid price

# Run the price comparison
if __name__ == '__main__':
    compare_prices()

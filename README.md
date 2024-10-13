# Price Match Automation Tool with Email Integration

## Overview

This repository provides a comprehensive tool that combines price matching automation with email purchase information extraction. It allows users to automatically track and compare current prices of purchased products, determining price match opportunities, while also extracting purchase details from email confirmations.

## Features

- Searches for products online using Google to find relevant retailer URLs (Amazon and Best Buy).
- Scrapes the current price of products from product pages.
- Compares the current price against the original purchase price.
- Provides output to indicate whether the price has increased or decreased.
- Gmail Authentication: Uses the Gmail API to access and retrieve recent order confirmation emails.
- Purchase Information Extraction: Extracts product names, purchase amounts, and dates from email order confirmations.
- Natural Language Processing (NLP): Utilizes spaCy's Named Entity Recognition (NER) to identify product information.
- MySQL Database Integration: Stores purchase information for future reference and price tracking.

## Prerequisites

- Python 3.x
- Required Python packages:
    - `requests`
    - `beautifulsoup4`
    - `googlesearch-python`
    - `schedule`
    - `google-auth-oauthlib`
    - `google-auth-httplib2`
    - `google-api-python-client`
    - `spacy`
    - `mysql-connector-python`

You can install the required packages using:

```bash
pip install requests beautifulsoup4 googlesearch-python schedule google-auth-oauthlib google-auth-httplib2 google-api-python-client spacy mysql-connector-python
```

## Setup and Usage

1. **Clone the Repository**: Clone the repository to your local machine.
2. **Install Dependencies**: Use the `pip install` command above to install all the necessary Python packages.
3. **Set up Gmail API**: Follow the steps in the Gmail API Setup section to set up authentication.
4. **Configure Database**: Set up the MySQL database as described in the Database Configuration section.
5. **Modify the Script**:
    - Update the `products` list with the product names and their purchase prices for manual tracking.
    - Configure the database connection settings in the script.
6. **Run the Scripts**:
    - Run `python trackPrice.py` to manually track prices.
    - Run `python get_purchase_emails.py` to extract purchase information from emails and store it in the database.

## How It Works

1. **Email Extraction**: The script authenticates with Gmail API and retrieves recent order confirmation emails.
2. **Information Parsing**: Purchase details are extracted from emails using NLP techniques.
3. **Database Storage**: Extracted information is stored in the MySQL database.
4. **Product Search**: The script uses the `googlesearch` library to find product URLs on Amazon and Best Buy.
5. **Price Scraping**: Current prices are scraped from retailer pages using `BeautifulSoup`.
6. **Price Comparison**: Current prices are compared to original purchase prices, with results displayed to the user.

## Limitations and Future Improvements

- The script relies on the structure of product pages, which may change frequently.
- Using Google search can trigger CAPTCHA. Consider using dedicated search APIs like SerpAPI.
- Implement more robust error handling for network issues, blocked requests, etc.
- Expand retailer support beyond Amazon and Best Buy.
- Implement scheduling for automated price checks.
- Improve the extraction logic for a wider range of email formats.
- Integrate real-time price tracking APIs for more accurate results.


## Contributing

Contributions are welcome! Please fork this repository, make changes, and submit a pull request. You can contribute by improving extraction logic, integrating new APIs, expanding retailer support, or enhancing error handling and logging.

## Contact

For questions or suggestions, feel free to reach out or open an issue on the repository.

Happy Price Matching and Smart Shopping!

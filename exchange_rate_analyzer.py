import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import logging
import json
import time
from datetime import datetime
from scipy.stats import linregress

# Configuring logging
log_dir = os.path.join(os.getcwd(), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)  # Create the logs directory if it doesn't exist

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
currency_pair = "AUD_to_NZD" 
log_file = f'exchange_rate_analysis_log_{currency_pair}_{timestamp}.log'
log_file = os.path.join(log_dir, log_file)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file),  # Log messages are saved to this file
                        logging.StreamHandler()  # Log messages are printed to the console
                    ])
logger = logging.getLogger(__name__)

class ExchangeRateAnalyzer:
    """Class to fetch and analyze exchange rates from AUD to NZD."""
    
    def __init__(self, cache_file='exchange_rates_cache.json'):
        """Initialize the analyzer with an API key from an environment variable and optional caching."""
        self.api_key = os.getenv('EXCHANGE_RATE_API_KEY')
        if not self.api_key:
            raise ValueError("API key not found. Set the 'EXCHANGE_RATE_API_KEY' environment variable.")
        self.base_url = 'https://api.exchangeratesapi.io/v1/'

        self.base_currency = 'AUD'
        self.target_currency = 'NZD'
        self.cache_file = cache_file  
        self.file_cache = self.load_cache()  # Load existing file-based cache
        self.memory_cache = {}  # Initialize an empty dictionary for in-memory caching

    def load_cache(self):
        """
        Load the file-based cache from the specified JSON file within the 'cache' folder.
        
        This function attempts to read the cache file from the 'cache' directory and load its JSON content
        into a Python dictionary. If the file does not exist, it returns an empty dictionary, indicating an empty cache.
        
        Returns:
        dict: The content of the cache file as a dictionary or an empty dictionary if the file does not exist.
        """
        cache_dir = os.path.join(os.getcwd(), 'cache')
        cache_file_path = os.path.join(cache_dir, self.cache_file)
        
        try:
            with open(cache_file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.info("Cache file not found in the 'cache' folder. Initializing an empty cache.")
            return {}

    def load_file_cache(self):
        """
        Load the file-based cache from the specified JSON file.
        
        This function attempts to read the cache file and load its JSON content into a Python dictionary.
        If the file does not exist, it returns an empty dictionary, indicating an empty cache.
        
        Returns:
        dict: The content of the cache file as a dictionary or an empty dictionary if the file does not exist.
        """
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.info("Cache file not found. Initializing an empty cache.")
            return {}


    def get_cached_data(self, key):
        """
        Retrieve data from the cache using the specified key.
        
        This function first checks the in-memory cache for the data associated with the given key.
        If the data is not found in the in-memory cache, it falls back to the file-based cache.
        A cache hit in the file-based cache will result in updating the in-memory cache with the retrieved data.
        
        Args:
        key (str): The key used to retrieve data from the cache.
        
        Returns:
        The cached data associated with the key or None if the key is not found in the cache.
        """
        if key in self.memory_cache:
            logger.info(f"Memory cache hit for key: {key}")
            return self.memory_cache[key]

        if key in self.file_cache:
            logger.info(f"File cache hit for key: {key}")
            data = self.file_cache[key]
            self.memory_cache[key] = data  # Update in-memory cache
            return data

        return None


    def save_file_cache(self):
        """
        Save the current state of the file-based cache to the specified JSON file within the 'cache' folder.
        
        This function writes the content of the file-based cache (a Python dictionary) to the cache file in JSON format.
        It ensures that any updates to the cache during the application's runtime are persisted to disk.
        The cache file is stored within a directory named 'cache'.
        """
        # Ensure the 'cache' directory exists
        cache_dir = os.path.join(os.getcwd(), 'cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        cache_file_path = os.path.join(cache_dir, self.cache_file)

        with open(cache_file_path, 'w') as f:
            json.dump(self.file_cache, f)
        
        logger.info("Cache file has been updated with the latest data in the 'cache' folder.")

    def set_cached_data(self, key, value):
        """
        Update the cache with the specified key-value pair.
        
        This function updates both the in-memory cache and the file-based cache with the given key-value pair.
        After updating the in-memory cache, it immediately persists changes to the file-based cache by saving it to disk.
        
        Args:
        key (str): The key under which the data should be stored in the cache.
        value: The data to be cached associated with the key.
        """
        self.memory_cache[key] = value
        self.file_cache[key] = value
        self.save_file_cache()  # Persist the updated file-based cache
        logger.info(f"Data for key: {key} has been updated in both memory and file cache.")

    def fetch_exchange_rates(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch exchange rates from the specified start date to the end date using the 'historical' endpoint.
        This function checks the in-memory cache first for data, then the file-based cache, and finally fetches from the API if the data is not cached.
        Retrieved data is cached in both in-memory and file-based caches for future quick access and persistence.
        
        Args:
        start_date (str): The start date for fetching exchange rates in 'YYYY-MM-DD' format.
        end_date (str): The end date for fetching exchange rates in 'YYYY-MM-DD' format.

        Returns:
        pd.DataFrame: A DataFrame containing the exchange rates for each day in the specified date range, sorted by date.
        """
        logger.info("Fetching exchange rates from %s to %s using the 'historical' endpoint", start_date, end_date)
        all_rates = []

        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        current_date_obj = start_date_obj

        max_attempts = 3  # Define the maximum number of retry attempts
        backoff_time = 1  # Initial backoff time in seconds

        while current_date_obj <= end_date_obj:
            current_date_str = current_date_obj.strftime("%Y-%m-%d")
            cache_key = f"{self.base_currency}_{self.target_currency}_{current_date_str}"

            # Attempt to retrieve cached data first
            cached_data = self.get_cached_data(cache_key)

            if cached_data is None:
                logger.info(f"Cache miss for {current_date_str}. Fetching fresh data.")
                attempt = 0
                while attempt < max_attempts:
                    try:
                        # Construct the URL using base_url and the current date
                        url = f"{self.base_url}{current_date_str}"
                        params = {'access_key': self.api_key, 'base': self.base_currency, 'symbols': self.target_currency}

                        response = requests.get(url, params=params)
                        response.raise_for_status()  # Raises an HTTPError for bad responses
                        if not response.ok:
                            logger.error(f"Failed to fetch data: {response.status_code} {response.json().get('error', '')}")
                            return pd.DataFrame(columns=['Date', 'ExchangeRate'])

                        data = response.json()

                        if data.get('success', True): 
                            try:
                                rate = data['rates'][self.target_currency]
                                all_rates.append((current_date_str, rate))
                                # Update cache with new data
                                self.set_cached_data(cache_key, rate)
                                break  # Exit retry loop on success
                            except KeyError:
                                logger.error(f"Rate for '{self.target_currency}' not found on {current_date_str}")
                        else:
                            logger.error("Failed to fetch rates for %s: %s", current_date_str, data.get('error', {}).get('info', 'No error info'))
                            break  # Exit retry loop on API error
                    except requests.exceptions.RequestException as e:
                        logger.warning("Request failed for %s, attempt %d: %s", current_date_str, attempt + 1, e)
                        attempt += 1
                        if attempt < max_attempts:
                            time.sleep(backoff_time * 2 ** attempt)  # Exponential backoff
            else:
                logger.info(f"Using cached data for {current_date_str}.")
                all_rates.append((current_date_str, cached_data))

            # Move to the next day
            current_date_obj += timedelta(days=1)

        # Construct a DataFrame from the fetched rates
        if all_rates:
            df = pd.DataFrame(all_rates, columns=['Date', 'ExchangeRate'])
            df['Date'] = pd.to_datetime(df['Date'])
            df.sort_values('Date', inplace=True)
            logger.info("Successfully fetched and processed exchange rates")
            return df
        else:
            logger.warning("No exchange rates fetched.")
            return pd.DataFrame(columns=['Date', 'ExchangeRate'])

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the data for analysis with data quality checks."""
        logger.info("Starting data preprocessing")
        if df.isnull().values.any():
            logger.warning("Data contains null values. Applying forward fill.")
        
        try:
            df.set_index('Date', inplace=True)
            df = df.asfreq('D').ffill()  # Forward fill to handle missing values
            df.reset_index(inplace=True)
            logger.info("Data preprocessing completed successfully")
        except Exception as e:
            logger.error("Error during data preprocessing: %s", e)
            raise
        
        return df

    def analyze_data(self, df: pd.DataFrame):
        """Perform comprehensive analysis including best, worst, average rates, trend analysis, and volatility analysis."""
        
        logger.info("Starting data analysis")

        try:
            # Basic analysis
            best_rate = df.loc[df['ExchangeRate'].idxmax()]
            worst_rate = df.loc[df['ExchangeRate'].idxmin()]
            average_rate = df['ExchangeRate'].mean()

            # Adding a 7-day moving average for trend analysis
            df['7DayMA'] = df['ExchangeRate'].rolling(window=7).mean()

            # Volatility and trend analysis
            high_volatility_date, max_volatility = self.analyze_volatility(df)
            trend, slope, intercept = self.analyze_trends(df)

            # Plotting with annotations for best, worst rates, and trend analysis
            self.plot_exchange_rate_analysis(df, best_rate, worst_rate, average_rate, trend, slope, intercept)

            logger.info("Data analysis and enhanced visualization completed successfully")
        except Exception as e:
            logger.error("Error during data analysis: %s", e)
            raise
            

    def analyze_variability(self, df: pd.DataFrame):
        """Calculate and log the standard deviation and range of exchange rates."""
        
        std_dev = df['ExchangeRate'].std()
        rate_range = df['ExchangeRate'].max() - df['ExchangeRate'].min()
        logger.info(f"Standard Deviation of Exchange Rates: {std_dev:.4f}")
        logger.info(f"Range of Exchange Rates: {rate_range:.4f}")
        
        return std_dev, rate_range


    def find_notable_observations(self, df: pd.DataFrame):
        """Identify and log the dates with the highest and lowest exchange rates."""
        
        highest_rate_date = df.loc[df['ExchangeRate'].idxmax(), 'Date'].strftime('%Y-%m-%d')
        lowest_rate_date = df.loc[df['ExchangeRate'].idxmin(), 'Date'].strftime('%Y-%m-%d')
        logger.info(f"Highest exchange rate observed on: {highest_rate_date}")
        logger.info(f"Lowest exchange rate observed on: {lowest_rate_date}")
        
        return highest_rate_date, lowest_rate_date

    def analyze_volatility(self, df: pd.DataFrame):
        """Analyze and log the volatility of exchange rates using a rolling standard deviation."""
        
        df['RollingStd'] = df['ExchangeRate'].rolling(window=7).std()
        high_volatility_date = df.loc[df['RollingStd'].idxmax(), 'Date'].strftime('%Y-%m-%d')
        logger.info(f"Date with highest volatility observed on: {high_volatility_date}")
        
        return high_volatility_date, df['RollingStd'].max()

    

    def analyze_trends(self, df: pd.DataFrame):
        """Analyze and log the overall trend in exchange rates using linear regression."""
        
        df['Timestamp'] = df['Date'].map(datetime.timestamp)
        slope, intercept, r_value, p_value, std_err = linregress(df['Timestamp'], df['ExchangeRate'])
        trend = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        logger.info(f"The overall trend in the exchange rate is {trend}")
        
        return trend, slope, intercept


    def generate_insights(self, df: pd.DataFrame):
        """Compile insights from the data analysis into a textual summary, print it, and save to a text file."""
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        currency_pair = f"{self.base_currency}_to_{self.target_currency}"
        # Ensure the 'insights' directory exists
        insights_dir = os.path.join(os.getcwd(), 'insights')
        if not os.path.exists(insights_dir):
            os.makedirs(insights_dir)

        insights_file = f'exchange_rate_insights_{currency_pair}_{timestamp}.txt'

        insights_file_path = os.path.join(insights_dir, insights_file)

        best_rate = df.loc[df['ExchangeRate'].idxmax()]
        worst_rate = df.loc[df['ExchangeRate'].idxmin()]
        average_rate = df['ExchangeRate'].mean()
        high_volatility_date, max_volatility = self.analyze_volatility(df)
        trend, slope, intercept = self.analyze_trends(df)

        insights = [
            f"Best Rate: {best_rate['ExchangeRate']} on {best_rate['Date'].date()}",
            f"Worst Rate: {worst_rate['ExchangeRate']} on {worst_rate['Date'].date()}",
            f"Average Rate over the period: {average_rate:.4f}",
            f"Highest volatility observed on: {high_volatility_date} with a standard deviation of {max_volatility:.4f}",
            f"The overall trend in the exchange rate is {trend}",
        ]
        insights_text = "\n".join(insights)

        # Print insights
        print("Exchange Rate Analysis Insights:\n")
        print(insights_text)

        # Save insights to a text file
        with open(insights_file_path, 'w') as f:
            f.write("Exchange Rate Analysis Insights:\n\n")
            f.write(insights_text)

        logger.info(f"Insights generated and saved successfully in {insights_file}.")


    def plot_exchange_rate_analysis(self, df: pd.DataFrame, best_rate: pd.Series, worst_rate: pd.Series, average_rate: float, trend: str, slope: float, intercept: float):
        """Plot the exchange rates with annotations for best, worst rates, average rate, and trend line."""

        plt.figure(figsize=(10, 6))
        plt.plot(df['Date'], df['ExchangeRate'], marker='o', linestyle='-', label='Daily Rate')
        plt.plot(df['Date'], df['7DayMA'], color='red', linestyle='-', label='7-Day Moving Average')

        # Highlight the best and worst rates
        plt.scatter(best_rate['Date'], best_rate['ExchangeRate'], color='green', label='Best Rate', zorder=5)
        plt.scatter(worst_rate['Date'], worst_rate['ExchangeRate'], color='red', label='Worst Rate', zorder=5)

        # Annotate the average rate line and trend line
        plt.axhline(y=average_rate, color='blue', linestyle='--', label='Average Rate')

        # Calculate and plot the trend line
        earliest_date, latest_date = df['Date'].min(), df['Date'].max()
        plt.plot([earliest_date, latest_date], [earliest_date.timestamp() * slope + intercept, latest_date.timestamp() * slope + intercept], color='purple', linestyle='-', label='Trend Line')

        plt.title('Exchange Rate Over Time with Annotations')
        plt.xlabel('Date')
        plt.ylabel('Exchange Rate')
        plt.legend()
        plt.grid(True)
        
        # Ensure the 'charts' directory exists
        charts_dir = os.path.join(os.getcwd(), 'charts')
        if not os.path.exists(charts_dir):
            os.makedirs(charts_dir)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        currency_pair = f"{self.base_currency}_to_{self.target_currency}"
        chart_file = f'exchange_rate_chart_{currency_pair}_{timestamp}.png'

        chart_file_path = os.path.join(charts_dir, chart_file)
        plt.savefig(chart_file_path)  # Save the chart as an image file
        plt.show()
        logger.info(f"Chart saved successfully in {chart_file}.")
        
def main():
    # Initialize the ExchangeRateAnalyzer
    analyzer = ExchangeRateAnalyzer()
    
    # Define the date range for the past 30 days
    start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.today().strftime('%Y-%m-%d')
    
    # Fetch exchange rates for the specified date range
    logger.info("Fetching exchange rates from %s to %s", start_date, end_date)
    df = analyzer.fetch_exchange_rates(start_date, end_date)
    
    # Preprocess the fetched data
    logger.info("Preprocessing the fetched data")
    df_preprocessed = analyzer.preprocess_data(df)
    
    # Analyze the preprocessed data
    logger.info("Analyzing the preprocessed data")
    analyzer.analyze_data(df_preprocessed)
    

    # Generate and save insights and chart
    analyzer.generate_insights(df_preprocessed)

if __name__ == "__main__":
    main()

# ExchangeRateAnalyzer
ExchangeRateAnalyzer is a Python application designed to fetch historical exchange rates between two currencies, perform data preprocessing, and analyze the exchange rate trends. This project includes functionality for data fetching, preprocessing, trend analysis, and visualization. It also includes a testing suite to ensure the application's reliability and correctness.
## Code Structure
The codebase of ExchangeRateAnalyzer is structured for clarity and maintainability. The main functionalities (API connection, data preprocessing, analysis, etc.) are modularized into separate functions or classes. This structure facilitates easy updates, testing, and scalability of the application.
## API Connection
The ExchangeRateAnalyzer connects to an external exchange rates API to fetch historical exchange rate data between two specified currencies. The connection is established using the Python requests library. Users must provide a valid API key, which is set as an environment variable or directly within the application configuration.

## Data Preprocessing
After fetching the data, the application performs several preprocessing steps to ensure data quality and consistency. This includes filling in any missing dates in the historical data range and applying forward filling for missing exchange rate values to maintain data continuity.

## Caching Mechanism
To optimize performance and reduce unnecessary API calls, ExchangeRateAnalyzer implements a caching mechanism. Once the data for a specific date range is fetched, it's stored locally. Subsequent requests for the same date range utilize the cached data instead of making another API call.

## Error Handling
The application includes robust error handling to manage potential issues such as API connectivity problems, invalid responses, or data processing errors. These errors are logged with appropriate error messages to assist in troubleshooting.

## Data Quality Checks
ExchangeRateAnalyzer performs data quality checks to ensure the integrity of the fetched and processed data. This includes validating the format and range of dates and ensuring the exchange rate values are numerical and within expected bounds.

## Analysis and Insights
The application analyzes the preprocessed exchange rate data to extract valuable insights. This includes identifying trends, calculating average exchange rates over the specified period, and highlighting significant fluctuations. The results are presented both textually as insights and visually through generated charts.

## Logging
Logging is an integral part of ExchangeRateAnalyzer, providing visibility into the application's operation and aiding in debugging. The application logs key events, information messages, warnings, and errors along with their timestamps.

## Correctness
The application's correctness is ensured through comprehensive unit tests that cover a wide range of scenarios, including edge cases. By simulating various conditions such as API failures, data inconsistencies, and caching behaviors, we validate the accuracy and reliability of the ExchangeRateAnalyzer.

## Test Coverage
In the test suite for ExchangeRateAnalyzer, we have devised five specific test cases to ensure the application's robustness and reliability across various scenarios. 
Below is a brief overview of each test case and its purpose:
* Fetch Exchange Rates Test: Ensures accurate retrieval of exchange rate data for specified date ranges.
* Preprocess Data Test: Verifies the correct handling and forward-filling of missing dates and values in the data.
* API Failure Handling Test: Confirms that the application gracefully manages API failures, maintaining stability and logging errors.
* Cache Utilization Test: Checks that cached data is used effectively to reduce redundant API calls and enhance performance.
* Data Completeness Test: Assesses the application's ability to ensure a complete dataset by identifying and filling in missing information.
These tests collectively ensure the application's functionality, reliability, and efficiency across various operational scenarios.

## Extensibility
ExchangeRateAnalyzer's modular design and clear code structure make it straightforward to build upon its existing foundation. Whether it's extending the range of supported currencies or adding sophisticated analytical features, the application is poised for growth and adaptation to meet evolving user needs and market demands.

### Key aspects of its extensibility include:
* Support for More Currency Pairs: The architecture allows for easy addition of new currency pairs. Users can extend the application's capabilities by simply adding new pairs to the configuration, without the need for significant code changes.
* Real-Time Data Analysis: Extend the application to analyze real-time exchange rate data, offering more immediate insights into currency market fluctuations.
* Predictive Modeling: Incorporate machine learning models to predict future exchange rate trends based on historical data, providing users with forward-looking analysis.
* Custom Alerts: Implement a feature to set up custom alerts for significant exchange rate changes, helping users stay informed of critical market movements.
* Integration with Financial Platforms: Enhance the application's utility by integrating with financial platforms and services, allowing users to act on the insights directly within their preferred financial ecosystem.

### Streamlined Error Monitoring and Notifications
Integrate error monitoring and notification systems to ensure timely awareness and response to critical issues:

#### Monitoring Integration 
  Incorporate connections to monitoring systems like Sentry, New Relic, or Datadog. These platforms can aggregate error logs, provide real-time alerts, and offer insights into application performance and health.

#### Email Alerts
Implement functionality to send automated email notifications in case of critical failures or significant data anomalies. Utilize SMTP libraries or email services like SendGrid for streamlined integration.

####  Messaging Platform Notifications
Enable notifications to messaging platforms such as Slack or Microsoft Teams for immediate alerts. This can be achieved using webhooks or platform-specific APIs, allowing for real-time error reporting and team collaboration in resolving issues.

### Enhanced Insights Storage and Accessibility
Extend the application's capability to store and access insights through various storage solutions and formats:

#### Database Storage
Facilitate the writing of insights and analysis results to databases, both SQL (like PostgreSQL, MySQL) and NoSQL (like MongoDB, DynamoDB). This approach allows for better data management, querying capabilities, and integration with other systems.

#### Alternative File Formats
Besides traditional text files, consider supporting additional formats for insights storage, such as JSON, CSV, or Excel files. This flexibility enables easier integration with data analysis tools and platforms.

#### Data Visualization Platforms
Explore options to push insights directly to data visualization tools or platforms like Tableau, Power BI, or Grafana. This can provide more interactive and intuitive representations of the analysis results, enhancing the decision-making process.

#### API Endpoints for Insights 
Develop API endpoints to serve the insights and analysis results, making it easier for other systems and applications to consume and act upon the data programmatically.

These extensibility enhancements not only improve the robustness and user-friendliness of the ExchangeRateAnalyzer but also ensure that it can seamlessly fit into larger ecosystems and workflows, accommodating various user needs and operational requirements.

## Maintainability
Maintainability is a key focus in the development of ExchangeRateAnalyzer. The use of well-established design patterns, thorough documentation within the code, and adherence to best practices ensure that the codebase remains clean, understandable, and easy to modify or extend.

## Getting Started
## Prerequisites
* Python 3.8 or higher
* Docker (for containerization)
* A valid API key for the exchange rates API, you can get from sigining up with https://manage.exchangeratesapi.io/
#### Installation
Clone the repository:
```console
git clone https://github.com/yassienshaalan/ExchangeRateAnalyzer.git
```
Navigate to the project directory:
```console
cd ExchangeRateAnalyzer
```
Install the required Python packages:
```
pip install -r requirements.txt
```
Running the Application
To run ExchangeRateAnalyzer, execute the following command in the project directory:

```
python exchange_rate_analyzer.py
```
Running Tests
The project includes a test suite test_exchange_rate_analyzer.py to validate the functionality. To run the tests, execute:

```
python -m unittest test_exchange_rate_analyzer.py
```
#### Dockerization
This project can be containerized using Docker. Follow these steps to build and run the application within a Docker container:

Build the Docker image:

```
docker build -t exchange-rate-analyzer .
```
This process will also run the test suite as part of the image build process.

Run the Docker container:

```
docker run -it --rm exchange-rate-analyzer
```

#### Directories
* Logs: The application logs its operations, which can be found in the attached app.log file.
* Insights: After analyzing the exchange rates, insights are generated and saved in the insights.txt file.
* Charts: Visualization of the exchange rate trends is available in the exchange_rate_chart.png file.

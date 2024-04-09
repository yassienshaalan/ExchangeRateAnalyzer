import unittest
from unittest.mock import patch, Mock
import pandas as pd
from exchange_rate_analyzer import ExchangeRateAnalyzer
import numpy as np

class TestExchangeRateAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = ExchangeRateAnalyzer(cache_file='test_cache.json')  # Specify a test cache file to avoid interfering with the actual cache

    @patch('exchange_rate_analyzer.requests.get')
    def test_preprocess_data(self, mock_get):
        # Assuming each date requires a separate API call
        mock_responses = [
            {'success': True, 'rates': {'NZD': 1.072039}},
            {'success': True, 'rates': {'NZD': 1.072116}},
            {'success': True, 'rates': {'NZD': 1.074481}}
        ]
        mock_get.return_value.json.side_effect = [response for response in mock_responses]

        start_date = '2024-03-10'
        end_date = '2024-03-12'
        df = self.analyzer.fetch_exchange_rates(start_date, end_date)

        # Assertions
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        expected_dates = pd.to_datetime(['2024-03-10', '2024-03-11', '2024-03-12'])
        self.assertTrue((df['Date'].dt.date == expected_dates.date).all())
        expected_rates = np.array([1.072039, 1.072116, 1.074481])
        self.assertTrue(np.isclose(df['ExchangeRate'].values, expected_rates).all())


    @patch('exchange_rate_analyzer.requests.get')
    def test_fetch_exchange_rates_with_caching(self, mock_get):
        self.analyzer.memory_cache.clear()
        self.analyzer.file_cache.clear()
        
        # Setup mock responses to mimic the actual data structure and values
        mock_responses = [
            {'success': True, 'rates': {'NZD': 1.078546}},  # For 2024-03-15
            {'success': True, 'rates': {'NZD': 1.078546}},  # For 2024-03-16
        ]
        mock_get.side_effect = [unittest.mock.Mock(json=lambda: mock_responses[i]) for i in range(2)]

        # Fetch rates for the date range not cached
        self.analyzer.fetch_exchange_rates('2024-03-15', '2024-03-16')

        # Assertions to ensure 'get' was called twice, once for each day
        self.assertEqual(mock_get.call_count, 2)

    def test_data_completeness_and_forward_filling(self):
        """Test that preprocessing forward-fills missing data for completeness."""
        # Simulate data with a missing date
        data = {
            'Date': pd.to_datetime(['2024-03-10', '2024-03-12']),
            'ExchangeRate': [1.072039, 1.074481]
        }
        df = pd.DataFrame(data)

        preprocessed_df = self.analyzer.preprocess_data(df)
        self.assertEqual(len(preprocessed_df), 3)  # Check for 3 days of data including the missing one

        # Ensure the missing date ('2024-03-11') has been forward-filled
        missing_date_rate = preprocessed_df.loc[preprocessed_df['Date'] == pd.to_datetime('2024-03-11'), 'ExchangeRate'].values[0]
        self.assertEqual(missing_date_rate, data['ExchangeRate'][0])  # Check the rate is forward-filled from '2024-03-10'


    @patch('exchange_rate_analyzer.requests.get')
    def test_api_failure_handling(self, mock_get):
        """Test the handling of API failures."""
        # Clear any cached data
        self.analyzer.memory_cache.clear()
        self.analyzer.file_cache.clear()

        # Setup mock response to simulate an API failure
        mock_get.return_value = Mock(ok=False, status_code=500, json=lambda: {"error": "Internal Server Error"})
        
        start_date = '2024-03-15'
        end_date = '2024-03-16'
        df = self.analyzer.fetch_exchange_rates(start_date, end_date)
        self.assertTrue(df.empty)

    def test_cache_utilization(self):
        """Test that the analyzer uses cached data when available."""
        cache_key = 'AUD_NZD_2024-03-15'
        expected_rate = 1.078546
        self.analyzer.set_cached_data(cache_key, expected_rate)  # Manually set cache

        with patch('exchange_rate_analyzer.requests.get') as mock_get:
            df = self.analyzer.fetch_exchange_rates('2024-03-15', '2024-03-15')

            mock_get.assert_not_called()  # Ensure no API call is made

        self.assertEqual(df.loc[0, 'ExchangeRate'], expected_rate)  # Check cached rate is used


if __name__ == '__main__':
    unittest.main()
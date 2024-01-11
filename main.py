import os
import csv

from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

load_dotenv()

GA4_ID = os.getenv('GA4_ID')
property_id = f"properties/{GA4_ID}"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

client = BetaAnalyticsDataClient()

def report(start_date, end_date):
    request = RunReportRequest(
        property=property_id,
        dimensions=[
            Dimension(name="date"),
            Dimension(name="pagePath"),
            Dimension(name="eventName")
        ],
        metrics=[
            Metric(name="eventCount"),
            Metric(name="activeUsers")
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter={
            "filter": {
                "field_name": "eventName",
                "string_filter": {
                    "value": "page_view",
                    "match_type": "EXACT"
                }
            }
        }
    )

    return client.run_report(request)

def make_csv_file(csv_file, response):
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Page', 'Event', 'Event Count', 'Active Users'])

        for row in response.rows:
            date = row.dimension_values[0].value
            page_path = row.dimension_values[1].value
            event_name = row.dimension_values[2].value
            event_count = row.metric_values[0].value
            active_users = row.metric_values[1].value
            writer.writerow([date, page_path, event_name, event_count, active_users])


def main():
    today = datetime.today().strftime('%Y-%m-%d')
    response = report(today, today)

    csv_path = Path('csv') / f"ga4_data_{today}.csv"
    make_csv_file(csv_path, response)


if __name__ == '__main__':
    main()

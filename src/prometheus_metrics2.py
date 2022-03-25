"""Application exporter"""

import os
import time
from prometheus_client import start_http_server, Gauge
import requests
import logging


# Create and configure logger
logging.basicConfig(format='%(asctime)s %(message)s') 
# Creating an object
logger = logging.getLogger("Pipeline-metrics")
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, polling_interval_seconds=5):
        self.polling_interval_seconds = polling_interval_seconds

        # Prometheus metrics to collect
        self.average_latency = Gauge("average_latency", "Average Latency")
        self.average_throughput = Gauge("average_throughput", "Average Throughput")

        self.fps_100_avg = Gauge("fps_100_avg", "Average pipeline FPS for past 100 frames")
        self.frame_counts = Gauge("frame_count", "Frame Count")

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            logger.info("Fetching logs")
            self.fetch()
            logger.info("Logs fetched")
            logger.info("Sleeping for {} seconds".format(self.polling_interval_seconds))
            time.sleep(self.polling_interval_seconds)


    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """

        try:
            # Fetch raw status data from the application
            url="http://" + os.environ['IP_ADDRESS'] + ":5011/healthStatus"
            logger.debug(url)
            resp = requests.get(url, timeout=1)
            status_data = resp.json()

        except ConnectionError as e:
            resp = None
        except Exception as e:
            resp = None

        if resp is not None:
            try:

                self.fps_100_avg.set(status_data["fps"][1]["avg"])
                self.frame_counts.set(status_data["frame_counts"]["total"])

            except KeyError as k:
               logger.error("Key words not found! ") 

        else:
            logger.info("Could not fetch health status")
        
        logger.info("Done fetching health status")

        try:
            # Fetch raw status data from the application
            url="http://" + os.environ['IP_ADDRESS'] + ":5011/performance"
            logger.debug(url)
            resp = requests.get(url, timeout=1)
            status_data = resp.json()

        except ConnectionError as e:
            resp = None
        except Exception as e:
            resp = None

        if resp is not None:
            try:

                self.average_latency.set(float(status_data["summary"]["average latency"][:-2]))
                self.average_throughput.set(float(status_data["summary"]["average throughput"][:-3]))
                logger.debug(float(status_data["summary"]["average latency"][:-2]))
                logger.debug(float(status_data["summary"]["average throughput"][:-3]))

            except KeyError as k:
               logger.error("Key words not found! ") 
        else:
            logger.info("Could not fetch performance")

        logger.info("Done fetching performance")

def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "1"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "9877"))
    # app_port = int(os.getenv("APP_PORT", "80"))

    logger.info("Running")
    app_metrics = AppMetrics(
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port)
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()

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
        # self.app_port = app_port
        self.polling_interval_seconds = polling_interval_seconds

        # Prometheus metrics to collect
        self.average_latency = Gauge("average_latency", "Average Latency")
        self.average_throughput = Gauge("average_throughput", "Average Throughput")
        self.fps = Gauge("fps", "FPS")
        # self.health = Enum("app_health", "Health", states=["healthy", "unhealthy"])
        # self.ip_add = ip_add

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
            resp = requests.get(url="http://192.168.41.5:5011/performance", timeout=1)
            status_data = resp.json()

        except KeyError as k:
            resp = None
        except ConnectionError as e:
            resp = None
        except Exception as e:
            resp = None

        if resp is not None and status_data==200:
            # Metrics collector
            average_latency = float(status_data["summary"]["average latency"][:-2])
            average_throughput = float(status_data["summary"]["average throughput"][:-3])
            fps = float(status_data["summary"]["fps"][:-3])
        else:
            average_latency = 0
            average_throughput = 0
            fps = 0
        
        logging.info("Done fetching")

        # Update Prometheus metrics with application metrics
        self.average_latency.set(average_latency)
        self.average_throughput.set(average_throughput)
        self.fps.set(fps)
        #self.health.state(status_data["health"])

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

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
        # self.average_latency = Gauge("average_latency", "Average Latency")
        # self.average_throughput = Gauge("average_throughput", "Average Throughput")
        # self.fps = Gauge("fps", "FPS")

        # self.health = Enum("app_health", "Health", states=["healthy", "unhealthy"])
        # self.ip_add = ip_add

        self.fps_10 = {}
        self.fps_100 = {}
        self.frame_counts = {}
        self.frame_drops = {}
        self.latency_10 = {}
        self.latency_100 = {}

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
            resp = requests.get(url="http://192.168.41.5:5011/healthStatus", timeout=1)
            status_data = resp.json()

        except ConnectionError as e:
            resp = None
        except Exception as e:
            resp = None

        if resp is not None:

            # Metrics collector
            # average_latency = float(status_data["summary"]["average latency"][:-2])
            # average_throughput = float(status_data["summary"]["average throughput"][:-3])
            # fps = float(status_data["summary"]["fps"][:-3])

            try:
                for cam_id in status_data["fps"][0]:
                    logger.debug(status_data["fps"][0])
                    if cam_id=="avg" or cam_id=="duration":
                        continue
                    if cam_id not in self.fps_10:
                        fps = Gauge("fps_10_{}".format(cam_id), "FPS for past 10 frames")
                        self.fps_10[cam_id] = fps
                        self.fps_10[cam_id].set(status_data["fps"][0][cam_id])
                    else:
                        self.fps_10[cam_id].set(status_data["fps"][0][cam_id])

                for cam_id in status_data["fps"][1]:
                    logger.debug(status_data["fps"][1])
                    if cam_id=="avg" or cam_id=="duration":
                        continue
                    if cam_id not in self.fps_100:
                        fps = Gauge("fps_100_{}".format(cam_id), "FPS for past 100 frames")
                        self.fps_100[cam_id] = fps
                        self.fps_100[cam_id].set(status_data["fps"][1][cam_id])
                    else:
                        self.fps_100[cam_id].set(status_data["fps"][1][cam_id])

                for module_name in status_data["frame_counts"]:
                    if module_name=="input-default" or module_name=="perimeter3-api_server" or module_name=="total":
                        continue 
                    if module_name not in self.frame_counts:
                        fc = Gauge("fc_{}".format(module_name), "Frame Count")
                        self.frame_counts[module_name] = fc
                        self.frame_counts[module_name].set(status_data["frame_counts"][module_name])
                    else:
                        self.frame_counts[module_name].set(status_data["frame_counts"][module_name])

                for module_name in status_data["frame_drops"]:
                    if module_name=="input-default" or module_name=="perimeter3-api_server" or module_name=="total":
                        continue 
                    if module_name not in self.frame_drops:
                        fd = Gauge("fd_{}".format(module_name), "Frame Drops")
                        self.frame_drops[module_name] = fd
                        self.frame_drops[module_name].set(status_data["frame_drops"][module_name])
                    else:
                        self.frame_drops[module_name].set(status_data["frame_drops"][module_name])

                for module_name in status_data["latency"][0]:
                    logger.debug(status_data["latency"][0])
                    if module_name=="avg" or module_name=="duration":
                        continue
                    if module_name not in self.latency_10:
                        lat = Gauge("Latency_10_{}".format(module_name), "Latency for past 10 frames")
                        self.latency_10[module_name] = lat
                        self.latency_10[module_name].set(status_data["latency"][0][module_name])
                    else:
                        self.latency_10[module_name].set(status_data["latency"][0][module_name])

                for module_name in status_data["latency"][1]:
                    logger.debug(status_data["latency"][1])
                    if module_name=="avg" or module_name=="duration":
                        continue
                    if module_name not in self.latency_100:
                        lat = Gauge("Latency_100_{}".format(module_name), "Latency for past 100 frames")
                        self.latency_100[module_name] = lat
                        self.latency_100[module_name].set(status_data["latency"][1][module_name])
                    else:
                        self.latency_100[module_name].set(status_data["latency"][1][module_name])

            except KeyError as k:
               logger.error("Key words not found! ") 

        else:
            logger.info("Could not fetch details")
        
        logger.info("Done fetching")

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

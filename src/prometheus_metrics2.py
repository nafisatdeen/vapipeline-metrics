"""Application exporter"""

import os
import time
from prometheus_client import start_http_server, Gauge
import requests
import logging
# import yaml
# from yaml.loader import SafeLoader

# from kubernetes import client, config

# config.load_kube_config("/app/.kube/config")
# v1 = client.CoreV1Api()
# ret = v1.read_namespaced_pod(name='people-analytics',namespace='vapipeline')


# Create and configure logger
logging.basicConfig(format='%(asctime)s %(message)s') 
# Creating an object
logger = logging.getLogger("Pipeline-metrics")
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

# with open('/app/config/config.yaml') as f:
#     data = yaml.load(f, Loader=SafeLoader)


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

        self.fps_10 = Gauge("fps_10", "FPS for past 10 frames", ["label1"])
        self.fps_10_total = Gauge("fps_10_total", "Total FPS for past 10 frames", ["label1"])
        self.fps_100 = Gauge("fps_100", "FPS for past 10 frames", ["label1"])
        self.fps_100_total = Gauge("fps_100_total", "Total FPS for past 100 frames", ["label1"])
        self.frame_counts = Gauge("frame_count", "Frame Count", ["label1"])
        self.frame_drops = Gauge("frame_drops", "Frame Drops", ["label1"])
        self.latency_10 = Gauge("latency_10", "Latency for past 10 frames", ["label1"])
        self.latency_100 = Gauge("latency_100", "Latency for past 100 frames", ["label1"])
        self.latency_10_avg = Gauge("latency_10_avg", "Avg latency for past 10 frames", ["label1"])
        self.latency_100_avg = Gauge("latency_100_avg", "Avg latency for past 100 frames", ["label1"])

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

            # Metrics collector
            # average_latency = float(status_data["summary"]["average latency"][:-2])
            # average_throughput = float(status_data["summary"]["average throughput"][:-3])
            # fps = float(status_data["summary"]["fps"][:-3])

            try:
                for cam_id in status_data["fps"][0]:
                    logger.debug(status_data["fps"][0])
                    if cam_id=="duration" or cam_id=="avg":
                        continue
                    self.fps_10.labels(cam_id).set(status_data["fps"][0][cam_id])
                self.fps_10_total.labels("total").set(status_data["fps"][0]["avg"])

                for cam_id in status_data["fps"][1]:
                    logger.debug(status_data["fps"][1])
                    if cam_id=="duration" or cam_id=="avg":
                        continue
                    self.fps_100.labels(cam_id).set(status_data["fps"][1][cam_id])
                self.fps_100_total.labels("total").set(status_data["fps"][1]["avg"])

                for module_name in status_data["frame_counts"]:
                    if module_name=="input-default" or module_name=="perimeter3-api_server":
                        continue 
                    self.frame_counts.labels(module_name).set(status_data["frame_counts"][module_name])

                for module_name in status_data["frame_drops"]:
                    if module_name=="input-default" or module_name=="perimeter3-api_server":
                        continue 
                    self.frame_drops.labels(module_name).set(status_data["frame_drops"][module_name])

                for module_name in status_data["latency"][0]:
                    logger.debug(status_data["latency"][0])
                    if module_name=="avg" or module_name=="duration":
                        continue
                    self.latency_10.labels(module_name).set(status_data["latency"][0][module_name])
                self.latency_10_avg.labels("avg").set(status_data["latency"][0]["avg"])

                for module_name in status_data["latency"][1]:
                    logger.debug(status_data["latency"][1])
                    if module_name=="avg" or module_name=="duration":
                        continue
                    self.latency_100.labels(module_name).set(status_data["latency"][1][module_name])
                self.latency_100_avg.labels("avg").set(status_data["latency"][1]["avg"])

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

import json
import os
from boto.ec2 import cloudwatch
from cgminer_api import APIClient
from datetime import datetime
from statsd import statsd
from time import sleep


config = json.load(open("config.json"))
HOSTNAME = config["hostname"]
ENABLE_CLOUDWATCH = True
ENABLE_DATADOG = True
REPORT_INTERVAL = 10


class CloudWatchMetrics(object):
    def __init__(self):
        self.cloud_watch = cloudwatch.connect_to_region(
            aws_access_key_id=config["aws_access_key_id"],
            aws_secret_access_key=config["aws_secret_access_key"],
            region="us-east-1")

    def report_metric(self, namespace, name, value, unit=None, dimensions=None):
        self.cloud_watch.put_metric_data(
            namespace=namespace,
            name=name,
            value=value,
            unit=unit,
            dimensions=dimensions)


cgminer = APIClient()
cloud_watch = CloudWatchMetrics()
while True:
    try:
        summary = cgminer.summary()
        devs = cgminer.devs()
        print "[%s] API Query OK" % datetime.now()
    except Exception, e:
        print "Error while querying CGMiner: %s" % e
        sleep(REPORT_INTERVAL)
        continue

    # Global stats
    statsd.gauge("cgminer.work_util", int(float(summary["Work Utility"])))

    # GPU stats (temperature, KHash/s, etc.)
    for name,info in devs.iteritems():
        if not "GPU" in name: continue
        gpu_id = int(name.split("=")[1])
        temp = float(info["Temperature"])
        khash_s = float(info["MHS 5s"]) / 1000
        fan_speed = int(info["Fan Speed"])
        fan_pct = int(info["Fan Percent"])
        hw_errors = int(info["Hardware Errors"])
        if ENABLE_DATADOG:
            gauge = lambda k,v: statsd.gauge(k, v, tags=["gpu:%s" % gpu_id])
            gauge("gpu.temp", temp)
            gauge("gpu.khash_s", khash_s)
            gauge("gpu.fan_rpm", fan_speed)
            gauge("gpu.fan_pct", fan_pct)
            gauge("gpu.hw_errors", hw_errors)
        if ENABLE_CLOUDWATCH:
            gpu_metric = lambda k, v: cloud_watch.report_metric("System/GPU", k, v, { "GPU": gpu_id, "Host": HOSTNAME })
            gpu_metric("TemperatureCelcius", temp)
            gpu_metric("FanSpeedRPM", fan_speed)
            gpu_metric("FanSpeedPercent", fan_pct)
            cgminer_metric = lambda k, v: cloud_watch.report_metric("App/CGMiner", k, v, { "GPU": gpu_id, "Host": HOSTNAME })
            cgminer_metric("KHashPerSecond", khash_s)
            cgminer_metric("HardwareErrors", hw_errors)


    sleep(REPORT_INTERVAL)

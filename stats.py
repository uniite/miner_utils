from cgminer_api import APIClient
from datetime import datetime
from statsd import statsd
from time import sleep


REPORT_INTERVAL = 10


api = APIClient()
while True:
    try:
        summary = api.summary()
        devs = api.devs()
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
        name = name.replace("=", "").lower()
        gauge = lambda k,v: statsd.gauge(k, v, tags=["device:%s" % name])
        gauge("gpu.temp", int(float(info["Temperature"])))
        gauge("gpu.khash", int(float(info["MHS 5s"]) * 1000))
        gauge("gpu.fan_rpm", int(info["Fan Speed"]))
        gauge("gpu.fan_pct", int(info["Fan Percent"]))
        gauge("gpu.hw_errors", int(info["Hardware Errors"]))

    sleep(REPORT_INTERVAL)

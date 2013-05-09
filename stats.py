from query import APIClient
from statsd import statsd
from time import sleep


api = APIClient()
while True:
    print "Querying API..."
    summary = api.summary()

    # Global stats
    #statsd.gauge("")

    # GPU stats (temperature, KHash/s, etc.)
    devs = api.devs()
    for name,info in devs.iteritems():
        if not "GPU" in name: continue
        name = name.replace("=", "").lower()
        gauge = lambda k,v: statsd.gauge(k, v, tags=["device:%s" % name])
        gauge("gpu.temp", int(float(info["Temperature"])))
        gauge("gpu.khash", int(float(info["MHS 5s"]) * 1000))
        gauge("gpu.fan_rpm", int(info["Fan Speed"]))
        gauge("gpu.fan_pct", int(info["Fan Percent"]))
        #gauge("gpu.hw_errors", int(info["Hardware Errors"]))

    sleep(10)

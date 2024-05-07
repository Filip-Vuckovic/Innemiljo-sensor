from time import sleep
import json
from wlan import connect
import uasyncio
import sensors



def test():
    data = dict(
        bme = dict(temperature=0, humidity=0, pressure=0),
        ens = dict(tvoc=0, eco2=0, rating=''),
        aht = dict(temperature=0, humidity=0),
    )
    loop = uasyncio.get_event_loop()
    loop.create_task(sensors.collect_sensors_data(data, True))
    loop.run_forever()
    #while True:
    #    await uasyncio.sleep_ms(5000)
    #    print(data)


if __name__ == '__main__':
    test()





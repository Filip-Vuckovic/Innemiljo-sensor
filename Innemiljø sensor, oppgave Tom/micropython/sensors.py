import gc
from time import sleep
from machine import Pin, I2C
import uasyncio
from BME280 import BME280
from PiicoDev_ENS160 import PiicoDev_ENS160 # import the device driver
from PiicoDev_Unified import sleep_ms       # a cross-platform sleep function
import aht



i2c = I2C(0, scl=Pin(17), sda=Pin(16))
bme = BME280(i2c=i2c)
ens = PiicoDev_ENS160(bus=0, scl=Pin(17), sda=Pin(16))
aht_sensor = aht.AHT2x(i2c, crc=False)


readings_bme_temperature = []
readings_bme_humidity = []
readings_bme_pressure = []
readings_ens_tvoc = []
readings_ens_eco2 = []
readings_ens_rating = ''
readings_aht_temperature = []
readings_aht_humidity = []

async def read_bme():
    temperature = bme.read_temperature() / 100
    humidity = bme.read_humidity() / 1024
    pressure = bme.read_pressure() / 25600
    return temperature, humidity, pressure


async def read_ens():
    return ens.tvoc, ens.eco2.value, ens.eco2.rating
    
    
async def read_aht():
    if aht_sensor.is_ready:
        temperature = aht_sensor.temperature
        humidity = aht_sensor.humidity  
    return temperature, humidity

def _pop0(l):
    if len(l) >= 60:
        l.pop(0)

def _mid(l):
    return sorted(l)[len(l)//2]
    

async def update_sensors_data(data):
    global readings_bme_temperature
    global readings_bme_humidity
    global readings_bme_pressure
    global readings_ens_tvoc
    global readings_ens_eco2
    global readings_ens_rating    
    global readings_aht_temperature
    global readings_aht_humidity

    temperature, humidity, pressure = await read_bme()
    readings_bme_temperature.append(temperature)
    readings_bme_humidity.append(humidity)
    readings_bme_pressure.append(pressure)
  
    tvoc, eco2, rating = await read_ens()
    readings_ens_tvoc.append(tvoc)
    readings_ens_eco2.append(eco2)
    readings_ens_rating = rating
   
    temperature, humidity = await read_aht()
    readings_aht_temperature.append(temperature)
    readings_aht_humidity.append(humidity)
 
    _pop0(readings_bme_temperature)
    _pop0(readings_bme_humidity)
    _pop0(readings_bme_pressure)

    _pop0(readings_ens_tvoc)
    _pop0(readings_ens_eco2)

    _pop0(readings_aht_temperature)
    _pop0(readings_aht_humidity)
     
    data['bme']['temperature'] = _mid(readings_bme_temperature)
    data['bme']['humidity'] = _mid(readings_bme_humidity)
    data['bme']['pressure'] = _mid(readings_bme_pressure)
    data['ens']['tvoc'] = _mid(readings_ens_tvoc)
    data['ens']['eco2'] = _mid(readings_ens_eco2)
    data['ens']['rating'] = readings_ens_rating
    data['aht']['humidity'] = _mid(readings_aht_humidity)
    data['aht']['temperature'] = _mid(readings_aht_temperature)


async def collect_sensors_data(data, test=False):    
    while True:
        await update_sensors_data(data)
        if test:
            print(data)
    
        await uasyncio.sleep_ms(2000)

def test():
    data = dict(
        bme = dict(temperature=0, humidity=0, pressure=0),
        ens = dict(tvoc=0, eco2=0, rating=''),
        aht = dict(temperature=0, humidity=0),
    )
    loop = uasyncio.get_event_loop()
    loop.create_task(collect_sensors_data(data, True))
    loop.run_forever()

if __name__ == '__main__':
    test()
    
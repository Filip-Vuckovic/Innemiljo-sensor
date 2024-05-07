import time
import json
from wlan import connect
import uasyncio
from nanoweb import Nanoweb
import urequests
from machine import WDT, Pin
import gc

import sensors
from html_functions import naw_write_http_header, render_template
#from leds import blink
import buttons
from thingspeak import thingspeak_publish_data




#Button variabel
button_pin_OUT = Pin(5, Pin.OUT) #black kabel
button_pin_IN = Pin(6, Pin.IN, Pin.PULL_DOWN) #white kabel

button_pin_OUT.value(1)

#RGB LED variabel 
r_rgb = Pin(2, Pin.OUT, Pin.PULL_DOWN)
g_rgb = Pin(1, Pin.OUT, Pin.PULL_DOWN)
b_rgb = Pin(0, Pin.OUT, Pin.PULL_DOWN)

#Defaulter til av
r_rgb.value(1)
g_rgb.value(1)
b_rgb.value(1)



sta_if = connect() # Kobler til trådløst nettverk

naw = Nanoweb() # Lager en instans av Nanoweb

#Sorterer datan den får fra sensoren
data = dict(
    bme = dict(temperature=0, humidity=0, pressure=0),
    ens = dict(tvoc=0, eco2=0, rating=''),
    aht = dict(temperature=0, humidity=0),
    )

inputs = dict(button_1=False)
    
@naw.route("/")
def index(request):
    naw_write_http_header(request)
    html = render_template(
        'index.html',
        temperature_bme=str(data['bme']['temperature']),
        humidity_bme=str(data['bme']['humidity']),
        pressure=str(data['bme']['pressure']),        
        tVOC=str(data['ens']['tvoc']),
        eCO2=str(data['ens']['eco2']),
        temperature_aht=str(data['aht']['temperature']),
        humidity_aht=str(data['aht']['humidity']),
        )
    await request.write(html)


@naw.route("/api/data")
def api_data(request):
    naw_write_http_header(request, content_type='application/json')
    await request.write(json.dumps(data))

async def control_loop():
    while True:
        thingspeak_publish_data(data)#Sender data til thingspeak
        gc.collect()
        await uasyncio.sleep_ms(60*1000)#passer på at datan den sender blir sent hver minutt 
    

async def wdt_loop():#bruker en async loop for å kjøre koden hele tiden. 
    #WDT restarter programmer hvis det blir en feil
    wdt = WDT(timeout=8000)
    while True:
        wdt.feed()
        await uasyncio.sleep_ms(1000)
        
        
#Button input
async def button_loop():#bruker en async loop for å kjøre koden hele tiden. 
    while True: 
        if button_pin_IN.value():#Skjekker om knappen er på eller av
            sensors.collect_sensors_data(data, False) #Henter ny data
            thingspeak_publish_data(data)#Sender data til thingspeak
            gc.collect()#Kaster gammel data man ikke trenger så pico-en tåler programmet
            time.sleep(5)#Setter en limit på 5 sekunder for å ikke sende formye på engang
            
        await uasyncio.sleep_ms(50)


#Kvalitets indikasjon
async def kvalitet_loop():#bruker en async loop for å kjøre koden hele tiden. 
    while True: 
        if data["ens"]["rating"] =='excellent':#Hvis verdien er riktig bytter lyset. Men hvis ikke gr den til neste "if" og finner hvilket lys den skal bytte til
            r_rgb.value(1)
            g_rgb.value(0)
            b_rgb.value(1)
            
        elif data["ens"]["rating"] == 'good':
            r_rgb.value(0)
            g_rgb.value(0)
            b_rgb.value(1)
            
        elif data["ens"]["rating"] == 'fair':
            r_rgb.value(0)
            g_rgb.value(0)
            b_rgb.value(1)
            
        elif data["ens"]["rating"] == 'poor':
            r_rgb.value(0)
            g_rgb.value(1)
            b_rgb.value(1)
            
        elif data["ens"]["rating"] == 'bad':
            r_rgb.value(0)
            g_rgb.value(1)
            b_rgb.value(1)
            
        await uasyncio.sleep_ms(1000)

                     
#loop som får kode til å kjøre flere ganger

loop = uasyncio.get_event_loop()
loop.create_task(sensors.collect_sensors_data(data, False))
loop.create_task(buttons.wait_for_buttons(inputs))
loop.create_task(naw.run())
loop.create_task(control_loop())
loop.create_task(wdt_loop())
loop.create_task(button_loop())
loop.create_task(kvalitet_loop())


loop.run_forever()
    


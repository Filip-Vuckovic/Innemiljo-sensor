from machine import Pin
import uasyncio

LED_PIN_BLUE = 2

led_blue = Pin(2, Pin.OUT)


async def blink():    
    while True:
        v = not led_blue.value()
        led_blue.value(v)
        await uasyncio.sleep_ms(1000)


def test(): 
    loop = uasyncio.get_event_loop()
    loop.create_task(blink())
    loop.run_forever()


if __name__ == '__main__':
    test()
    
from machine import Pin
import uasyncio

BUTTON_1_PIN = 14

button_1 = Pin(BUTTON_1_PIN, Pin.IN, Pin.PULL_DOWN)

async def wait_for_buttons(inputs):
    counter = 0
    while True:
        counter += 1
        #if (counter % 10) == 0: # Printer verdien hvert 10. sekund pga 100 ms pause lenger ned
        #    print(counter, 'Button value', button_1.value())
        
        if button_1.value(): # Hvis større en trigger verdi
            inputs['button_1'] = True
            #print(counter, 'Button value', button_1.value())
            await uasyncio.sleep_ms(2000) # Venter 2  sek for å bounce
        await uasyncio.sleep_ms(100)

def test():
    inputs = dict(button_1=False)
    loop = uasyncio.get_event_loop()
    loop.create_task(wait_for_buttons(inputs))
    loop.run_forever()

if __name__ == '__main__':
    test()
import lcddriver
from time import *

lcd = lcddriver.lcd()
print ("Iniciando...")

lcd.lcd_display_string("linea 1", 1)
sleep(6)
lcd.lcd_display_string("linea 2", 2)
lcd.lcd_display_string("linea 3", 3)
lcd.lcd_display_string("conectarme x I2C", 4)

sleep(6)
print ("Terminando...")

#for i in range(1,100):
#    lcd.lcd_display_string(str(i), 3, 1)
#    sleep (1)

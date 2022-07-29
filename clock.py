from lcd_display import lcd
from subprocess import * 
from time import sleep, strftime
from datetime import datetime

from pynput import keyboard as kb

lcd = lcd()

cmd = "ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1"
temp_cpu = '/usr/bin/vcgencmd measure_temp' # mide la temperatura de la CPU

count = 0
bandera = 0
cadena = ""

def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output

def portada():
    lcd.display_string('Proy. Capstone Eq.11',1 )
    lcd.display_string('Sergio Magdaleno    ',2)
    lcd.display_string('Bogart Yail Marquez ',3 )
    lcd.display_string('Antonio Landa       ',4 )

def pulsa(tecla):
	print("Se ha pulsado la tecla ESC " + str(tecla))
	cadena=str(tecla)
	salir= ' Key.esc '
	print("  valor de la cadena :",cadena,":")
	
	
lcd.clear()
portada()
sleep(10)

while ((1) and (bandera==0)):
    
      
    #with kb.Listener(pulsa) as escuchador:
   #     escuchador.join()
    
   # if (cadena==salir):
   #     i=0
   #     print ("Se ha pulsado la tecla ESC --->Salir ")

    if (bandera==0):    
        lcd.clear()
        ipaddr = run_cmd(cmd)
        temp = run_cmd(temp_cpu)

        #lcd.display_string(datetime.now().strftime('%b %d  %H:%M:%S'),1)
    
        lcd.display_string('Linea 1             ',1 )
        lcd.display_string('Linea 2             ',2 )
        lcd.display_string('Linea 3             ',3 )
        lcd.display_string('Linea 4             ',4 )
        print ("Fin...")
  
    
        #lcd.display_string('IP %s' % ( ipaddr ),2 )
        #lcd.display_string('%s' % ( temp ),3 )
   
        sleep(2)
    
   
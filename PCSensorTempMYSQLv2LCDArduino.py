import mariadb 
import sys
import serial
import time
import datetime
from datetime import date
from time import sleep, strftime
from datetime import datetime


import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) 

GPIO.setwarnings(False)

from lcd_display import lcd
from subprocess import *

lcd = lcd()

                
GPIO.setup(12,GPIO.OUT) #Pin que corresponde al relay 1, ventilador
GPIO.setup(18,GPIO.OUT) #Pin que corresponde al led rojo del relay 1, ventilador
GPIO.setup(21,GPIO.OUT) #Pin que corresponde al relay 2, filtro
GPIO.setup(20,GPIO.OUT) #Pin que corresponde al led verde del relay 2, filtro
GPIO.setup(26, GPIO.IN) #Pin de entrada del MQ135

from subprocess import *

ser = serial.Serial('/dev/ttyACM0',9600)
ser.flushInput()

# Configuracion del puerto GPIO del sensor DHT11, ell cual esta conectado  (GPIO 23)
pin = 23
pinmq135 = 26


#Variables Globales

#datetime.datetime.now()
temperatura= 0
humedad=0
fecha=date.today()
hora=datetime.now().time()

pin_relay1 = 12 #pin del relay 1, ventilador
pin_led_relay1 = 18 #pin del led relay 1, ventilador
pin_relay2 = 21 #pin del relay 2, filtro
pin_led_relay2 = 20 #pin del led relay 2, filtro


GPIO.output(pin_relay1,GPIO.LOW)
GPIO.output(pin_led_relay1,GPIO.LOW)
GPIO.output(pin_relay2,GPIO.LOW)
GPIO.output(pin_led_relay2,GPIO.LOW)

bandera = True
tempmax=28.6
totalhoraslab=50000

def portada():
    lcd.display_string('Proy. Capstone Eq.11',1 )
    lcd.display_string('Sergio Magdaleno    ',2)
    lcd.display_string('Bogart Yail Marquez ',3 )
    lcd.display_string('Antonio Landa       ',4 )

def sensartemp():
    pasadas=0
    print('Dentro del ciclo del sensor...')
    # Ciclo principal infinito
    banderaciclo=0
    contador=0
     
    while banderaciclo==0:
        print('Dentro de grabar temperaturas...')
        pasadas=pasadas+1
        print('Contador de pasadas del ciclo :',pasadas)
        
        def run_cmd(cmd):
            p = Popen(cmd, shell=True, stdout=PIPE)
            output = p.communicate()[0]
            return output
      
        #import mysql.connector
        #import mysql.connector as mariadb
        #Conexion con el servidor MySQL Server
        print ('Antes de conectar mariadb...')
        try:
            mariadb_conexion = mariadb.connect(host='localhost',user='padmin',passwd='usuariopc@1',db='proyecto')
        except mariadb.Error as e:
            print(f"Error de conexion con la plataforma de MariaDB {e}")
            sys.exit(1)
        print('...Logro conexion con mariadb')
        cursor = mariadb_conexion.cursor()
                
        fecha=date.today()
        hora=datetime.now().time()
        
        try:
            lineBytes = ser.readline()
            line = lineBytes.decode('utf=8').strip()            
            continuarmq135=1
        except KeyBoardInterrupt:
            continuarmq135=0
            break
        
        if continuarmq135==1:
            if (line!='DHTxx') and (line!='DHTxx test!'):
                #Dentro de line!=DHTxx (Para convertir a float la temperatura
                cadhumedad=line[0:5] #copiar de la cadena line el mesaje humedad y su valor
                ct=cadhumedad
                ch=ct
                #Convertir la temperatura recibida a float
                b  = float(ct[0])
                b2 = float(ct[1])
                #ct[2] es el punto decimal
                b3 = float(ct[3])
                b4 = float(ct[4])                                            
                humedad=(b*10)+(b2)+(b3*0.1)+(b4*0.01)
                
                  
                #Convertir la temperatura recibida a float
                cadtemperatura=line[5:10] #copist de la cadena line la temperatura
                ct=cadtemperatura
                b  = float(ct[0])
                b2 = float(ct[1])
                #ct[2] es el punto decimal
                b3 = float(ct[3])
                b4 = float(ct[4])                                            
                temperatura=(b*10)+(b2)+(b3*0.1)+(b4*0.01)
                
                print ('Fecha : ',fecha)
                print ('Valor de la temperatura:',temperatura,'°C ')
                print ('Valor de la humedad:',humedad,'%')                
                
                lcd.clear()
                ct=ct+"°C"
                ch=ch+"%"
                lcd.display_string('  Temperatura',1 ) 
                lcd.display_string(' '+ct,2 )
                lcd.display_string('  Humedad',3 ) 
                lcd.display_string(' '+ch,4 )               
                sleep(3)

    		# Imprime en la consola las variables temperatura y humedad con un decimal
                if temperatura>tempmax:
                    print ("VENTILADOR Encendido...")
                    GPIO.output(pin_relay1,GPIO.HIGH) # enciende el relay 1 del ventilador
                    GPIO.output(pin_led_relay1,GPIO.HIGH) #encender led rojo del ventilador
                else:
                    print("VENTILADOR Apagado...")
                    GPIO.output(pin_relay1,GPIO.LOW)
                    GPIO.output(pin_led_relay1,GPIO.LOW) 
            
                sqlSelect = "INSERT INTO sensor (temperatura, humedad) VALUES (%s,%s)"
                val=(temperatura, humedad)        
                cursor.execute(sqlSelect,val)
            
                #Lectura del MQ135
                #Buena calidad del ambiente = 0   True
                #Mala calidad del ambiente =1   False
                #Verifica el pin 26, si es True o False. Si se cumple para este if es True
                if GPIO.input(pinmq135):                    
                    calidadaire=0.0
                    print ('Se esta leyendo TRUE en el pin 26. BUENA calidad del aire, filtro APAGADO... ');
                    GPIO.output(pin_relay2,GPIO.LOW)
                    GPIO.output(pin_led_relay2,GPIO.LOW)
                             
                    sqlSelect2 = "INSERT INTO dbmq135 (calidad) VALUES (0)"
                    #print ('sql2', sqlSelect2)
                    cursor.execute(sqlSelect2)
                else:
                    calidadaire=1.0
                    print ('Se esta leyendo FALSE en el pin 26. MALA calidad del aire, filtro ENCENDIDO... ');
                    GPIO.output(pin_relay2,GPIO.HIGH) # enciende el relay 2 del filtro
                    GPIO.output(pin_led_relay2,GPIO.HIGH) #encender led verde del filtro
                
                    sqlSelect3 = "INSERT INTO dbmq135 (calidad) VALUES (1)"
                    #print ('sql3', sqlSelect3)
                    cursor.execute(sqlSelect3) 
                    time.sleep(2)
                   
                mariadb_conexion.commit() 

        # Se ejecuta en caso de que falle alguna instruccion dentro del try
        #except RuntimeError as error:
            # Imprime en pantalla el error
          #  print(error.args[0])

        # Duerme 2 segundos
        time.sleep(2)
        contador=contador+1
        if contador == totalhoraslab:
            banderaciclo=1
    mariadb_conexion.close()    
     
while bandera:
    portada()
    sensartemp()     
    print("Termine de grabar")
    bandera=False
GPIO.cleanup() 
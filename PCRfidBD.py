import mariadb 
import sys


#Envioi de correos por gmail
import smtplib
from email.mime.text import MIMEText

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

import max30102
import hrcalc

from lcd_display import lcd
from subprocess import *

import time
from time import sleep, strftime
from datetime import datetime

lcd = lcd()

m = max30102.MAX30102()
repetirlectura=1
terminar=0
centraron=0.0
cenviados=0.0
ccentraron=0.0
ccenviados=0.0


#Oxigenacion minima a este valor, para envio de correo a oficina para revision
Oxigenacionminima=98.0
nombrealumno=''


def pmax30102(nombrealumno):   #Lectura para la oxigenacion
    global ccentraron
    global ccenviados
    nombrerecibido=nombrealumno
    print ("Lectura del MAX30102...",nombrerecibido)
       
    m = max30102.MAX30102()
    repetirlectura=1
    terminar=0
    
    try:
        mariadb_conexion = mariadb.connect(host='localhost',user='padmin',passwd='usuariopc@1',db='proyecto')
    except mariadb.Error as e:
        print(f"Error de conexion con la plataforma de MariaDB {e}")
        sys.exit(1)
    cursor = mariadb_conexion.cursor()
    
    while terminar==0:   #Logro hacer una lectura correcta, por lo tanto terminar lectura, de lo contrario ciclarse para leer
        while repetirlectura==1: #Validacion de lectura con valores correctos
            print ("Coloque el dedo indice en el sensor MAX30102 : ")
            red, ir = m.read_sequential()
            print(hrcalc.calc_hr_and_spo2(ir, red))
            #print("valores:")
            #print(hrcalc.calc_hr_and_spo2(ir,red)[0], hrcalc.calc_hr_and_spo2(ir,red)[1])
            #print(hrcalc.calc_hr_and_spo2(ir,red)[2], hrcalc.calc_hr_and_spo2(ir,red)[3]) 
            time.sleep(1)
            #Verificar que la lectura tenga valores validos
            if hrcalc.calc_hr_and_spo2(ir,red)[1] == False or hrcalc.calc_hr_and_spo2(ir,red)[3]==False:
                repetirlectura=1
            else:
                repetirlectura=0
            #Requiere atencion medica, enviar correo a la oficina de proteccion de la institucion
            
            if repetirlectura ==0:
                if hrcalc.calc_hr_and_spo2(ir,red)[2] < Oxigenacionminima:
                    print ("Requiere atencion medica, no puede entrar al laboratorio")
                    print ("Enviar correo a la oficina de proteccion de la institucion para seguimiento ")
                    repetirlectura=0
                
                    #Enviar_correo a la oficina correspoindiente (de proteccion)
                    #Informacion para el envio de correos
                    correo_origen = 'sergio.magdaleno@uabc.edu.mx' #correo de origen
                    contrasena = 'magdapalmarcos3'
                    correo_destino = 'JSMPCorreoIoT@gmail.com' # correo de destino
                    #Función para el envio de correo electrónico
                    stroxigeno=str(hrcalc.calc_hr_and_spo2(ir,red)[2])
                    msg = MIMEText(f"La oxigenacion requiere atencion,su oxigenacion es de : ")
                    msg['Subject'] = 'Monitoreo de Oxigenacion para :' + nombrerecibido + ' ' + stroxigeno
                    msg['From'] = correo_origen
                    msg['To'] = correo_destino
                    server = smtplib.SMTP('smtp.gmail.com',587)
                    server.starttls()
                    server.login(correo_origen,contrasena)
                    server.sendmail(correo_origen,correo_destino,msg.as_string())
                    print("Su Email ha sido enviado...")
                    server.quit()
                    #registrar que un alumno mas entro al laboratorio
                    # se resgistra en la tabla cantidad (entraron) de la base de datos proyecto
                    print('Antes de guardar en tabla cantidad enviados')
                    print ('VALOR DE ccentraron ',ccentraron)
                    ccentraron = ccentraron
                    ccenviados = ccenviados + 1.0
                    print ('Cantidad hasta ahora de enviados = ',ccenviados)
                    sqlSelect2 = "INSERT INTO cantidad (entraron, enviados) VALUES (%s,%s)"
                    val=(ccentraron,ccenviados)
                    cursor.execute(sqlSelect2,val)
                    mariadb_conexion.commit()                
                    time.sleep(1)
                else:
                    print ("Puede entrar al laboratorio")
                    print('Antes de guardar en tabla cantidad entraron')
                    #registrar que un alumno mas no entro al laboratorio porque su oxigenacion es baja
                    #se envio un correo a la oficina de control (proteccion) para seguimiento
                    # se resgistra en la tabla cantidad  (enviados) de la base de datos proyecto
                    print ('VALOR DE ccenviados ',ccenviados)
                    ccentraron = ccentraron + 1.0
                    ccenviados = ccenviados
                    print ('Cantidad que entarron al laboratorio hasta ahora = ',ccentraron)
                    sqlSelect3 = "INSERT INTO cantidad (entraron,enviados) VALUES (%s,%s)"
                    val=(ccentraron,ccenviados) 
                    cursor.execute(sqlSelect3,val)
                    mariadb_conexion.commit() 
                    time.sleep(1)
                    
               
       
        print ("Lectura CORRECTA hecha del indice... ")
        terminar = 1


def prfid():
    def run_cmd(cmd):
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.communicate()[0]
        return output

    def portada():
        lcd.display_string('Proy. Capstone Eq.11',1 )
        lcd.display_string('Sergio Magdaleno    ',2)
        lcd.display_string('Bogart Yail Marquez ',3 )
        lcd.display_string('Antonio Landa       ',4 )

    #import mysql.connector
    #import mysql.connector as mariadb
    #Conexion con el servidor MySQL Server

    try:
        mariadb_conexion = mariadb.connect(host='localhost',user='padmin',passwd='usuariopc@1',db='proyecto')
    except mariadb.Error as e:
        print(f"Error de conexion con la plataforma de MariaDB {e}")
        sys.exit(1)
    
    cursor = mariadb_conexion.cursor()

    print ('Coloque su tarjeta de identificacion y ESPERE que aparezca su numero de control')
    reader = SimpleMFRC522()
    try:
        id, text = reader.read()
        print(id)
        print(text)
    finally:
        GPIO.cleanup()
        cadnocontrol = str(id)
        print("nocontrol =",cadnocontrol)
        sqlSelect = "SELECT nombre from alumno where nocontrol={}".format(cadnocontrol)  
        cursor.execute(sqlSelect)
        #resultadoSQL = cursor.fetchall()
        resultadoSQL = cursor.fetchall()
    
    lcd.clear()
    lcd.display_string('Coloque CREDENCIAL',1)
    lcd.display_string('en el lector',2)
    sleep(2)
    portada()
    sleep(2)


    #Lectura de la tarjeta
    reader = SimpleMFRC522()
    #Resultados de la busqueda del SELECT
    #print ("resulados de la busqueda : ",resultadoSQL)    
    if len(resultadoSQL)==0: #No encontro el alumno
        print ('NO existe ses alumno...')
        lcd.clear()
        lcd.display_string('  No existe ese',1 ) 
        lcd.display_string('      ALUMNO   ',2 )
        sleep(3)
    else:   #Si encontro al alumno
        cadenanombre = str(resultadoSQL[0])
        for row in resultadoSQL:
            nc = row[0] #Nombre del alumno que encontro en el SELECT
            nccadena=str(nc)
            nombrealumno=nccadena[0:40]
            print ('NOMBRE DEL ALUMNO ',nombrealumno)
            lcd.clear()
            lcd.display_string('Bienvenido...      ',2)
            Nombre20 = nccadena[0:20]
            lcd.display_string(Nombre20,3 )
        sleep(2)
        pmax30102(nombrealumno) #Lectura del MAX30102 para la oxigenacion
        
    mariadb_conexion.close()
    return ccentraron,ccenviados

def inicializa():
    repetirlectura=1
    terminar=0
    ccentraron=0.0
    ccenviados=0.0
while True:
    inicializa()
    prfid()
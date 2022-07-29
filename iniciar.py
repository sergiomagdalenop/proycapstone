import max30102
import hrcalc
import time
m = max30102.MAX30102()
repetirlectura=1
terminar=0

# 100 samples are read and used for HR/SpO2 calculation in a single loop
while terminar==0:
    
    while repetirlectura==1:
        print ("Coloque el el dedo indice en el sensor MAX30102 : ")
        red, ir = m.read_sequential()
        print(hrcalc.calc_hr_and_spo2(ir, red))
        #print("valores:")
        #print(hrcalc.calc_hr_and_spo2(ir,red)[0], hrcalc.calc_hr_and_spo2(ir,red)[1])
        #print(hrcalc.calc_hr_and_spo2(ir,red)[2], hrcalc.calc_hr_and_spo2(ir,red)[3])
      
      
        time.sleep(1)
        if hrcalc.calc_hr_and_spo2(ir,red)[1] == False and hrcalc.calc_hr_and_spo2(ir,red)[3]==False:
            repetirlectura=1
        else:
            repetirlectura=0
            #Requiere atencion medica
            if hrcalc.calc_hr_and_spo2(ir,red)[2] < 90:
                print ("Requiere atencion medica, no puede entrar al laboratorio")
                print ("Enviar correo a la oficina de proteccion de la institucion para seguimiento ")
                repetirlectura=0
            else:
                print ("Puede entrar al laboraorio")
       
    print ("Lectura hecha del indice ")
    terminar = 1
    
    
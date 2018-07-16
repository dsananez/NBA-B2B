import pandas as pd
import numpy as np


def fact_24(df):
    fact_oferta = {}
    ofertas = pd.read_csv('listado_campanas.txt', sep=",")
    
    for i in range(0,len(ofertas)):
        fact_esp = ofertas['fact_esp'][i]
        fact = np.array([], dtype=np.float).reshape(0,24)
        
        if ofertas['tipo_oferta'][i] == 'cater':
            
            if ofertas['tipo_fact'][i] == 'delta':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(df['fact'][k] + fact_esp, 12)) + list(np.repeat(df['fact'][k], 12)) 
                    fact = np.vstack([fact, fact_24])
            elif ofertas['tipo_fact'][i] == 'aumento_porct':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(df['fact'][k]*(1+fact_esp), 12)) + list(np.repeat(df['fact'][k], 12)) 
                    fact = np.vstack([fact, fact_24])
            elif ofertas['tipo_fact'][i] == 'fijo':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(fact_esp, 12)) + list(np.repeat(df['fact'][k], 12)) 
                    fact = np.vstack([fact, fact_24])
        
        elif ofertas['tipo_oferta'][i] == 'bono':
            
            duracion = int(ofertas['id_oferta'][i].split('_')[2])
            
            if ofertas['tipo_fact'][i] == 'delta':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(df['fact'][k] + fact_esp, duracion)) + list(np.repeat(df['fact'][k], 24-duracion)) 
                    fact = np.vstack([fact, fact_24])
            elif ofertas['tipo_fact'][i] == 'aumento_porct':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(df['fact'][k]*(1+fact_esp), duracion)) + list(np.repeat(df['fact'][k], 24-duracion)) 
                    fact = np.vstack([fact, fact_24])
            elif ofertas['tipo_fact'][i] == 'fijo':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(fact_esp, duracion)) + list(np.repeat(df['fact'][k], 24-duracion)) 
                    fact = np.vstack([fact, fact_24])
                    
        elif ofertas['tipo_oferta'][i] == 'cross_sell':
    
            if ofertas['tipo_fact'][i] == 'delta':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(df['fact'][k] + fact_esp, 24)) 
                    fact = np.vstack([fact, fact_24])
            elif ofertas['tipo_fact'][i] == 'aumento_porct':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(df['fact'][k]*(1+fact_esp), 24)) 
                    fact = np.vstack([fact, fact_24])
            elif ofertas['tipo_fact'][i] == 'fijo':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(fact_esp, 24))
                    fact = np.vstack([fact, fact_24])
       
        elif ofertas['tipo_oferta'][i] == 'cross_sell':
    
            if ofertas['tipo_fact'][i] == 'delta':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(df['fact'][k] + fact_esp, 24)) 
                    fact = np.vstack([fact, fact_24])
            elif ofertas['tipo_fact'][i] == 'aumento_porct':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(df['fact'][k]*(1+fact_esp), 24)) 
                    fact = np.vstack([fact, fact_24])
            elif ofertas['tipo_fact'][i] == 'fijo':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(fact_esp, 24))
                    fact = np.vstack([fact, fact_24])
        
        elif ofertas['tipo_oferta'][i] == 'up_sell':
    
            if ofertas['tipo_fact'][i] == 'delta':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(df['fact'][k] + fact_esp, 24)) 
                    fact = np.vstack([fact, fact_24])
            elif ofertas['tipo_fact'][i] == 'aumento_porct':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(df['fact'][k]*(1+fact_esp), 24)) 
                    fact = np.vstack([fact, fact_24])
            elif ofertas['tipo_fact'][i] == 'fijo':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(fact_esp, 24))
                    fact = np.vstack([fact, fact_24])
                    
        elif ofertas['tipo_oferta'][i] == 'descuento':
            
            if ofertas['id_oferta'][i].split('_')[2] == 'indef':
                duracion = 24
            else:
                duracion = int(ofertas['id_oferta'][i].split('_')[2])
            
            if ofertas['tipo_fact'][i] == 'delta':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(df['fact'][k] + fact_esp, duracion)) + list(np.repeat(df['fact'][k], 24-duracion)) 
                    fact = np.vstack([fact, fact_24])
            elif ofertas['tipo_fact'][i] == 'aumento_porct':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(df['fact'][k]*(1+fact_esp), duracion)) + list(np.repeat(df['fact'][k], 24-duracion)) 
                    fact = np.vstack([fact, fact_24])
            elif ofertas['tipo_fact'][i] == 'fijo':
                for k in range(0,len(df)):
                    fact_24 = list(np.repeat(fact_esp, duracion)) + list(np.repeat(df['fact'][k], 24-duracion)) 
                    fact = np.vstack([fact, fact_24])                    
        
                    
        fact_oferta[ofertas['id_oferta'][i]] = pd.concat([df['msisdn_id'], pd.DataFrame(data=fact)], axis=1)
        
    return fact_oferta

d = {'msisdn_id': ['1','2','3','4','5','6','7','8','9','10','11','12'],
     'fact': [220,250.3,230,500,420,125,600,623,121,597,875,210]
    }

data = pd.DataFrame(data=d)
fact_24(data)
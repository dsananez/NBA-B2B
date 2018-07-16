# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 16:10:33 2018

@author: gchiesap
"""

import pandas as pd
import numpy as np
import random 
import source as fp

class ofertas():
    def __init__(self, name, acp, tipo_oferta, df, costos, tasa):
        self.oferta = name
        self.tipo = tipo_oferta
        self.aceptacion = acp
        self.cliente = df
        self.costos = costos
        self.tasa_interes = tasa
	
class cliente():
	def __init__(self,cuit,razon_social,df):
		self.cliente = df
		self.cuit = cuit
		self.rs = razon_social

def calculo_cltv(dataOferta, dataSinOferta):
	
##Calculo del customer lifetime value
	
	t1 = 1/(dataSinOferta['prob_churn']).mean()
	t2 = 1/min(dataSinOferta['prob_churn'].mean(), dataOferta.cliente['prob_churn'].mean())
	

	ltv_con = (dataOferta.aceptacion * ((dataOferta.cliente['facturacion']-dataOferta.costos).mean())*t2)+((1-dataOferta.aceptacion)* ((dataSinOferta['facturacion']-dataOferta.costos).mean())*t1)
        
	ltv_sin = (dataSinOferta['facturacion'].mean())*t1
	
	return ltv_con - ltv_sin
	

def calculo_van_diff(dataOferta,dataSinOferta):

    ##Calculo del valor actual neto con oferta    
    van_con = 0    
    for i in range(0,round(len(dataOferta.cliente['facturacion']))):
        van_con = van_con + (dataOferta.cliente['facturacion'].values[i]-dataOferta.costos[i])*((1-dataOferta.cliente['prob_churn'].values[i]))*(pow((1+dataOferta.tasa_interes.mean()),i))

    ##valor actual neto sin oferta
    van_sin = 0 
    for i in range(0,round(len(dataOferta.cliente['facturacion']))):
        van_sin = van_sin + (dataSinOferta['facturacion'].values[i])*((1-dataSinOferta['prob_churn'].values[i]))*(pow((1+dataOferta.tasa_interes.mean()),i))    

    #valor actual neto con oferta teniendo en cuenta la aceptacion de la oferta
    van_oferta = (dataOferta.aceptacion)*van_con + (1-dataOferta.aceptacion)*(van_sin-dataOferta.costos[0])

    #Score por oferta en un determinado cliente
   

    return van_oferta - van_sin	

												  
	

def mejor_oferta(fact_oferta,churn_oferta,k,costos_of,aceptacion,tasa_interes,cliente,func_obj):

    dataOferta = {}
    ##Ajusto variables de entrada para el calculo de los valores actuales cuando se hace una oferta
    for i in range(0,len(fact_oferta)):


        nombre = list(fact_oferta.keys())[i]
        tipo = list(fact_oferta.keys())[i].split('_')[0]
        acep = aceptacion[i]
        df = pd.DataFrame(columns=['facturacion','prob_churn'])
        df['facturacion'] = pd.Series(list(fact_oferta[nombre].loc[k,:])[1:])
        df['prob_churn'] = pd.Series(list(churn_oferta[nombre].loc[k,:])[1:])
        tasa_interes = pd.Series(tasa_interes)
        costos = np.zeros(24)
        costos[0] = costos_of[i]
    
        dataOferta[i] = ofertas(nombre,acep,tipo,df,costos,tasa_interes)

    dataSinOferta = pd.DataFrame()

    dataSinOferta['facturacion'] = cliente.cliente['facturacion']
    dataSinOferta['prob_churn'] = cliente.cliente['prob_churn']
    


    ##Calculo la diferencia entre valores actuales netos con y sin oferta
    scores = pd.Series()

    for i in range(0,len(dataOferta)):
        if(func_obj == 'van'):
            scores[dataOferta[i].oferta] = calculo_van_diff(dataOferta[i],dataSinOferta)
        elif(func_obj == 'ltv'):
            scores[dataOferta[i].oferta] = calculo_cltv(dataOferta[i],dataSinOferta)

    ##Ordeno de mayor a menor y expongo las dos principales ofertas y sus scores.
    ordenados = scores.sort_values(ascending=False)

    print('Oferta principal: '+ordenados.index.values[0]+' con un score de '+str((ordenados.values[0])))
    print('Oferta secundaria: '+ordenados.index.values[1]+' con un score de '+str((ordenados.values[1])))
    print('-------------')

    #devuelvo los scores ordenados para cada oferta
    return ordenados


if __name__ == "__main__":
		
    #BANCO DE PRUEBAS
    
    ##FACTURACION CLIENTES NORMAL
    	
    d = {'msisdn_id': ['1','2','3','4','5','6','7','8','9','10','11','12'],
    'fact': [220,250.3,230,500,420,125,600,623,121,597,875,210],
    'churn_calibrated': [0.1,0.02,0.05,0.06,0.02,0.02,0.04,0.09,0.02,0.01,0.03,0.07]}
    
    data = pd.DataFrame(data=d)
    
    clientes = {}
    df = pd.DataFrame()
    
    ##Datos del cliente
    for i in range(0,len(data['msisdn_id'])):
        cuit = data['msisdn_id'].values[i]
        rs = 'empresa_'+data['msisdn_id'].values[i]
        df['facturacion'] = pd.Series(data['fact'].values[i]*np.ones(24))
        df['prob_churn'] = pd.Series(data['churn_calibrated'].values[i]*np.ones(24))
    
        clientes[i] = cliente(cuit,rs,df)
	
    #FACTURACION CUANDO SE APLICA LA OFERTA
    fact_oferta = fp.fact_24(data)
    	
    ##REEMPLAZAR POR EL CHURN CON OFERTA
    churn_oferta = fp.churn_24(data)
    	
    for i in range(0,len(churn_oferta)):
    	nombre = list(churn_oferta.keys())[i]
    	churn_oferta[nombre][churn_oferta[nombre].columns[1:]] = (churn_oferta[nombre][churn_oferta[nombre].columns[1:]]/1000)*(random.random())
    	
    of = pd.read_csv('listado_campanas.txt', sep=",")
    
    ##Aceptacion Ofertas
    aceptacion_in = list(of['aceptacion_in'])
    aceptacion_out = list(of['aceptacion_out'])
    
    ##Costos
    
    costos_in = list(fp.costo_total(of)['cost_campana_in'])
    costos_out = list(fp.costo_total(of)['cost_campana_out'])
    
    ##Tasa Interes
    tasa_interes = list(0.02*np.ones(24))

    ##Funcion objetivo ('van' o 'ltv')
    func_obj = 'van'

    NBA_in = pd.DataFrame()
    NBA_out = pd.DataFrame()

    for i in range(0,len(clientes)):
        print('NBA para la '+clientes[i].rs+' canal IN')
        NBA_in[clientes[i].rs] = mejor_oferta(fact_oferta,churn_oferta,i,costos_in,aceptacion_in,tasa_interes,clientes[i],func_obj)
        print('NBA para la '+clientes[i].rs+' canal OUT')
        NBA_out[clientes[i].rs] = mejor_oferta(fact_oferta,churn_oferta,i,costos_out,aceptacion_out,tasa_interes,clientes[i],func_obj)
    	
    print(NBA_in)
    print(NBA_out)
                            	
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 16:10:33 2018

@author: gchiesap
"""

import pandas as pd
import numpy as np

def calculo_van_diff(dataOferta,dataSinOferta, p_acpt_oferta):

    ##Calculo del valor actual neto con oferta    
    van_con = 0    
    for i in range(0,11):
        van_con = van_con + (dataOferta['facturacion'].values[i]-dataOferta['costos'].values[i])*((1-dataOferta['prob_churn'].values[i]))*(pow((1+dataOferta['tasa_interes'].values[i]),i))

    ##valor actual neto sin oferta
    van_sin = 0 
    for i in range(0,11):
        van_sin = van_sin + (dataSinOferta['facturacion'].values[i])*((1-dataSinOferta['prob_churn'].values[i]))*(pow((1+dataSinOferta['tasa_interes'].values[i]),i))    

    #valor actual neto con oferta teniendo en cuenta la aceptacion de la oferta
    van_oferta = p_acpt_oferta*van_con + (1-p_acpt_oferta)*(van_sin-dataOferta['costos'].values[0])

    #Score por oferta en un determinado cliente
    score = van_oferta - van_sin

    return score

def mejor_oferta(ofertas,aceptacion,tasa_interes,cliente):

    dataOferta = {}

    ##Ajusto variables de entrada para el calculo de los valores actuales cuando se hace una oferta
    for i in range(0,len(ofertas)):

        df = pd.DataFrame(columns=['facturacion','prob_churn','tasa_interes','costos'])
        df['facturacion'] = (1+ofertas[i]['delta_fact'])*cliente['facturacion']
        df['prob_churn'] = (1+ofertas[i]['delta_churn'])*cliente['prob_churn']
        df['tasa_interes'] = pd.Series(tasa_interes)
        df['costos'] = ofertas[i]['costo']
        dataOferta[i] = df

    dataSinOferta = pd.DataFrame()

    dataSinOferta['costos'] = 0
    dataSinOferta['facturacion'] = cliente['facturacion']
    dataSinOferta['tasa_interes'] = pd.Series(tasa_interes)
    dataSinOferta['prob_churn'] = cliente['prob_churn']


    ##Calculo la diferencia entre valores actuales netos con y sin oferta
    scores = pd.Series()

    for i in range(0,len(dataOferta)):
        scores['Oferta_'+str(i)] = calculo_van_diff(dataOferta[i],dataSinOferta,aceptacion[i])

    ##Ordeno de mayor a menor y expongo las dos principales ofertas y sus scores.
    ordenados = scores.sort_values(ascending=False)

    print('Oferta principal: '+ordenados.index.values[0]+' con un score de '+str((ordenados.values[0])))
    print('Oferta secundaria: '+ordenados.index.values[1]+' con un score de '+str((ordenados.values[1])))
    print('-------------')

    #devuelvo los scores ordenados para cada oferta
    return ordenados
	

if __name__ == "__main__":
		
    #BANCO DE PRUEBAS
    
    ###Ofertas
    ofertas = {}
    
    ofertas[0] = pd.read_excel('ejemploOfertas.xlsx',sheet_name='oferta1')
    ofertas[1] = pd.read_excel('ejemploOfertas.xlsx',sheet_name='oferta2')
    ofertas[2] = pd.read_excel('ejemploOfertas.xlsx',sheet_name='oferta3')
    
    ##Aceptacion Ofertas
    acp = pd.read_excel('ejemploOfertas.xlsx',sheet_name='aceptacion')
    aceptacion = list(acp['aceptacion'])
    
    ##Clientes
    clientes = {}
    
    clientes[0] = pd.read_excel('ejemploClientes.xlsx',sheet_name='cliente1')
    clientes[1] = pd.read_excel('ejemploClientes.xlsx',sheet_name='cliente2')
    clientes[2] = pd.read_excel('ejemploClientes.xlsx',sheet_name='cliente3')
    
    ##Tasa Interes
    tasa_interes = list(0.02*np.ones(12))
    	
    
    NBA = pd.DataFrame()
    
    for i in range(0,len(clientes)):
        NBA['cliente_'+str(i)] = mejor_oferta(ofertas,aceptacion,tasa_interes,clientes[i])
    	
	
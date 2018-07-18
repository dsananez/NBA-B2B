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
    def __init__(self, name, acp, tipo_oferta, df, costos_sac,costos_camp, tasa, contactabilidad):
        self.oferta = name
        self.tipo = tipo_oferta
        self.aceptacion = acp
        self.cliente = df
        self.costos_sac = costos_sac
        self.costos_camp = costos_camp
        self.tasa_interes = tasa
        self.contactabilidad = contactabilidad

class cliente():
	def __init__(self,ani,cuit,razon_social,df,contactabilidad,upsell,downsell,cater,cross):
		self.cliente = df
		self.ani = ani
		self.cuit = cuit
		self.rs = razon_social
		self.prob_upsell = upsell
		self.prob_downsell = downsell
		self.prob_cater = cater
		self.prob_digitales = cross

class costos_class():
	def __init__(self,costos_sac_1,costos_campania_1):
		self.costos_sac = list(costos_sac_1)
		self.costos_campania = list(costos_campania_1)


def calculo_cltv(dataOferta, dataSinOferta):

##Calculo del customer lifetime value

	t1 = 1/(dataSinOferta['prob_churn']).mean()
	t2 = 1/dataOferta.cliente['prob_churn'].mean()


	ltv_con = ((dataOferta.aceptacion *dataOferta.contactabilidad* ((dataOferta.cliente['facturacion']-dataSinOferta['costos'].values[i]-dataOferta.costos_sac-dataOferta.costos_camp).mean())*t2)+
    ((1-dataOferta.aceptacion)*((dataSinOferta['facturacion']-dataSinOferta['costos']-dataOferta.costos_camp).mean())*t1))


	ltv_sin = ((dataSinOferta['facturacion']-dataSinOferta['costos']).mean())*t1

	return ltv_con - ltv_sin


def calculo_van_diff(dataOferta,dataSinOferta):

    ##Calculo del valor actual neto con oferta
    van_con = 0
    for i in range(0,round(len(dataOferta.cliente['facturacion']))):
        van_con = van_con + (((dataOferta.aceptacion*dataOferta.contactabilidad*((1-dataOferta.cliente['prob_churn'].values[i]))*(dataOferta.cliente['facturacion'].values[i]-dataSinOferta['costos'].values[i]-dataOferta.costos_sac[i])+
							(1-dataOferta.aceptacion)*(1-dataSinOferta['prob_churn'].values[i])*(dataSinOferta['facturacion'].values[i]-dataSinOferta['costos'].values[i]))-dataOferta.costos_camp[i])*(pow((1+dataOferta.tasa_interes.mean()),i)))

    ##valor actual neto sin oferta
    van_sin = 0
    for i in range(0,round(len(dataOferta.cliente['facturacion']))):
        van_sin = van_sin + (dataSinOferta['facturacion'].values[i]-dataSinOferta['costos'].values[i])*((1-dataSinOferta['prob_churn'].values[i]))*(pow((1+dataOferta.tasa_interes.mean()),i))

    #valor actual neto con oferta teniendo en cuenta la aceptacion de la oferta
    #van_oferta = (dataOferta.aceptacion)*van_con*dataOferta.contactabilidad + (1-dataOferta.aceptacion)*(van_sin-dataOferta.costos[0])

    #Score por oferta en un determinado cliente


    return van_con - van_sin



def aceptacion_func(aceptacion_campania,tipo_oferta, cliente):

##ESTA FUNCION ASIGNA LA ACEPTACION DE LA OFERTA DEPENDIENDO DEL TIPO DE OFERTA Y DE LA PROPENSION DE CADA CLIENTE A ACEPTARLA

	aceptacion = 0

	if tipo_oferta == 'desc':
		aceptacion = aceptacion_campania
	elif tipo_oferta == 'cater':
		aceptacion = cliente.prob_cater
	elif tipo_oferta == 'upsell':
		aceptacion = cliente.prob_upsell
	elif tipo_oferta == 'cross':
		aceptacion = cliente.prob_digitales
	elif tipo_oferta == 'downsell':
		aceptacion = cliente.prob_downsell
	else:
		aceptacion = aceptacion_campania

	return aceptacion

def oferta_por_cliente(NBA_ani,cuits):

    scores_cuit_df = pd.DataFrame(index=NBA_ani.index,columns=cuits)
    scores_cuit = {}

    for y in range(0,len(NBA_ani.index)):
        for i in range(0,len(cuits)):
            scores_cuit[i] = 0
            for k in range(0,len(NBA_ani.columns)):
                if(NBA_ani.columns.values[k].split('_')[1] == cuits[i]):
                    scores_cuit[i] = scores_cuit[i] + NBA_ani.loc[NBA_ani.index.values[y],NBA_ani.columns.values[k]]
        for i in range(0,len(cuits)):
            scores_cuit_df.loc[NBA_ani.index.values[y],cuits[i]] = scores_cuit[i]

    return scores_cuit_df


def mejor_oferta(fact_oferta,churn_oferta,k,costos_of,aceptacion,tasa_interes,cliente,func_obj, contactabilidad):

    dataOferta = {}
    ##Ajusto variables de entrada para el calculo de los valores actuales cuando se hace una oferta
    for i in range(0,len(fact_oferta)):

        nombre = list(fact_oferta.keys())[i]
        tipo = list(fact_oferta.keys())[i].split('_')[0]
        acep = aceptacion_func(aceptacion[i],tipo,cliente)
        df = pd.DataFrame(columns=['facturacion','prob_churn'])
        df['facturacion'] = pd.Series(list(fact_oferta[nombre].loc[k,:])[1:])
        df['prob_churn'] = pd.Series(list(churn_oferta[nombre].loc[k,:])[1:])
        tasa_interes = pd.Series(tasa_interes)
        costos_sac = np.zeros(24)
        costos_camp = np.zeros(24)
        costos_sac[0] = costos_of.costos_sac[i]
        costos_camp[0] = costos_of.costos_campania[i]

        dataOferta[i] = ofertas(nombre,acep,tipo,df,costos_sac,costos_camp,tasa_interes,contactabilidad)

    dataSinOferta = pd.DataFrame()

    dataSinOferta['facturacion'] = cliente.cliente['facturacion']
    dataSinOferta['prob_churn'] = cliente.cliente['prob_churn']
    dataSinOferta['costos'] = cliente.cliente['costos']



    ##Calculo la diferencia entre valores actuales netos con y sin oferta
    scores = pd.Series()

    for i in range(0,len(dataOferta)):
        if(func_obj == 'van'):
            scores[dataOferta[i].oferta] = calculo_van_diff(dataOferta[i],dataSinOferta)
        elif(func_obj == 'ltv'):
            scores[dataOferta[i].oferta] = calculo_cltv(dataOferta[i],dataSinOferta)

    ##Ordeno de mayor a menor y expongo las dos principales ofertas y sus scores.
    #ordenados = scores.sort_values(ascending=False)

    #print('Oferta principal: '+ordenados.index.values[0]+' con un score de '+str((ordenados.values[0])))
    #print('Oferta secundaria: '+ordenados.index.values[1]+' con un score de '+str((ordenados.values[1])))
    #print('-------------')

    #devuelvo los scores ordenados para cada oferta
    #return ordenados
    return scores

if __name__ == "__main__":

    #BANCO DE PRUEBAS

    ##DATOS CLIENTES NORMAL

    d = {'ani': ['1','2','3','4','5','6','7','8','9','10','11','12'],
	'cuit':['a','a','b','b','b','b','c','c','c','d','d','d'],
    'fact': [220,250.3,230,500,420,125,600,623,121,597,875,210],
	'costos': [100,50,20,200,100,50,100,100,40,150,200,20],
    'churn_calibrated': [0.1,0.02,0.05,0.06,0.02,0.02,0.04,0.09,0.02,0.01,0.03,0.07],
	'contactabilidad':[0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5],
	'prob_upsell': [0.8,0.3,0.25,0.04,0.4,0.9,0.1,0.1,0.1,0.9,0.1,0.2],
	'prob_downsell': [0.5,0.2,0.1,0.4,0.87,0.19,0.11,0.12,0.41,0.91,0.11,0.12],
	'prob_cater': [0.25,0.72,0.91,0.54,0.29,0.59,0.71,0.62,0.41,0.11,0.781,0.412],
	'prob_digitales': [0.5,0.172,0.1911,0.354,0.229,0.959,0.271,0.162,0.141,0.811,0.1,0.7412]}

    data = pd.DataFrame(data=d)

    clientes = {}
    df = pd.DataFrame()

    ##Datos del cliente
    for i in range(0,len(data['ani'])):
        ani = data['ani'].values[i]
        cuit = data['cuit'].values[i]
        id_ = 'empresa_'+data['cuit'].values[i]+'_'+data['ani'].values[i]
        df['facturacion'] = pd.Series(data['fact'].values[i]*np.ones(24))
        df['prob_churn'] = pd.Series(data['churn_calibrated'].values[i]*np.ones(24))
        df['costos'] = pd.Series(data['costos'].values[i]*np.ones(24))

        clientes[i] = cliente(ani,cuit,id_,df,data['contactabilidad'].values[i],data['prob_upsell'].values[i],data['prob_downsell'].values[i],data['prob_cater'].values[i],data['prob_digitales'].values[i])

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

    costos_in = costos_class(fp.costo_total(of)['cost_sac'],fp.costo_total(of)['cost_campana_in'])
    costos_out = costos_class(fp.costo_total(of)['cost_sac'],fp.costo_total(of)['cost_campana_out'])

    ##Tasa Interes
    tasa_interes = list(0.02*np.ones(24))

    ##Funcion objetivo ('van' o 'ltv')
    func_obj = 'van'

    NBA_in = pd.DataFrame()
    NBA_out = pd.DataFrame()


    for i in range(0,len(clientes)):
        NBA_in[clientes[i].rs] = mejor_oferta(fact_oferta,churn_oferta,i,costos_in,aceptacion_in,tasa_interes,clientes[i],func_obj, data['contactabilidad'].values[i])
        NBA_out[clientes[i].rs] = mejor_oferta(fact_oferta,churn_oferta,i,costos_out,aceptacion_out,tasa_interes,clientes[i],func_obj, data['contactabilidad'].values[i])

    #print(NBA_in)
    #print(NBA_out)

    ##OFERTA AGRUPADA POR CUIT

    cuits = list(data['cuit'].unique())
    oferta_cuit_in = oferta_por_cliente(NBA_in,cuits)
    oferta_cuit_out = oferta_por_cliente(NBA_out,cuits)


    ##Para el IN
    for i in range(0,len(oferta_cuit_in.columns)):
        ordenados = oferta_cuit_in[oferta_cuit_in.columns.values[i]].sort_values(ascending=False)
        print('Oferta principal para el cliente '+oferta_cuit_in.columns.values[i]+' en el IN es '+ordenados.index.values[0]+' con un score de '+str((ordenados.values[0])))
        print('Oferta secundaria para el cliente '+oferta_cuit_in.columns.values[i]+' en el IN es '+ordenados.index.values[1]+' con un score de '+str((ordenados.values[1])))
        print('-------------')


    ##Para el OUT
    for i in range(0,len(oferta_cuit_out.columns)):
        ordenados = oferta_cuit_out[oferta_cuit_out.columns.values[i]].sort_values(ascending=False)
        print('Oferta principal para el cliente '+oferta_cuit_out.columns.values[i]+' en el OUT es '+ordenados.index.values[0]+' con un score de '+str((ordenados.values[0])))
        print('Oferta secundaria para el cliente '+oferta_cuit_out.columns.values[i]+' en el OUT es '+ordenados.index.values[1]+' con un score de '+str((ordenados.values[1])))
        print('-------------')

                            	

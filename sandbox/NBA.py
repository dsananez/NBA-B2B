# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 16:10:33 2018

@author: gchiesap
"""

import pandas as pd
import numpy as np
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


def fold(l, operador, neutro):
  if l == []:
    return(neutro)
  e = l.pop(0)
  return(operador(e, fold(l,operador,neutro)))
def producto(x,y):
  return(x*y)


def q_esperado_sin_oferta(clientes,meses):
    q_esperado = {}
    for k in range(0,meses):
        q_esperado[k] = 0
        for i in range(0,len(clientes)):
            cuenta = fold(list(1-clientes[i].cliente.prob_churn[0:k]),producto,1)
            q_esperado[k] = q_esperado[k] + cuenta
    return q_esperado

def fact_esperado_sin_oferta(clientes,meses):
    fact_esperado = {}
    for k in range(0,meses):
        fact_esperado[k] = 0
        for i in range(0,len(clientes)):
            cuenta = fold(list((1-clientes[i].cliente.prob_churn[0:k])),producto,1)
            cuenta = cuenta*clientes[i].cliente.facturacion[k]
            fact_esperado[k] = fact_esperado[k] + cuenta
        if(k>=1):
            fact_esperado[k] = fact_esperado[k] + fact_esperado[k-1]
    return fact_esperado

def q_esperado_oferta(churn_oferta,clientes,oferta,NBA_ani,umbral,meses):
    q_esperado = {}
    for k in range(0,meses):
        q_esperado[k] = 0
        for i in range(0,len(churn_oferta[oferta])):
            if(NBA_ani.loc[oferta,'empresa_'+clientes[i].cuit+'_'+str(clientes[i].ani)]>=umbral):
                cuenta = fold(list(1-churn_oferta[oferta].loc[:, churn_oferta[oferta].columns != 'ani'].loc[i][0:k]),producto,1)
            else:
                cuenta = fold(list((1-clientes[i].cliente.prob_churn[0:k])),producto,1)
            q_esperado[k] = q_esperado[k] + cuenta
    return q_esperado


def fact_esperado_oferta(churn_oferta,fact_oferta,clientes,oferta,NBA_ani,umbral,meses):
    q_esperado = {}
    for k in range(0,meses):
        q_esperado[k] = 0
        for i in range(0,len(churn_oferta[oferta])):
            if(NBA_ani.loc[oferta,'empresa_'+clientes[i].cuit+'_'+str(clientes[i].ani)]>=umbral):
                cuenta = fold(list(1-churn_oferta[oferta].loc[:, churn_oferta[oferta].columns != 'ani'].loc[i][0:k]),producto,1)
                cuenta = cuenta*fact_oferta[oferta].loc[:, churn_oferta[oferta].columns != 'ani'].loc[i,k]
            elif(NBA_ani.loc[oferta,'empresa_'+clientes[i].cuit+'_'+str(clientes[i].ani)]<umbral):
                cuenta = fold(list((1-clientes[i].cliente.prob_churn[0:k])),producto,1)
                cuenta = cuenta*clientes[i].cliente.facturacion[k]
            q_esperado[k] = q_esperado[k] + cuenta
        if(k>=1):
            q_esperado[k] = q_esperado[k] + q_esperado[k-1]
    return q_esperado


def calculo_cltv(dataOferta, dataSinOferta):

##Calculo del customer lifetime value

	t1 = 1/(dataSinOferta['prob_churn']).mean()
	t2 = 1/dataOferta.cliente['prob_churn'].mean()


	ltv_con = ((dataOferta.aceptacion *dataOferta.contactabilidad* ((dataOferta.cliente['facturacion']-dataSinOferta['costos']-dataOferta.costos_sac-dataOferta.costos_camp).mean())*t2)+
    ((1-dataOferta.aceptacion)*((dataSinOferta['facturacion']-dataSinOferta['costos']-dataOferta.costos_camp).mean())*t1))


	ltv_sin = ((dataSinOferta['facturacion']-dataSinOferta['costos']).mean())*t1

	return ltv_con - ltv_sin


def calculo_van_diff(dataOferta,dataSinOferta,meses):

    ##Calculo del valor actual neto con oferta
    van_con = 0
    for i in range(0,meses):
        van_con = van_con + (((dataOferta.aceptacion*dataOferta.contactabilidad*((1-dataOferta.cliente['prob_churn'].values[i]))*(dataOferta.cliente['facturacion'].values[i]-dataSinOferta['costos'].values[i]-dataOferta.costos_sac[i])+
							(1-dataOferta.aceptacion)*(1-dataSinOferta['prob_churn'].values[i])*(dataSinOferta['facturacion'].values[i]-dataSinOferta['costos'].values[i]))-dataOferta.costos_camp[i])/(pow((1+dataOferta.tasa_interes.mean()),i)))

    ##valor actual neto sin oferta
    van_sin = 0
    for i in range(0,meses):
        van_sin = van_sin + ((dataSinOferta['facturacion'].values[i]-dataSinOferta['costos'].values[i])*((1-dataSinOferta['prob_churn'].values[i])))/(pow((1+dataOferta.tasa_interes.mean()),i))

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


def mejor_oferta(fact_oferta,churn_oferta,k,costos_of,aceptacion,tasa_interes,cliente,func_obj, contactabilidad,meses):

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
            scores[dataOferta[i].oferta] = calculo_van_diff(dataOferta[i],dataSinOferta,meses)
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

def NBA(base_clientes,of,plataforma,func_obj,tipo_canal,meses,umbral):

    #BANCO DE PRUEBAS

    #data = pd.read_csv('pruebas.csv',sep=';')

    clientes = {}
    df = pd.DataFrame()

    ##Datos del cliente
    for i in range(0,len(base_clientes['ani'])):
        ani = base_clientes['ani'].values[i]
        cuit = base_clientes['cuit'].values[i]
        id = 'empresa_'+base_clientes['cuit'].values[i]+'_'+str(base_clientes['ani'].values[i])
        df['facturacion'] = pd.Series(base_clientes['fact'].values[i]*np.ones(24))
        df['prob_churn'] = pd.Series(base_clientes['churn_calibrated'].values[i]*np.ones(24))
        df['costos'] = pd.Series(base_clientes['costos'].values[i]*np.ones(24))

        clientes[i] = cliente(ani,cuit,id,df.copy(),base_clientes['contactabilidad'].values[i],base_clientes['prob_upsell'].values[i],base_clientes['prob_downsell'].values[i],base_clientes['prob_cater'].values[i],base_clientes['prob_digitales'].values[i])

    ##Ofertas
    #of = pd.read_csv('listado_campanas.txt', sep=",")

    #FACTURACION CUANDO SE APLICA LA OFERTA
    fact_oferta = fp.fact_24(base_clientes,of)

    ##REEMPLAZAR POR EL CHURN CON OFERTA
    churn_oferta = fp.churn_24(base_clientes,of)

    ##Plataforma
    #plataforma = pd.read_csv('modelo_plataforma_cc.txt', sep=",")

    ##Aceptacion Ofertas
    if(tipo_canal == 'IN'):
        aceptacion = list(of['aceptacion_in'])
    elif(tipo_canal =='OUT'):
        aceptacion = list(of['aceptacion_out'])

    ##Costos
    if(tipo_canal == 'IN'):
        costos = costos_class(fp.costo_total(of,plataforma)['cost_sac'],fp.costo_total(of,plataforma)['cost_campana_in'])
    elif(tipo_canal =='OUT'):
        costos = costos_class(fp.costo_total(of,plataforma)['cost_sac'],fp.costo_total(of,plataforma)['cost_campana_out'])

    ##Tasa Interes
    tasa_interes = list(0.02*np.ones(24))

    NBA_ = pd.DataFrame()


    for i in range(0,len(clientes)):
        NBA_[clientes[i].rs] = mejor_oferta(fact_oferta,churn_oferta,i,costos,aceptacion,tasa_interes,clientes[i],func_obj, base_clientes['contactabilidad'].values[i],meses)

    ##OFERTA AGRUPADA POR CUIT

    cuits = list(base_clientes['cuit'].unique())
    oferta_cuit = oferta_por_cliente(NBA_,cuits)

    ##Retención clientes con y sin oferta
    q = pd.DataFrame()
    for i in range(0,len(of)):
        q_of = q_esperado_oferta(churn_oferta,clientes,of['id_oferta'][i],NBA_,umbral,meses)
        q[of['id_oferta'][i]] = pd.Series(q_of)

    q['sin oferta'] = pd.Series(q_esperado_sin_oferta(clientes,meses))

    ##Facturacion esperada con y sin oferta
    fact = pd.DataFrame()
    for i in range(0,len(of)):
        f_of = fact_esperado_oferta(churn_oferta,fact_oferta,clientes,of['id_oferta'][i],NBA_,umbral,meses)
        fact[of['id_oferta'][i]] = pd.Series(f_of)

    fact['sin oferta'] = pd.Series(fact_esperado_sin_oferta(clientes,meses))


    return oferta_cuit,NBA_,q,fact

#if __name__ == "__main__":
#
#    base_clientes = pd.read_csv('pruebas.csv',sep=';')
#    ofert = pd.read_csv('listado_campanas.txt', sep=",")
#    plataforma = pd.read_csv('modelo_plataforma_cc.txt', sep=",")
#
#    [oferta_cuit,NBA_,q,fact] = NBA(base_clientes,ofert,plataforma,'van','IN',12)

                   	

# DATAFRAMES DE PRUEBA

import pandas as pd

d = {'tipo_oferta': ['cater','up_sell','bono','descuento','descuento','up_sell','descuento','bono','up_sell','cross_sell','bono','up_sell']}
data1 = pd.DataFrame(data=d)
data2 = pd.read_csv('listado_campanas.txt', sep=",")

d = {'fact': [220,250.3,230,500,420,125,600,623,121,597,875,210],
    'msisdn_id': ['1','2','3','4','5','6','7','8','9','10','11','12'],
    'churn_calibrated': [0.01,0.03,0.02,0.06,0.08,0.09,0.12,0.05,0.01,0.02,0.01,0.02]}
data3 = pd.DataFrame(data=d)

#FUNCIONES

import pandas as pd
import numpy as np

def costo_plataforma(df, t_util = 8, efic_rep = 0.75, dias_lab = 6, q_sem = 4):
    """
    Calcula costes de plataforma IN/OUT, donde
        df: data frame con columna tipo_oferta
        t_util: horas utiles diarias por rep
        efic_rep: % de eficiencia promedio por rep
        dias_lab: cantidad de dias disponibles para llamar (por semana)
        q_sem: cantidad de semanas al mes
    :return:
    """
    ofertas = pd.read_csv('modelo_plataforma_cc.txt', sep=",")
    ofertas['cost_plat_in'] = 0
    ofertas['cost_plat_out'] = ofertas['cost_hora_pos']*ofertas['dur_llam_out']/ofertas['efic_rep']

    result = pd.merge(df, ofertas, on = 'tipo_oferta', how = 'left')

    return result[['cost_plat_in','cost_plat_out']]

def costo_sac(df):
    """
    Calcula costes SAC totales, donde
        df: data frame con columnas:
            - subsidio
            - logistica
            - comisiones
    :return:
    """
    costo_sac = {'cost_sac': df['subsidio'] + df['logistica'] + df['comisiones']}
    costo_sac_df = pd.DataFrame(data=costo_sac)
    return costo_sac_df

def costo_campana(df):
    """
    Calcula costes de campana totales IN/OUT, donde
        df: data frame con columnas:
            - cost_plat_in
            - cost_plat_out
            - cost_sac
        :return:
     """
    cost_campana = {'cost_campana_in': df['cost_plat_in'] + df['cost_sac'],
                    'cost_campana_out': df['cost_plat_out'] + df['cost_sac']}
    cost_campana_df = pd.DataFrame(data=cost_campana)
    return cost_campana_df

def costo_total(df, t_util = 8, efic_rep = 0.75, dias_lab = 6, q_sem = 4):
    """
    Corre las 3 funciones anteriores, donde
        df: data frame con columna tipo_oferta
        t_util: horas utiles diarias por rep
        efic_rep: % de eficiencia promedio por rep
        dias_lab: cantidad de dias disponibles para llamar (por semana)
        q_sem: cantidad de semanas al mes
    :return:
    """

    cost_plat = costo_plataforma(df, t_util, efic_rep, dias_lab, q_sem)
    cost_sac = costo_sac(df)
    cost_campana = costo_campana(pd.concat([cost_plat, cost_sac], axis=1))
    return cost_campana

def fact_24(df):
    """
    Calcula facturacion estimada proximos 24 meses, donde
        df: data frame con columnas:
            - msisdn_id: ani del cliente
            - fact: facturacion plan + excedentes
        listado_campanas.txt: archivo de texto con informacion de las campañas
    :return:
    """

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

def churn_post_oferta(churn_orig, churn_nvo, dur_oferta, progresivo = True):
    """
    Calcula churn estimado al vencimiento de una oferta, donde
        churn_orig: churn antes de aceptar la oferta
        churn_nvo: churn despues de aceptar la oferta
        dur_oferta: duracion de la oferta (meses)
        dur_blindaje: duracion del blindaje
    :return:
    """
    churn_of = list(np.repeat(churn_nvo, dur_oferta))

    churn_blin = list()

    if progresivo:
        churn_n = churn_nvo*1.1
        while churn_n < churn_orig and len(churn_blin) < 24 - dur_oferta:
            churn_blin.append(churn_n)
            churn_n = churn_n*1.1

    churn_po = list(np.repeat(churn_orig, 24 - dur_oferta - len(churn_blin)))

    return churn_of + churn_blin + churn_po

def churn_24(df):
    """
    Calcula churn estimado proximos 24 meses, donde
        df: data frame con columnas:
            - msisdn_id: ani del cliente
            - churn_calibrated: churn mensual calibrado (probabilidad real)
        listado_campanas.txt: archivo de texto con informacion de las campañas
    :return:
    """

    churn_oferta = {}
    ofertas = pd.read_csv('listado_campanas.txt', sep=",")

    for i in range(0,len(ofertas)):
        churn_esp = ofertas['churn_esp_n1'][i]
        churn = np.array([], dtype=np.float).reshape(0,24)

        if ofertas['tipo_oferta'][i] == 'cater':

            if ofertas['tipo_churn'][i] == 'delta':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = df['churn_calibrated'][k] + churn_esp
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, 12)
                    churn = np.vstack([churn, churn_24])
            elif ofertas['tipo_churn'][i] == 'aumento_porct':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = df['churn_calibrated'][k]*(1+churn_esp)
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, 12)
                    churn = np.vstack([churn, churn_24])
            elif ofertas['tipo_churn'][i] == 'fijo':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = churn_esp
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, 12)
                    churn = np.vstack([churn, churn_24])

        elif ofertas['tipo_oferta'][i] == 'bono':

            duracion = int(ofertas['id_oferta'][i].split('_')[2])

            if ofertas['tipo_churn'][i] == 'delta':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = df['churn_calibrated'][k] + churn_esp
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, duracion)
                    churn = np.vstack([churn, churn_24])
            elif ofertas['tipo_churn'][i] == 'aumento_porct':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = df['churn_calibrated'][k]*(1+churn_esp)
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, duracion)
                    churn = np.vstack([churn, churn_24])
            elif ofertas['tipo_churn'][i] == 'fijo':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = churn_esp
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, duracion)
                    churn = np.vstack([churn, churn_24])

        elif ofertas['tipo_oferta'][i] == 'cross_sell':

            if ofertas['tipo_churn'][i] == 'delta':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = df['churn_calibrated'][k] + churn_esp
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, 12, progresivo = False)
                    churn = np.vstack([churn, churn_24])
            elif ofertas['tipo_churn'][i] == 'aumento_porct':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = df['churn_calibrated'][k]*(1+churn_esp)
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, 12, progresivo = False)
                    churn = np.vstack([churn, churn_24])
            elif ofertas['tipo_churn'][i] == 'fijo':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = churn_esp
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, 12, progresivo = False)
                    churn = np.vstack([churn, churn_24])

        elif ofertas['tipo_oferta'][i] == 'up_sell':

            if ofertas['tipo_churn'][i] == 'delta':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = df['churn_calibrated'][k] + churn_esp
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, 12, progresivo = False)
                    churn = np.vstack([churn, churn_24])
            elif ofertas['tipo_churn'][i] == 'aumento_porct':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = df['churn_calibrated'][k]*(1+churn_esp)
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, 12, progresivo = False)
                    churn = np.vstack([churn, churn_24])
            elif ofertas['tipo_churn'][i] == 'fijo':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = churn_esp
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, 12, progresivo = False)
                    churn = np.vstack([churn, churn_24])

        elif ofertas['tipo_oferta'][i] == 'descuento':

            if ofertas['id_oferta'][i].split('_')[2] == 'indef':
                duracion = 24
            else:
                duracion = int(ofertas['id_oferta'][i].split('_')[2])

            if ofertas['tipo_churn'][i] == 'delta':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = df['churn_calibrated'][k] + churn_esp
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, duracion)
                    churn = np.vstack([churn, churn_24])
            elif ofertas['tipo_churn'][i] == 'aumento_porct':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = df['churn_calibrated'][k]*(1+churn_esp)
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, duracion)
                    churn = np.vstack([churn, churn_24])
            elif ofertas['tipo_churn'][i] == 'fijo':
                for k in range(0,len(df)):
                    churn_orig = df['churn_calibrated'][k]
                    churn_nvo = churn_esp
                    churn_24 = churn_post_oferta(churn_orig, churn_nvo, duracion)
                    churn = np.vstack([churn, churn_24])

        churn_oferta[ofertas['id_oferta'][i]] = pd.concat([df['msisdn_id'], pd.DataFrame(data=churn)], axis=1)

    return churn_oferta


churn_24(data3)

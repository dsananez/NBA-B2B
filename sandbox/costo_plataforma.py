# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 16:20:37 2018

@author: dsananez
"""
import pandas as pd

d = {'tipo_oferta': ['cater','upsell','bono','descuento','descuento','upsell','descuento','bono','upsell','cross_sell','bono','upsell']}
data = pd.DataFrame(data=d)


def costo_plataforma(df, t_util = 8, efic_rep = 0.75, dias_lab = 6, q_sem = 4):
    """
    Calcula costes de plataforma IN/OUT donde
        df: data frame con columna tipo_oferta
        t_util: horas utiles diarias por rep
        efic_rep: % de eficiencia promedio por rep
        dias_lab: cantidad de dias disponibles para llamar (por semana)
        q_sem: cantidad de semanas al mes
        :return:
    """
    import pandas as pd
    ofertas = pd.read_csv('modelo_plataforma_cc.txt', sep=",")
    ofertas['cost_plat_in'] = 0
    ofertas['cost_plat_out'] = ofertas['cost_hora_pos']*ofertas['dur_llam_out']/ofertas['efic_rep']
    
    result = pd.merge(df, ofertas, on = 'tipo_oferta', how = 'left')
    
    return result[['cost_plat_in','cost_plat_out']]

costo_plataforma(data)

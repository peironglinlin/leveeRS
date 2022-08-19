import pandas as pd
import numpy as np

def calc_cons_year_levee_effect(df):
    df1 = df[df['year_diff'].isin([-10,-9,-8,-7,-6])].groupby('cons_year')[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_1','county_urban':'county_urban_1'})
    df2 = df[df['year_diff'].isin([-5,-4,-3,-2,-1])].groupby('cons_year')[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_2','county_urban':'county_urban_2'})
    df3 = df[df['year_diff'].isin([1,2,3,4,5])].groupby('cons_year')[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_3','county_urban':'county_urban_3'})
    df4 = df[df['year_diff'].isin([6,7,8,9,10])].groupby('cons_year')[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_4','county_urban':'county_urban_4'})

    df0 = df1.merge(df2,on='cons_year').merge(df3,on='cons_year').merge(df4,on='cons_year')

    df0['levee_urban_ratio'] = (df0['levee_urban_4']-df0['levee_urban_3'])/(df0['levee_urban_2']-df0['levee_urban_1'])-1
    df0['levee_urban_ratio'] = df0['levee_urban_ratio'].fillna(0)
    df0['county_urban_ratio'] = (df0['county_urban_4']-df0['county_urban_3'])/(df0['county_urban_2']-df0['county_urban_1'])-1
    df0['county_urban_ratio'] = df0['county_urban_ratio'].fillna(0)
    df0['levee_effect'] = df0['levee_urban_ratio']-df0['county_urban_ratio']
    df0['levee_effect'].replace(np.inf, 999, inplace=True)
    df0['levee_effect'].replace(-np.inf, -999, inplace=True)
    return df0

if __name__=='__main__':
    df = pd.read_csv('processed_data/processed_levee_county_combined.csv')

    df1 = pd.read_csv('data/P_systemID_year_0813.csv')
    df1 = df1[['systemId','Levee_year']].drop_duplicates()
    y_map = {}
    nstep = 7
    for y in range(1900,2025):
        y_map[y] = '%s-%s'%(int(y/nstep)*nstep,int(y/nstep)*nstep+nstep-1)
    df1['cons_year'] = df1['Levee_year'].map(y_map)
    # df1['cons_year'] = df1['Levee_year']

    df = pd.merge(df,df1[['systemId','cons_year']],on=['systemId'],how='left')
    df = df.groupby(['year_diff','cons_year'])[['levee_urban','county_urban','levee_area','county_area']].apply(np.sum).reset_index()
    df.to_csv('processed_data/cons_year_urban.csv',index=False)

    # 计算 state level的levee effect
    df_output = calc_cons_year_levee_effect(df)
    df_output.to_csv('processed_data/cons_year_levee_effect.csv',index=False)

	




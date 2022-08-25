import pandas as pd
import numpy as np
import statsmodels.api as sm

def calc_watershed_levee_effect(df):
    df1 = df[df['year_diff'].isin([-10,-9,-8,-7,-6])].groupby(lev_colname)[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_1','county_urban':'county_urban_1'})
    df2 = df[df['year_diff'].isin([-5,-4,-3,-2,-1])].groupby(lev_colname)[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_2','county_urban':'county_urban_2'})
    df3 = df[df['year_diff'].isin([1,2,3,4,5])].groupby(lev_colname)[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_3','county_urban':'county_urban_3'})
    df4 = df[df['year_diff'].isin([6,7,8,9,10])].groupby(lev_colname)[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_4','county_urban':'county_urban_4'})

    df_output = df1.merge(df2,on=lev_colname).merge(df3,on=lev_colname).merge(df4,on=lev_colname)

    df_output['levee_urban_ratio'] = (df_output['levee_urban_4']-df_output['levee_urban_3'])/(df_output['levee_urban_2']-df_output['levee_urban_1'])-1
    df_output['levee_urban_ratio'] = df_output['levee_urban_ratio'].fillna(0)
    df_output['county_urban_ratio'] = (df_output['county_urban_4']-df_output['county_urban_3'])/(df_output['county_urban_2']-df_output['county_urban_1'])-1
    df_output['county_urban_ratio'] = df_output['county_urban_ratio'].fillna(0)
    df_output['levee_effect'] = df_output['levee_urban_ratio']-df_output['county_urban_ratio']
    df_output['levee_effect'].replace(np.inf, 999, inplace=True)
    df_output['levee_effect'].replace(-np.inf, -999, inplace=True)
    return df_output

def _regr(df):
    X = sm.add_constant(np.array([[i] for i in range(len(df))]))
    est1 = sm.OLS(df['levee_urban'].values, X).fit()
    est2 = sm.OLS(df['county_urban'].values, X).fit()
    return pd.Series({'k_levee':est1.params[1],'p_levee':est1.f_pvalue,'k_county':est2.params[1],'p_county':est2.f_pvalue})


def calc_watershed_levee_effect_regr(df,by='STATE'):
    df1 = df[df['year_diff']<0].groupby(by)[['levee_urban','county_urban']]\
            .apply(_regr)\
            .reset_index()\
            .rename(columns={'k_levee':'k_levee_1','p_levee':'p_levee_1','k_county':'k_county_1','p_county':'p_county_1'})
    df2 = df[df['year_diff']>0].groupby(by)[['levee_urban','county_urban']]\
            .apply(_regr)\
            .reset_index()\
            .rename(columns={'k_levee':'k_levee_2','p_levee':'p_levee_2','k_county':'k_county_2','p_county':'p_county_2'})

    df0 = df1.merge(df2,on=by)
    return df0

if __name__=='__main__':
    for level in (2,4,6,8):
        df = pd.read_csv('processed_data/processed_levee_county_combined.csv')
        lev_colname = 'huc%s'%level

        df1 = pd.read_csv('data/ID_link_systemId_HUC%s.csv'%level)
        df1 = df1[['systemId',lev_colname]].drop_duplicates()

        df = pd.merge(df,df1,on=['systemId'],how='left')
        df[lev_colname] = df[lev_colname].fillna('None')
        df = df.groupby(['year_diff',lev_colname])[['levee_urban','county_urban']].apply(np.sum).reset_index()
        df.to_csv('watershed_urban_%s.csv'%lev_colname,index=False)

        df_output = calc_watershed_levee_effect(df)
        df_output.to_csv('watershed_levee_effect_%s.csv'%lev_colname,index=False)

        # 计算 watershed level的levee effect using linear regression
        df_output = calc_watershed_levee_effect_regr(df,by=lev_colname)
        df_output.to_csv('processed_data/watershed_levee_effect_%s_regr.csv'%lev_colname,index=False)

	




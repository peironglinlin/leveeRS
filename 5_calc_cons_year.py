import pandas as pd
import numpy as np
import statsmodels.api as sm

def calc_cons_year_levee_effect(df):
    df1 = df[df['year_diff'].isin([-10,-9,-8,-7,-6])].groupby('Levee_year')[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_1','county_urban':'county_urban_1'})
    df2 = df[df['year_diff'].isin([-5,-4,-3,-2,-1])].groupby('Levee_year')[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_2','county_urban':'county_urban_2'})
    df3 = df[df['year_diff'].isin([1,2,3,4,5])].groupby('Levee_year')[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_3','county_urban':'county_urban_3'})
    df4 = df[df['year_diff'].isin([6,7,8,9,10])].groupby('Levee_year')[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_4','county_urban':'county_urban_4'})

    df0 = df1.merge(df2,on='Levee_year').merge(df3,on='Levee_year').merge(df4,on='Levee_year')

    df0['levee_urban_ratio'] = (df0['levee_urban_4']-df0['levee_urban_3'])/(df0['levee_urban_2']-df0['levee_urban_1'])-1
    df0['levee_urban_ratio'] = df0['levee_urban_ratio'].fillna(0)
    df0['county_urban_ratio'] = (df0['county_urban_4']-df0['county_urban_3'])/(df0['county_urban_2']-df0['county_urban_1'])-1
    df0['county_urban_ratio'] = df0['county_urban_ratio'].fillna(0)
    df0['levee_effect'] = df0['levee_urban_ratio']-df0['county_urban_ratio']
    df0['levee_effect'].replace(np.inf, 999, inplace=True)
    df0['levee_effect'].replace(-np.inf, -999, inplace=True)
    return df0

def _regr(df):
    X = sm.add_constant(np.array([[i] for i in range(len(df))]))
    est1 = sm.OLS(df['levee_urban'].values, X).fit()
    est2 = sm.OLS(df['county_urban'].values, X).fit()
    return pd.Series({'k_levee':est1.params[1],'p_levee':est1.f_pvalue,'k_county':est2.params[1],'p_county':est2.f_pvalue})

def calc_cons_year_levee_effect_regr(df,by='Levee_year'):
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
    dfx = pd.read_csv("data/P_systemID_year_0813.csv")
    dfx = dfx[['systemId','Levee_year']].drop_duplicates()
    min_y = dfx.Levee_year.min()
    max_y = dfx.Levee_year.max()
    for nstep in range(3,11,2):
        df = pd.read_csv('processed_data/processed_levee_county_combined.csv')
        df = pd.merge(df,dfx[['systemId','Levee_year']],on=['systemId'],how='left')
        list_df = [df]

        for i in range(int(nstep/2)):
            df1 = df.copy()
            df1['Levee_year'] = df1['Levee_year']-i-1
            df2 = df.copy()
            df2['Levee_year'] = df2['Levee_year']+i+1
            list_df = list_df+[df1,df2]
        df = pd.concat(list_df, ignore_index=True)
        df.loc[df.Levee_year<min_y,'Levee_year'] = min_y
        df.loc[df.Levee_year>max_y,'Levee_year'] = max_y

        df = df.groupby(['year_diff','Levee_year'])[['levee_urban','county_urban','levee_area','county_area']].apply(np.sum).reset_index()

        df.to_csv('processed_data/cons_year_urban_%syr.csv'%nstep,index=False)

        # 计算 state level的levee effect
        df_output = calc_cons_year_levee_effect(df)
        df_output.to_csv('processed_data/cons_year_levee_effect_%syr.csv'%nstep,index=False)

        # 计算 state level的levee effect using linear regression
        df_output = calc_cons_year_levee_effect_regr(df)
        df_output.to_csv('processed_data/cons_year_levee_effect_%syr_regr.csv'%nstep,index=False)

	




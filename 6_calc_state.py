import pandas as pd
import numpy as np
import statsmodels.api as sm

states = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}

def calc_state_levee_effect(df):
    df1 = df[df['year_diff'].isin([-10,-9,-8,-7,-6])].groupby('STATE')[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_1','county_urban':'county_urban_1'})
    df2 = df[df['year_diff'].isin([-5,-4,-3,-2,-1])].groupby('STATE')[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_2','county_urban':'county_urban_2'})
    df3 = df[df['year_diff'].isin([1,2,3,4,5])].groupby('STATE')[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_3','county_urban':'county_urban_3'})
    df4 = df[df['year_diff'].isin([6,7,8,9,10])].groupby('STATE')[['levee_urban','county_urban']]\
            .apply(np.mean).reset_index()\
            .rename(columns={'levee_urban':'levee_urban_4','county_urban':'county_urban_4'})

    df0 = df1.merge(df2,on='STATE').merge(df3,on='STATE').merge(df4,on='STATE')

    df0['levee_urban_ratio'] = (df0['levee_urban_4']-df0['levee_urban_3'])/(df0['levee_urban_2']-df0['levee_urban_1'])-1
    df0['levee_urban_ratio'] = df0['levee_urban_ratio'].fillna(0)
    df0['county_urban_ratio'] = (df0['county_urban_4']-df0['county_urban_3'])/(df0['county_urban_2']-df0['county_urban_1'])-1
    df0['county_urban_ratio'] = df0['county_urban_ratio'].fillna(0)
    df0['levee_effect'] = df0['levee_urban_ratio']-df0['county_urban_ratio']
    df0['levee_effect'].replace(np.inf, 999, inplace=True)
    df0['levee_effect'].replace(-np.inf, -999, inplace=True)
    df0['state'] = df0['STATE'].map(states)
    return df0

def _regr(df):
    X = sm.add_constant(np.array([[i] for i in range(len(df))]))
    est1 = sm.OLS(df['levee_urban'].values, X).fit()
    est2 = sm.OLS(df['county_urban'].values, X).fit()
    return pd.Series({'k_levee':est1.params[1],'p_levee':est1.f_pvalue,'k_county':est2.params[1],'p_county':est2.f_pvalue})


def calc_state_levee_effect_regr(df):
    df1 = df[df['year_diff']<0].groupby('STATE')[['levee_urban','county_urban']]\
            .apply(_regr)\
            .reset_index()\
            .rename(columns={'k_levee':'k_levee_1','p_levee':'p_levee_1','k_county':'k_county_1','p_county':'p_county_1'})
    df2 = df[df['year_diff']>0].groupby('STATE')[['levee_urban','county_urban']]\
            .apply(_regr)\
            .reset_index()\
            .rename(columns={'k_levee':'k_levee_2','p_levee':'p_levee_2','k_county':'k_county_2','p_county':'p_county_2'})

    df0 = df1.merge(df2,on='STATE')
    df0['state'] = df0['STATE'].map(states)
    return df0

if __name__=='__main__':
    df = pd.read_csv('processed_data/processed_levee_county_combined.csv')

    # 计算全国的levee ratio
    x1 = df[df['year_diff'].isin([-10,-9,-8,-7,-6])][['levee_urban','county_urban']].mean()
    x2 = df[df['year_diff'].isin([-5,-4,-3,-2,-1])][['levee_urban','county_urban']].mean()
    x3 = df[df['year_diff'].isin([1,2,3,4,5])][['levee_urban','county_urban']].mean()
    x4 = df[df['year_diff'].isin([6,7,8,9,10])][['levee_urban','county_urban']].mean()
    x = (x4-x3)/(x2-x1)
    us_levee_effect = x['levee_urban']-x['county_urban']
    print("us levee = %s"%us_levee_effect)

    df1 = pd.read_csv('data/ID_link_systemId_STATE1.csv')
    df1 = df1[['systemId','STATE']].drop_duplicates()

    df = pd.merge(df,df1,on=['systemId'],how='left')
    df['STATE'] = df['STATE'].fillna('None')
    df = df.groupby(['year_diff','STATE'])[['levee_urban','county_urban','levee_area','county_area']].apply(np.sum).reset_index()
    df.to_csv('processed_data/state_urban.csv',index=False)

    df[df.year_diff>0].groupby(['STATE'])[['levee_urban','county_urban','levee_area','county_area']]\
        .apply(np.sum).reset_index().to_csv('state_urban_ratio.csv',index=False)

    # 计算levee urban ratio的变化
    df1 = df[df['year_diff']<0].groupby(['STATE'])[['levee_urban','levee_area']].apply(np.sum).reset_index()
    df1['levee_urban_ratio_prior'] = df1['levee_urban']/df1['levee_area']
    df2 = df[df['year_diff']>0].groupby(['STATE'])[['levee_urban','levee_area']].apply(np.sum).reset_index()
    df2['levee_urban_ratio_after'] = df2['levee_urban']/df2['levee_area']
    df3 = df1[['STATE','levee_urban_ratio_prior']].merge(df2[['STATE','levee_urban_ratio_after']],on='STATE')
    df3['levee_urban_ratio_diff'] = df3['levee_urban_ratio_after']-df3['levee_urban_ratio_prior']
    df3.to_csv('processed_data/state_levee_urban_change.csv',index=False)

    # 计算 state level的levee effect
    df_output = calc_state_levee_effect(df)
    df_output.to_csv('processed_data/state_levee_effect.csv',index=False)

    # 计算 state level的levee effect using linear regression
    df_output = calc_state_levee_effect_regr(df)
    df_output.to_csv('processed_data/state_levee_effect_regr.csv',index=False)

	




import pandas as pd
import numpy as np

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

        df = df1.merge(df2,on=lev_colname).merge(df3,on=lev_colname).merge(df4,on=lev_colname)

        df['levee_urban_ratio'] = (df['levee_urban_4']-df['levee_urban_3'])/(df['levee_urban_2']-df['levee_urban_1'])-1
        df['levee_urban_ratio'] = df['levee_urban_ratio'].fillna(0)
        df['county_urban_ratio'] = (df['county_urban_4']-df['county_urban_3'])/(df['county_urban_2']-df['county_urban_1'])-1
        df['county_urban_ratio'] = df['county_urban_ratio'].fillna(0)
        df['levee_effect'] = df['levee_urban_ratio']-df['county_urban_ratio']
        df['levee_effect'].replace(np.inf, 999, inplace=True)
        df['levee_effect'].replace(-np.inf, -999, inplace=True)
        df.to_csv('watershed_levee_effect_%s.csv'%lev_colname,index=False)

	




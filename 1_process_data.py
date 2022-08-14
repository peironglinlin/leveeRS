import pandas as pd

if __name__=='__main__':
	# 加载systemId和COMID的对应关系，多对多，处理成1个systemId对应多个COMID
	df1 = pd.read_csv('data/COMID_systemID_intersection.csv')
	df1 = df1[['systemId','COMID','county_areasqkm','levee_areasqkm']].drop_duplicates()

	# 加载每个systemId的levee建造年份
	df2 = pd.read_csv('./data/P_systemID_year_0813.csv')
	df2 = df2[['systemId','Levee_year']].drop_duplicates()

	df = pd.merge(df1,df2,on='systemId')
	df = df.rename(columns={'county_areasqkm':'county_area','levee_areasqkm':'levee_area','Levee_year':'levee_year'})

	# 加载levee urban area %的数据
	df_levee = pd.read_csv('./data/USGS_urban_ts_by_leveearea.csv')
	# 将数据堆积成systemId|year|levee的格式
	df_levee = pd.melt(df_levee, id_vars=['systemId'], value_vars=[i for i in df_levee if i!='systemId'])
	df_levee = df_levee.rename(columns = {'variable':'year','value':'levee_urban_%'})
	df_levee['year'] = df_levee['year'].astype(int)
	df_levee['systemId'] = df_levee['systemId'].astype(int)

	# 加载county urban area %的数据
	df_county = pd.read_csv('./data/USGS_urban_ts_by_county.csv')
	# 将数据堆积成COMID|year|county的格式
	df_county = pd.melt(df_county, id_vars=['COMID'], value_vars=[i for i in df_county if i!='COMID'])
	df_county = df_county.rename(columns = {'variable':'year','value':'county_urban_%'})
	df_county['year'] = df_county['year'].astype(int)
	df_county['COMID'] = df_county['COMID'].astype(int)

	# merge levee_urban_%和county_urban_%
	df = pd.merge(df,df_levee,on='systemId',how='left')
	df = pd.merge(df,df_county,on=['COMID','year'],how='left')

	df['year_diff'] = df['year']-df['levee_year']
	df = df[(df.year_diff<=10) & (df.year_diff>=-10)]
	df['levee_urban'] = df['levee_area']*df['levee_urban_%']/100
	df['county_urban'] = df['county_area']*df['county_urban_%']/100

	df[['systemId', 'COMID', 'year', 'levee_year', 'year_diff', 
		'levee_area', 'county_area', 'levee_urban_%', 'county_urban_%', 
		'levee_urban', 'county_urban']].to_csv('processed_data/processed_levee_county.csv',index=False)

	####### 把每个systemId的信息合并
	df1 = df.groupby(['systemId','year','levee_year', 'year_diff'])['COMID'].apply(list).reset_index()
	df2 = df[['systemId', 'year', 'levee_year', 'year_diff',
			'levee_area', 'levee_urban_%', 'levee_urban']].drop_duplicates()
	df3 = df.groupby(['systemId','year','levee_year', 'year_diff'])[['county_area','county_urban']].apply(sum).reset_index()

	df = pd.merge(df1,df2,on=['systemId','year','levee_year', 'year_diff'])
	df = pd.merge(df,df3,on=['systemId','year','levee_year', 'year_diff'])
	df['county_urban_%'] = df['county_urban']/df['county_area']*100

	df[['systemId', 'COMID', 'year', 'levee_year', 'year_diff', 
		'levee_area', 'county_area', 'levee_urban_%', 'county_urban_%', 
		'levee_urban', 'county_urban']].to_csv('processed_data/processed_levee_county_combined.csv',index=False)




import pandas as pd 
from sklearn import linear_model
import matplotlib.pyplot as plt

def arg_parser():
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('-y','--year',dest='year_to_plot',default='0')
	return parser.parse_args()

argparser = arg_parser()
year_to_plot = int(argparser.year_to_plot)

def filter_levees(df_levee):
	df_levee = df_levee.pivot_table(index='year_diff',columns='systemId',values='levee')
	# 删掉全都是0的levee
	x = (df_levee!=0).any(axis=0)
	return x[x].index.tolist()

def load_levee_data():
	# read systemId - COMID map
	df_id = pd.read_csv('./data/summary_systemId_COMID.csv')
	# read levee area data
	df_levee = pd.read_csv('./data/USGS_urban_ts_by_leveearea.csv')
	# read county area data
	df_county = pd.read_csv('./data/USGS_urban_ts_by_county.csv')

	# 将数据堆积成systemId|year|levee的格式
	df_levee = pd.melt(df_levee, id_vars=['systemId'], value_vars=[i for i in df_levee if i!='systemId'])
	df_levee = df_levee.rename(columns = {'variable':'year','value':'levee'})
	df_levee['year'] = df_levee['year'].astype(int)
	df_levee['systemId'] = df_levee['systemId'].astype(int)

	# 将数据堆积成COMID|year|county的格式
	df_county = pd.melt(df_county, id_vars=['COMID'], value_vars=[i for i in df_county if i!='COMID'])
	df_county = df_county.rename(columns = {'variable':'year','value':'county'})
	df_county['year'] = df_county['year'].astype(int)
	df_county['COMID'] = df_county['COMID'].astype(int)

	# 加上yearCons
	df_levee = pd.merge(df_levee,df_id[['systemId','COMID','yearCons','areakm2','Area_km2']],on='systemId')
	df_levee = pd.merge(df_levee,df_county,on=['COMID','year'],how='left')
	df_levee['year_diff'] = df_levee['year']-df_levee['yearCons'].astype(int)
	df_levee['levee'] = df_levee['levee']*df_levee['areakm2']/100
	df_levee['county'] = df_levee['county']*df_levee['Area_km2']/100
	df_levee = df_levee[(df_levee.year_diff<=10) & (df_levee.year_diff>=-10)]

	# 删掉全都是0的levee
	levees_filtered = filter_levees(df_levee)
	df_levee = df_levee[df_levee.systemId.isin(levees_filtered)]

	# Save data
	df_levee[['systemId','COMID','year','yearCons','year_diff','levee','county']].to_csv('processed_levee_county.csv',index=False)

	if year_to_plot!=0:
		df_levee = df_levee[df_levee.yearCons==year_to_plot]

	# 计算所有systemID的levee和county的总和
	df_levee = df_levee.pivot_table(index='year_diff',columns='systemId',values=['levee','county'])
	
	# 把有空值的levee去掉
	df_levee.dropna(axis=1, how="any",inplace=True)
	df_levee['global_sum_levee'] = df_levee['levee'].sum(axis=1)
	df_levee['global_sum_county'] = df_levee['county'].sum(axis=1)
	df_levee['levee_urban_percent'] = df_levee['global_sum_levee']/df_levee['global_sum_county']*100.

	return df_levee[['levee_urban_percent','global_sum_county','global_sum_levee']].reset_index()

def plot_levee_effect_percent(df_levee):
	# 画图
	data = df_levee
	data_fit = data[data.year_diff<0]

	regr = linear_model.LinearRegression()
	regr.fit(data_fit[['year_diff']], data_fit['levee_urban_percent'])
	data['global_sum_predict'] = regr.predict(data[['year_diff']])

	### levee effect的计算
	data['levee_diff'] = (data['levee_urban_percent']-data['global_sum_predict'])*data['global_sum_county']/data['global_sum_levee']

	fig, axs = plt.subplots(2,figsize=(5,7))

	# 画protected area with levee
	axs[0].plot(data['year_diff'], data['levee_urban_percent'], color='red', linewidth=3,label='with levee effect')
	axs[0].scatter(data['year_diff'], data['levee_urban_percent'],alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	# 画protected area without levee
	axs[0].plot(data[data.year_diff<=0]['year_diff'], data[data.year_diff<=0]['global_sum_predict'], color='blue', linewidth=3, linestyle='dashed')
	axs[0].plot(data[data.year_diff>=0]['year_diff'], data[data.year_diff>=0]['global_sum_predict'], color='blue', linewidth=3,label='without levee effct')
	axs[0].plot([0,0], [data['global_sum_predict'].min(),data['global_sum_predict'].max()], color='grey', linewidth=3, linestyle='dashed')
	if year_to_plot!=0:
		axs[0].set_title('levee urban area / county urban area - %s'%year_to_plot)
	else:
		axs[0].set_title('levee urban area / county urban area')

	for i in range(1,11):
		if i==1:
			axs[0].plot([i,i], [data['global_sum_predict'][data.year_diff==i],data['levee_urban_percent'][data.year_diff==i]], color='green', linewidth=2, linestyle='dashed', label='"levee effect"')
		else:
			axs[0].plot([i,i], [data['global_sum_predict'][data.year_diff==i],data['levee_urban_percent'][data.year_diff==i]], color='green', linewidth=2, linestyle='dashed')

	axs[0].set_xticks(range(-10,12,2))
	axs[0].set_ylabel("%")

	axs[0].legend()

	# 画protected area with levee
	axs[1].plot(data['year_diff'], data['levee_diff'], color='red', linewidth=3,label='with levee effect')
	axs[1].scatter(data['year_diff'], data['levee_diff'],alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	axs[1].plot([0,0], [data['levee_diff'].min(),data['levee_diff'].max()], color='grey', linewidth=3, linestyle='dashed')
	axs[1].set_title('levee effect')

	axs[1].plot([data['year_diff'].min(),data['year_diff'].max()], [0,0], color='black', linewidth=1,linestyle='dashed')

	for i in range(1,11):
		if i==1:
			axs[1].plot([i,i], [0,data['levee_diff'][data.year_diff==i]], color='green', linewidth=2, linestyle='dashed', label='"levee effect"')
		else:
			axs[1].plot([i,i], [0,data['levee_diff'][data.year_diff==i]], color='green', linewidth=2, linestyle='dashed')

	axs[1].set_xticks(range(-10,12,2))
	axs[1].set_xlabel("levee construct year")
	axs[1].set_ylabel("%")

	plt.tight_layout()
	if year_to_plot!=0:
		plt.savefig('plots/levee_effect_by_year/%s.png'%year_to_plot,dpi=500)
	else:
		plt.savefig('plots/global_levee_urban_percentage.png',dpi=500)
	plt.close()

if __name__=='__main__':

	df_levee = load_levee_data()

	plot_levee_effect_percent(df_levee)


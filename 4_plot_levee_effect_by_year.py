import pandas as pd 
from sklearn import linear_model
import matplotlib.pyplot as plt
import numpy as np

def calc_levee_effect_m1(df):

	# 计算所有systemID的总和
	df = df.pivot_table(index='year_diff',columns='systemId',values=['levee_urban','county_urban'])
	df['levee_urban_sum'] = df['levee_urban'].sum(axis=1)
	df['county_urban_sum'] = df['county_urban'].sum(axis=1)
	df['levee_urban_percent'] = df['levee_urban_sum']/df['county_urban_sum']*100.

	df = df[['levee_urban_percent','county_urban_sum','levee_urban_sum']].reset_index()

	data_fit = df[df.year_diff<0]
	try:
		regr = linear_model.LinearRegression()
		regr.fit(data_fit[['year_diff']], data_fit['levee_urban_percent'])
		df['levee_urban_percent_predict'] = regr.predict(df[['year_diff']])

		### levee effect的计算
		df['levee_diff'] = (df['levee_urban_percent']-df['levee_urban_percent_predict'])*df['county_urban_sum']/df['levee_urban_sum']

		# 去levee建成后10年的平均
		return df['levee_diff'][df.year_diff>0].values.mean()
		# return df['levee_diff'][df.year_diff==10].values[0]
	except:
		return np.nan

def calc_levee_effect_m2(df):

	# 计算所有systemID的总和
	df = df.pivot_table(index='year_diff',columns='systemId',values=['levee_urban','county_urban'])
	df['levee_urban_sum'] = df['levee_urban'].sum(axis=1)
	df['county_urban_sum'] = df['county_urban'].sum(axis=1)

	df = df[['county_urban_sum','levee_urban_sum']].reset_index()

	try:
		return (df['levee_urban_sum'][df.year_diff>0].mean()/df['levee_urban_sum'][df.year_diff<0].mean() - \
						df['county_urban_sum'][df.year_diff>0].mean()/df['county_urban_sum'][df.year_diff<0].mean())*100
	except:
		return np.nan

if __name__=='__main__':
	df = pd.read_csv('processed_data/processed_levee_county_combined.csv')

	x = sorted(df.levee_year.unique().tolist())
	y = []

	for year in x:
		y.append(calc_levee_effect_m2(df[df.levee_year==year]))


	plt.plot(x, y, color='red', linewidth=3,label='levee effect')
	plt.scatter(x, y,alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	plt.plot([min(x),max(x)],[0,0], color='black', linewidth=2, linestyle='dashed')
	plt.xlabel('Year')
	plt.ylabel('%')
	plt.title('levee effect by year')
	plt.savefig('plots/4_levee_effect_by_year.png',dpi=500)
	plt.close()


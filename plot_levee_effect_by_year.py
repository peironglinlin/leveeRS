import pandas as pd 
from sklearn import linear_model
import matplotlib.pyplot as plt
import numpy as np

def calc_levee_effect(df_levee,year=10):

	df_levee = df_levee.pivot_table(index='year_diff',columns='systemId',values=['levee','county'])
	
	# 把有空值的levee去掉
	df_levee.dropna(axis=1, how="any",inplace=True)
	df_levee['global_sum_levee'] = df_levee['levee'].sum(axis=1)
	df_levee['global_sum_county'] = df_levee['county'].sum(axis=1)
	df_levee['levee_urban_percent'] = df_levee['global_sum_levee']/df_levee['global_sum_county']*100.

	df_levee = df_levee[['levee_urban_percent','global_sum_county','global_sum_levee']].reset_index()

	data_fit = df_levee[df_levee.year_diff<0]
	try:

		regr = linear_model.LinearRegression()
		regr.fit(data_fit[['year_diff']], data_fit['levee_urban_percent'])
		df_levee['global_sum_predict'] = regr.predict(df_levee[['year_diff']])

		### levee effect的计算
		df_levee['levee_diff'] = (df_levee['levee_urban_percent']-df_levee['global_sum_predict'])*df_levee['global_sum_county']/df_levee['global_sum_levee']

		return df_levee['levee_diff'][df_levee.year_diff==year].values[0]
	except:
		return np.nan

if __name__=='__main__':
	df = pd.read_csv('processed_levee_county.csv')

	x = sorted(df.yearCons.unique().tolist())
	y = []

	for year in x:
		y.append(calc_levee_effect(df[df.yearCons==year]))


	plt.plot(x, y, color='red', linewidth=3,label='levee effect')
	plt.scatter(x, y,alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	plt.plot([min(x),max(x)],[0,0], color='black', linewidth=2, linestyle='dashed')
	plt.xlabel('Year')
	plt.ylabel('%')
	plt.title('levee effect by year')
	plt.savefig('plots/levee_effect_by_year.png',dpi=500)
	plt.close()


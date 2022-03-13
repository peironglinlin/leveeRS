import pandas as pd 
from sklearn import linear_model
import matplotlib.pyplot as plt

def load_data():
	df = pd.read_csv('processed_data/processed_levee_county_combined.csv')

	# 计算所有systemID的总和
	df = df.pivot_table(index='year_diff',columns='systemId',values=['levee_urban','county_urban'])
	df['levee_urban_sum'] = df['levee_urban'].sum(axis=1)
	df['county_urban_sum'] = df['county_urban'].sum(axis=1)
	df['levee_urban_percent'] = df['levee_urban_sum']/df['county_urban_sum']*100.
	return df[['levee_urban_sum','county_urban_sum','levee_urban_percent']].reset_index()

def linear_predict(df):
	"""
	用 没有levee前的时间序列 [预测] 建造levee后的时间序列
	"""
	data_fit = df[df.year_diff<0]
	for c in ['levee_urban_percent']:
		regr = linear_model.LinearRegression()
		regr.fit(data_fit[['year_diff']], data_fit[c])
		df['%s_predict'%c] = regr.predict(df[['year_diff']])
	return df

def plot_levee_effect_percent(df):
	# 用 没有levee前的时间序列 [预测] 建造levee后的时间序列
	df = linear_predict(df)

	### levee effect的计算
	df['levee_diff'] = (df['levee_urban_percent']-df['levee_urban_percent_predict'])*df['county_urban_sum']/df['levee_urban_sum']

	fig, axs = plt.subplots(2,figsize=(5,7))

	# 画protected area with levee
	axs[0].plot(df['year_diff'], df['levee_urban_percent'], color='red', linewidth=3,label='with levee effect')
	axs[0].scatter(df['year_diff'], df['levee_urban_percent'],alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	# 画protected area without levee
	axs[0].plot(df[df.year_diff<=0]['year_diff'], df[df.year_diff<=0]['levee_urban_percent_predict'], color='blue', linewidth=3, linestyle='dashed')
	axs[0].plot(df[df.year_diff>=0]['year_diff'], df[df.year_diff>=0]['levee_urban_percent_predict'], color='blue', linewidth=3,label='without levee effct')
	axs[0].plot([0,0], [df['levee_urban_percent_predict'].min(),df['levee_urban_percent_predict'].max()], color='grey', linewidth=3, linestyle='dashed')
	axs[0].set_title('levee urban area / county urban area')

	for i in range(1,11):
		if i==1:
			axs[0].plot([i,i], [df['levee_urban_percent'][df.year_diff==i],df['levee_urban_percent_predict'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed', label='"levee effect"')
		else:
			axs[0].plot([i,i], [df['levee_urban_percent'][df.year_diff==i],df['levee_urban_percent_predict'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed')

	axs[0].set_xticks(range(-10,12,2))
	axs[0].set_ylabel("%")

	axs[0].legend()

	# 画protected area with levee
	axs[1].plot(df['year_diff'], df['levee_diff'], color='red', linewidth=3,label='with levee effect')
	axs[1].scatter(df['year_diff'], df['levee_diff'],alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	axs[1].plot([0,0], [df['levee_diff'].min(),df['levee_diff'].max()], color='grey', linewidth=3, linestyle='dashed')
	axs[1].set_title('levee effect')

	axs[1].plot([df['year_diff'].min(),df['year_diff'].max()], [0,0], color='black', linewidth=1,linestyle='dashed')

	for i in range(1,11):
		if i==1:
			axs[1].plot([i,i], [0,df['levee_diff'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed', label='"levee effect"')
		else:
			axs[1].plot([i,i], [0,df['levee_diff'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed')

	axs[1].set_xticks(range(-10,12,2))
	axs[1].set_xlabel("levee construct year")
	axs[1].set_ylabel("%")

	plt.tight_layout()
	plt.savefig('plots/3_global_levee_urban_percentage.png',dpi=500)
	plt.close()

if __name__=='__main__':

	df = load_data()

	plot_levee_effect_percent(df)


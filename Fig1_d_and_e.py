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

	fig, axs = plt.subplots(2,figsize=(18.3,9))

	# 画protected area with levee
	axs[0]=plt.subplot(121)
	axs[0].plot(df['year_diff'], df['levee_urban_percent'], color='red', linewidth=3,label='Observed')
	axs[0].scatter(df['year_diff'], df['levee_urban_percent'],alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	# 画protected area without levee
	axs[0].plot(df[df.year_diff<=0]['year_diff'], df[df.year_diff<=0]['levee_urban_percent_predict'], color='blue', linewidth=3, linestyle='dashed')
	axs[0].plot(df[df.year_diff>=0]['year_diff'], df[df.year_diff>=0]['levee_urban_percent_predict'], color='blue', linewidth=3,label='Predicted')
	axs[0].plot([0,0], [df['levee_urban_percent_predict'].min(),df['levee_urban_percent_predict'].max()], color='grey', linewidth=3, linestyle='dashed')
	axs[0].set_title('Urban area in levee protected floodplains as percentage of \n to urban area in counties', fontsize=20, pad=11)

	for i in range(1,11):
		if i==1:
			axs[0].plot([i,i], [df['levee_urban_percent'][df.year_diff==i],df['levee_urban_percent_predict'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed', label='Difference between observed and predicted')
		else:
			axs[0].plot([i,i], [df['levee_urban_percent'][df.year_diff==i],df['levee_urban_percent_predict'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed')

	axs[0].set_xticks(range(-10,12,2))
	axs[0].set_ylabel("%", fontsize=13)
	axs[0].tick_params(axis='x', labelsize=20)
	axs[0].tick_params(axis='y', labelsize=20)
	axs[0].legend(loc='lower center', bbox_to_anchor=(0.46, -0.3), ncol=1,fontsize=16, frameon=False)
	axs[0].tick_params(axis='x', colors='black',labelsize=20)
	axs[0].tick_params(axis='y', colors='black',labelsize=20)

	# 画protected area with levee
	axs[1]=plt.subplot(122)
	axs[1].plot(df['year_diff'], df['levee_diff'], color='tab:blue', linewidth=3,label='Percentage of urban expansion')
	axs[1].scatter(df['year_diff'], df['levee_diff'],alpha=0.5,marker='o',facecolors='none', edgecolors='tab:blue',linewidth=3)
	axs[1].plot([0,0], [df['levee_diff'].min(),df['levee_diff'].max()], color='grey', linewidth=3, linestyle='dashed')
	axs[1].set_title('Percentage of urban expansion in levee protected floodplains \n caused by levee construction', fontsize=20, pad=11)
	axs[1].plot([df['year_diff'].min(),df['year_diff'].max()], [0,0], color='black', linewidth=1,linestyle='dashed')

	for i in range(1,11):
		if i==1:
			axs[1].plot([i,i], [0,df['levee_diff'][df.year_diff==i]], color='tab:orange', linewidth=2, linestyle='dashed', label='"levee effect"')
		else:
			axs[1].plot([i,i], [0,df['levee_diff'][df.year_diff==i]], color='tab:orange', linewidth=2, linestyle='dashed')

	axs[1].set_xticks(range(-10,12,2))
	axs[1].set_ylabel("%", fontsize=13)
	axs[1].tick_params(axis='x', labelsize=20)
	axs[1].tick_params(axis='y', labelsize=20)
	axs[1].legend(loc='lower center', bbox_to_anchor=(0.48, -0.28), ncol=1,fontsize=16, frameon=False)
	axs[1].tick_params(axis='x', colors='black',labelsize=20)
	axs[1].tick_params(axis='y', colors='black',labelsize=20)
	plt.tight_layout()
	plt.show() 
	plt.savefig('plots/Fig1_d_and_e.png',dpi=500)
	#plt.close()

if __name__=='__main__':

	df = load_data()

	plot_levee_effect_percent(df)


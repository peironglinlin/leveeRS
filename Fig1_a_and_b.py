import pandas as pd 
from sklearn import linear_model
import matplotlib.pyplot as plt

def load_data():
	df = pd.read_csv('processed_data/processed_levee_county_combined.csv')

	# 计算所有systemID的总和
	df = df.pivot_table(index='year_diff',columns='systemId',values=['levee_urban','county_urban'])
	df['levee_urban_sum'] = df['levee_urban'].sum(axis=1)
	df['county_urban_sum'] = df['county_urban'].sum(axis=1)
	# df['county_urban_sum'] = df['county_urban_sum']-df['levee_urban_sum']
	return df[['levee_urban_sum','county_urban_sum']].reset_index()

def linear_predict(df):
	"""
	用 没有levee前的时间序列 [预测] 建造levee后的时间序列
	"""
	data_fit = df[df.year_diff<0]
	for c in ['levee_urban_sum','county_urban_sum']:
		regr = linear_model.LinearRegression()
		regr.fit(data_fit[['year_diff']], data_fit[c])
		df['%s_predict'%c] = regr.predict(df[['year_diff']])
	return df

def plot_levee_effect(df):
	# 用 没有levee前的时间序列 [预测] 建造levee后的时间序列
	df = linear_predict(df)

	fig, axs = plt.subplots(2,figsize=(16,7))

	# 画protected area with levee
	axs[0]=plt.subplot(121)
	axs[0].plot(df['year_diff'], df['levee_urban_sum'], color='red', linewidth=3,label='Observed')
	axs[0].scatter(df['year_diff'], df['levee_urban_sum'],alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	# 画protected area without levee
	axs[0].plot(df[df.year_diff<=0]['year_diff'], df[df.year_diff<=0]['levee_urban_sum_predict'], color='blue', linewidth=3, linestyle='dashed')
	axs[0].plot(df[df.year_diff>=0]['year_diff'], df[df.year_diff>=0]['levee_urban_sum_predict'], color='blue', linewidth=3,label='Predicted')
	axs[0].plot([0,0], [df['levee_urban_sum'].min(),df['levee_urban_sum'].max()], color='grey', linewidth=3, linestyle='dashed')
	axs[0].set_title('Urban expansion in all levee protected floodplains', fontsize=22, pad=11)
    

	for i in range(1,11):
		if i==1:
			axs[0].plot([i,i], [df['levee_urban_sum_predict'][df.year_diff==i],df['levee_urban_sum'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed', label='Difference between observed and predicted')
		else:
			axs[0].plot([i,i], [df['levee_urban_sum_predict'][df.year_diff==i],df['levee_urban_sum'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed')

	axs[0].set_xticks(range(-10,12,2))
	#axs[0].set_xlabel("Year constructed")
	axs[0].set_ylabel("Urban area ($km^2$)", fontsize=20)
    
	axs[0].tick_params(axis='x', labelsize=20)
	axs[0].tick_params(axis='y', labelsize=20)
	#axs[0].legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, fancybox=True, shadow=True)
	plt.text(1,3300,r"$\frac{K_{observed}}{K_{predicted}}$=1.36", fontsize=20)

	# 画county
	axs[1]=plt.subplot(122)
	axs[1].plot(df['year_diff'], df['county_urban_sum'], color='red', linewidth=3,label='Observed')
	axs[1].scatter(df['year_diff'], df['county_urban_sum'],alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	# 画protected area without levee
	axs[1].plot(df[df.year_diff<=0]['year_diff'], df[df.year_diff<=0]['county_urban_sum_predict'], color='blue', linewidth=3, linestyle='dashed')
	axs[1].plot(df[df.year_diff>=0]['year_diff'], df[df.year_diff>=0]['county_urban_sum_predict'], color='blue', linewidth=3,label='Predicted')
	axs[1].plot([0,0], [df['county_urban_sum'].min(),df['county_urban_sum'].max()], color='grey', linewidth=3, linestyle='dashed',label='${T_0}$')
	axs[1].set_title('Urban expansion in all counties', fontsize=22, pad=11)

	for i in range(1,11):
		if i==1:
			axs[1].plot([i,i], [df['county_urban_sum_predict'][df.year_diff==i],df['county_urban_sum'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed', label='Difference between observed and predicted')
		else:
			axs[1].plot([i,i], [df['county_urban_sum_predict'][df.year_diff==i],df['county_urban_sum'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed')

	axs[1].set_xticks(range(-10,12,2))
	#axs[1].set_xlabel("Before  After  ", fontsize=13)
	axs[1].set_ylabel("Urban area ($km^2$)", fontsize=20)
    
	axs[1].tick_params(axis='x', labelsize=20)
	axs[1].tick_params(axis='y', labelsize=20)

	plt.text(0.9,110000,r"$\frac{K_{observed}}{K_{predicted}}$=1.12", fontsize=20)
	plt.show()  
	plt.tight_layout() 
	plt.savefig('plots/Fig1_a_and_b.png',dpi=600)
	#plt.close()

if __name__=='__main__':

	df = load_data()

	plot_levee_effect(df)



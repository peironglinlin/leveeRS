import pandas as pd 
from sklearn import linear_model

import matplotlib
from matplotlib.backends.backend_pgf import FigureCanvasPgf
matplotlib.backend_bases.register_backend('pdf', FigureCanvasPgf)
import matplotlib.pyplot as plt

pgf_with_latex = {
    "text.usetex": True,            # use LaTeX to write all text
    "pgf.rcfonts": False,           # Ignore Matplotlibrc
    "pgf.preamble": [
        r'\usepackage{color}'     # xcolor for colours
    ]
}
matplotlib.rcParams.update(pgf_with_latex)

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
	for c in ['levee_urban_sum','levee_urban_sum_predict','county_urban_sum','county_urban_sum_predict']:
		df[c] = df[c]/1000

	# x轴的显示值
	xticks = [str(i) for i in range(-10,11,2)]
	xticks[5]='T0'

	fig, axs = plt.subplots(2,figsize=(16,7))

	# 画protected area with levee
	axs[0]=plt.subplot(121)
	axs[0].plot(df['year_diff'], df['levee_urban_sum'], color='red', linewidth=3,label='Observed')
	axs[0].scatter(df['year_diff'], df['levee_urban_sum'],alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	# 画protected area without levee
	axs[0].plot(df[df.year_diff<=0]['year_diff'], df[df.year_diff<=0]['levee_urban_sum_predict'], color='blue', linewidth=3, linestyle='dashed')
	axs[0].plot(df[df.year_diff>=0]['year_diff'], df[df.year_diff>=0]['levee_urban_sum_predict'], color='blue', linewidth=3,label='Predicted')
	axs[0].axvline(x=0, color='grey', linewidth=3,alpha=0.2)
	axs[0].set_title('Urban expansion in all levee protected floodplains', fontsize=22, pad=11)

	# axs[0].fill_between(df[df.year_diff>=0]['year_diff'], df[df.year_diff>=0]['levee_urban_sum_predict'], df[df.year_diff>=0]['levee_urban_sum'],
 #                 facecolor='green', alpha=0.5, interpolate=True)
	axs[0].axvspan(-11, 0, facecolor='green', alpha=0.2)
	axs[0].axvspan(0, 11, facecolor='yellow', alpha=0.2)
	axs[0].set_xlim(-11, 11)
	axs[0].set_xticks([i for i in range(-10,11,2)])
	axs[0].set_xticklabels(xticks)
    

	for i in range(1,11):
		if i==1:
			axs[0].plot([i,i], [df['levee_urban_sum_predict'][df.year_diff==i],df['levee_urban_sum'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed', label='Difference between observed and predicted')
		else:
			axs[0].plot([i,i], [df['levee_urban_sum_predict'][df.year_diff==i],df['levee_urban_sum'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed')

	axs[0].set_xticks(range(-10,12,2))
	#axs[0].set_xlabel("Year constructed")
	axs[0].set_ylabel("Urban area ($10^3$$km^2$)", fontsize=20)
    
	axs[0].tick_params(axis='x', labelsize=20)
	axs[0].tick_params(axis='y', labelsize=20)
	#axs[0].legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, fancybox=True, shadow=True)
	# axs[0].text(1,3.3,r"\frac{K_{observed}}{K_{predicted}}=1.36", fontsize=20))
	# 这里微调公式
	axs[0].text(1.3,3.3,r"$K_{observed}$", fontsize=15,color='red',horizontalalignment='center')
	axs[0].text(1.3,3.25,r"$K_{predicted}$", fontsize=15,color='blue',horizontalalignment='center')
	axs[0].plot([0.2,2.4],[3.28,3.28],color='black')
	axs[0].text(2.5,3.27,r"=1.36", fontsize=15,color='black',horizontalalignment='left')
	axs[0].text(0,2.65,"construction year", fontsize=15,horizontalalignment='center',color='blue')
	axs[0].arrow(0,2.6,0,-0.08,head_width=0.3, head_length=0.03, linewidth=4,color='blue')


	# 画county
	axs[1]=plt.subplot(122)
	axs[1].plot(df['year_diff'], df['county_urban_sum'], color='red', linewidth=3,label='Observed')
	axs[1].scatter(df['year_diff'], df['county_urban_sum'],alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	# 画protected area without levee
	axs[1].plot(df[df.year_diff<=0]['year_diff'], df[df.year_diff<=0]['county_urban_sum_predict'], color='blue', linewidth=3, linestyle='dashed')
	axs[1].plot(df[df.year_diff>=0]['year_diff'], df[df.year_diff>=0]['county_urban_sum_predict'], color='blue', linewidth=3,label='Predicted')
	axs[0].axvline(x=0, color='grey', linewidth=3,alpha=0.2)
	axs[1].set_title('Urban expansion in all counties', fontsize=22, pad=11)

	# axs[1].fill_between(df[df.year_diff>=0]['year_diff'], df[df.year_diff>=0]['county_urban_sum_predict'], df[df.year_diff>=0]['county_urban_sum'],
 #                 facecolor='green', alpha=0.5, interpolate=True)
	axs[1].axvspan(-11, 0, facecolor='green', alpha=0.2)
	axs[1].axvspan(0, 11, facecolor='yellow', alpha=0.2)
	axs[1].set_xlim(-11, 11)
	axs[1].set_xticks([i for i in range(-10,11,2)])
	axs[1].set_xticklabels(xticks)

	for i in range(1,11):
		if i==1:
			axs[1].plot([i,i], [df['county_urban_sum_predict'][df.year_diff==i],df['county_urban_sum'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed', label='Difference between observed and predicted')
		else:
			axs[1].plot([i,i], [df['county_urban_sum_predict'][df.year_diff==i],df['county_urban_sum'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed')

	axs[1].set_xticks(range(-10,12,2))
	#axs[1].set_xlabel("Before  After  ", fontsize=13)
	axs[1].set_ylabel("Urban area ($10^3$$km^2$)", fontsize=20)
    
	axs[1].tick_params(axis='x', labelsize=20)
	axs[1].tick_params(axis='y', labelsize=20)

	# plt.text(0.9,110,r"$\frac{K_{observed}}{K_{predicted}}$=1.12", fontsize=20)
	# 这里微调公式
	axs[1].text(1.3,110.8,r"$K_{observed}$", fontsize=15,color='red',horizontalalignment='center')
	axs[1].text(1.3,109,r"$K_{predicted}$", fontsize=15,color='blue',horizontalalignment='center')
	axs[1].plot([0.2,2.4],[110,110],color='black')
	axs[1].text(2.5,109.8,r"=1.12", fontsize=15,color='black',horizontalalignment='left')
	axs[1].text(0,89,"construction year", fontsize=15,horizontalalignment='center',color='blue')
	axs[1].arrow(0,87,0,-3,head_width=0.3, head_length=1, linewidth=4,color='blue')

	# plt.show()  
	plt.tight_layout() 
	plt.savefig('plots/Fig1_a_and_b.pdf')
	plt.close()

if __name__=='__main__':

	df = load_data()

	plot_levee_effect(df)



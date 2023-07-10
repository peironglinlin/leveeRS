import pandas as pd 
from sklearn import linear_model

import matplotlib
from matplotlib.backends.backend_pgf import FigureCanvasPgf
matplotlib.backend_bases.register_backend('pdf', FigureCanvasPgf)
import matplotlib.pyplot as plt

pgf_with_latex = {
    "text.usetex": True,            # use LaTeX to write all text
    "pgf.rcfonts": True,           # Ignore Matplotlibrc
    "pgf.preamble": [
        r'\usepackage{color}'     # xcolor for colours
    ],
    'font.family':"sans-serif",
    'font.sans-serif': 'Arial'
}
matplotlib.rcParams.update(pgf_with_latex)

def load_data():
	df = pd.read_csv('processed_data/processed_levee_county_combined.csv')

	# Calculate sum of all systemID
	df = df.pivot_table(index='year_diff',columns='systemId',values=['levee_urban','county_urban'])
	df['levee_urban_sum'] = df['levee_urban'].sum(axis=1)
	df['county_urban_sum'] = df['county_urban'].sum(axis=1)
	# df['county_urban_sum'] = df['county_urban_sum']-df['levee_urban_sum']
	return df[['levee_urban_sum','county_urban_sum']].reset_index()

def linear_predict(df):
	"""
	Estimate the time series after levee construction using the time series before no levee
	"""
	data_fit = df[df.year_diff<0]
	for c in ['levee_urban_sum','county_urban_sum']:
		regr = linear_model.LinearRegression()
		regr.fit(data_fit[['year_diff']], data_fit[c])
		df['%s_predict'%c] = regr.predict(df[['year_diff']])
	return df

def slope_ratio(df,name='levee'):
	"""
	Estimate the time series after levee construction using the time series before no levee
	"""
	df1 = df[df.year_diff<0]
	df2 = df[df.year_diff>0]

	regr = linear_model.LinearRegression()
	regr.fit(df1[['year_diff']], df1['%s_urban_sum'%name])
	s1 = regr.coef_
	regr = linear_model.LinearRegression()
	regr.fit(df2[['year_diff']], df2['%s_urban_sum'%name])
	s2 = regr.coef_
		
	return s2/s1

def plot_levee_effect(df):
	# Estimate the time series after levee construction using the time series before no levee
	df = linear_predict(df)
	for c in ['levee_urban_sum','levee_urban_sum_predict','county_urban_sum','county_urban_sum_predict']:
		df[c] = df[c]/1000

	# Value on x axis
	xticks = [str(i) for i in range(-10,11,2)]
	xticks[5]='T0'

	fig, axs = plt.subplots(2,figsize=(16,5))

	# Draw protected area with levee
	axs[0]=plt.subplot(121)
	axs[0].plot(df['year_diff'], df['levee_urban_sum'], color='red', linewidth=3,label='Observed')
	axs[0].scatter(df['year_diff'], df['levee_urban_sum'],alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	# Draw protected area without levee
	axs[0].plot(df[df.year_diff<=0]['year_diff'], df[df.year_diff<=0]['levee_urban_sum_predict'], color='blue', linewidth=3, linestyle='dashed')
	axs[0].plot(df[df.year_diff>=0]['year_diff'], df[df.year_diff>=0]['levee_urban_sum_predict'], color='blue', linewidth=3,label='Predicted')
	axs[0].axvline(x=0, color='grey', linewidth=3,alpha=0.2)
	axs[0].set_title('Urban expansion in levee-protected floodplains', fontsize=25,fontname="Arial", pad=11)

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
	axs[0].set_ylabel("Urban area ($10^3$$km^2$)", fontsize=25)
    
	axs[0].tick_params(axis='x', labelsize=20)
	axs[0].tick_params(axis='y', labelsize=20)
	#axs[0].legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, fancybox=True, shadow=True)
	# axs[0].text(1,3.3,r"\frac{K_{observed}}{K_{predicted}}=1.36", fontsize=20))
	# Better visualization
	axs[0].text(-6,3.62,r"$k_{p}$$(observed)$", fontsize=25,color='red',horizontalalignment='center')
	axs[0].text(-6,3.42,r"$k_{p}$$(predicted)$", fontsize=25,color='blue',horizontalalignment='center')
	axs[0].plot([-9,-3.2],[3.56,3.56],color='black')
	axs[0].text(-2.7,3.5,r'=%.2f'%slope_ratio(df,name='levee'), fontsize=25,color='black',horizontalalignment='left')
	axs[0].text(0,2.65,"levee construction year", fontsize=25,horizontalalignment='center',color='blue')
	axs[0].arrow(0,2.6,0,-0.08,head_width=0.3, head_length=0.03, linewidth=4,color='blue')


	# Draw county
	axs[1]=plt.subplot(122)
	axs[1].plot(df['year_diff'], df['county_urban_sum'], color='red', linewidth=3,label='Observed')
	axs[1].scatter(df['year_diff'], df['county_urban_sum'],alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	# Draw protected area without levee
	axs[1].plot(df[df.year_diff<=0]['year_diff'], df[df.year_diff<=0]['county_urban_sum_predict'], color='blue', linewidth=3, linestyle='dashed')
	axs[1].plot(df[df.year_diff>=0]['year_diff'], df[df.year_diff>=0]['county_urban_sum_predict'], color='blue', linewidth=3,label='Predicted')
	axs[1].axvline(x=0, color='grey', linewidth=3,alpha=0.2)
	axs[1].set_title('Urban expansion in counties', fontsize=25, fontname="Arial", pad=11)

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
	axs[1].set_ylabel("Urban area ($10^3$$km^2$)", fontsize=25)
    
	axs[1].tick_params(axis='x', labelsize=20)
	axs[1].tick_params(axis='y', labelsize=20)

	# plt.text(0.9,110,r"$\frac{K_{observed}}{K_{predicted}}$=1.12", fontsize=20)
	# Better visualization
	axs[1].text(-6,120.5,r"$k_{c}$$(observed)$", fontsize=25,color='red',horizontalalignment='center')
	axs[1].text(-6,114.5,r"$k_{c}$$(predicted)$", fontsize=25,color='blue',horizontalalignment='center')
	axs[1].plot([-9,-3.2],[118.8,118.8],color='black')
	axs[1].text(-2.7,117,r'=%.2f'%slope_ratio(df,name='county'), fontsize=25,color='black',horizontalalignment='left')
	axs[1].text(0,88,"levee construction year", fontsize=25,horizontalalignment='center',color='blue')
	axs[1].arrow(0,86,0,-3,head_width=0.3, head_length=1, linewidth=4,color='blue')

	#plt.show()  
	plt.tight_layout(pad=3) 
	plt.savefig('plots/Fig1_a_and_b.pdf', dpi=600)

if __name__=='__main__':

	df = load_data()

	plot_levee_effect(df)



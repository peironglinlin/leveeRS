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

	# Calculate the sum of all systemID
	df = df.pivot_table(index='year_diff',columns='systemId',values=['levee_urban','county_urban'])
	df['levee_urban_sum'] = df['levee_urban'].sum(axis=1)
	df['county_urban_sum'] = df['county_urban'].sum(axis=1)
	df['levee_urban_percent'] = df['levee_urban_sum']/df['county_urban_sum']*100.
	return df[['levee_urban_sum','county_urban_sum','levee_urban_percent']].reset_index()

def linear_predict(df):
	"""
	Estimate the time series after levee construction using the time series before no levee
	"""
	data_fit = df[df.year_diff<0]
	for c in ['levee_urban_percent']:
		regr = linear_model.LinearRegression()
		regr.fit(data_fit[['year_diff']], data_fit[c])
		df['%s_predict'%c] = regr.predict(df[['year_diff']])
	return df

def plot_levee_effect_percent(df):
	# Estimate the time series after levee construction using the time series before no levee
	df = linear_predict(df)

	### Calculation of levee effect
	df['levee_diff'] = (df['levee_urban_percent']-df['levee_urban_percent_predict'])*df['county_urban_sum']/df['levee_urban_sum']

	# Value on x axis
	xticks = [str(i) for i in range(-10,11,2)]
	xticks[5]='T0'

	fig, axs = plt.subplots(2,figsize=(16,7.5))

	# Draw protected area with levee
	axs[0]=plt.subplot(121)
	axs[0].plot(df['year_diff'], df['levee_urban_percent'], color='red', linewidth=3,label='Observed')
	axs[0].scatter(df['year_diff'], df['levee_urban_percent'],alpha=0.5,marker='o',facecolors='none', edgecolors='red',linewidth=3)
	# Draw protected area without levee
	axs[0].plot(df[df.year_diff<=0]['year_diff'], df[df.year_diff<=0]['levee_urban_percent_predict'], color='blue', linewidth=3, linestyle='dashed')
	axs[0].plot(df[df.year_diff>=0]['year_diff'], df[df.year_diff>=0]['levee_urban_percent_predict'], color='blue', linewidth=3,label='Predicted')
	# axs[0].plot([0,0], [df['levee_urban_percent_predict'].min(),df['levee_urban_percent_predict'].max()], color='grey', linewidth=3, linestyle='dashed')
	# axs[0].set_title(r"$\frac{U_{p}}{U_{c}}$", fontsize=25, pad=11)
	axs[0].set_title(r"${U_{p}}/{U_{c}}$ ratio", fontsize=25, pad=11)

	axs[0].axvspan(-11, 0, facecolor='green', alpha=0.2)
	axs[0].axvspan(0, 11, facecolor='yellow', alpha=0.2)
	axs[0].axvline(x=0, color='grey', linewidth=3,alpha=0.2)
	axs[0].set_xlim(-11, 11)
	axs[0].set_ylim(2.8, 3.2)
	axs[0].set_xticks([i for i in range(-10,11,2)])
	axs[0].set_xticklabels(xticks)
	axs[0].text(0,2.87,"levee construction year", fontsize=25,horizontalalignment='center',color='blue')
	axs[0].arrow(0,2.86,0,-0.03,head_width=0.3, head_length=0.01, linewidth=4,color='blue')
	axs[0].text(-14.5,3.21,"a", fontsize=28,color='black', fontname='Arial')

	for i in range(1,11):
		if i==1:
			axs[0].plot([i,i], [df['levee_urban_percent'][df.year_diff==i],df['levee_urban_percent_predict'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed', label='Difference')
		else:
			axs[0].plot([i,i], [df['levee_urban_percent'][df.year_diff==i],df['levee_urban_percent_predict'][df.year_diff==i]], color='green', linewidth=2, linestyle='dashed')

	axs[0].set_xticks(range(-10,12,2))
	axs[0].set_ylabel('%', fontsize=20, loc="top",fontname='Arial')
	axs[0].tick_params(axis='x', labelsize=20)
	axs[0].tick_params(axis='y', labelsize=20)
	axs[0].legend(fontsize=25)
	# axs[0].legend(loc='lower center', bbox_to_anchor=(0.46, -0.3), ncol=1,fontsize=16, frameon=False)
	axs[0].tick_params(axis='x', colors='black',labelsize=20)
	axs[0].tick_params(axis='y', colors='black',labelsize=20)

	# Draw protected area with levee
	axs[1]=plt.subplot(122)
	axs[1].plot(df['year_diff'], df['levee_diff'], color='tab:blue', linewidth=3,label='urban expansion rate')
	axs[1].scatter(df['year_diff'], df['levee_diff'],alpha=0.5,marker='o',facecolors='none', edgecolors='tab:blue',linewidth=3)
	# axs[1].plot([0,0], [df['levee_diff'].min(),df['levee_diff'].max()], color='grey', linewidth=3, linestyle='dashed')
	axs[1].set_title('Percentage change in floodplain urban area', fontsize=25, pad=11)
	axs[1].plot([df['year_diff'].min(),df['year_diff'].max()], [0,0], color='black', linewidth=1,linestyle='dashed')

	axs[1].axvspan(-11, 0, facecolor='green', alpha=0.2)
	axs[1].axvspan(0, 11, facecolor='yellow', alpha=0.2)
	axs[1].axvline(x=0, color='grey', linewidth=3,alpha=0.2)
	axs[1].set_xlim(-11, 11)
	axs[1].set_ylim(-0.2, 5.2)
	axs[1].set_xticks([i for i in range(-10,11,2)])
	axs[1].set_xticklabels(xticks, fontname='Arial')
	axs[1].text(0,2.8,"levee construction year", fontsize=25,horizontalalignment='center',color='blue', fontname='Arial')
	axs[1].arrow(0,2.65,0,-0.5,head_width=0.3, head_length=0.1, linewidth=4,color='blue')
	axs[1].text(-13.7,5.3,"b", fontsize=28,color='black', fontname='Arial')

	for i in range(1,11):
		if i==1:
			axs[1].plot([i,i], [0,df['levee_diff'][df.year_diff==i]], color='tab:orange', linewidth=2, linestyle='dashed', label='"levee effect"')
		else:
			axs[1].plot([i,i], [0,df['levee_diff'][df.year_diff==i]], color='tab:orange', linewidth=2, linestyle='dashed')

	axs[1].set_xticks(range(-10,12,2))
	axs[1].set_ylabel("%", fontsize=20, loc="top",fontname='Arial')
	axs[1].tick_params(axis='x', labelsize=20)
	axs[1].tick_params(axis='y', labelsize=20)
	axs[1].legend(fontsize=25)
	# axs[1].legend(loc='lower center', bbox_to_anchor=(0.48, -0.28), ncol=1,fontsize=16, frameon=False)
	axs[1].tick_params(axis='x', colors='black',labelsize=20)
	axs[1].tick_params(axis='y', colors='black',labelsize=20)
	plt.tight_layout(pad=3)
	plt.savefig('plots/FigS4.pdf', dpi=600)
	#plt.close()

if __name__=='__main__':

	df = load_data()

	plot_levee_effect_percent(df)

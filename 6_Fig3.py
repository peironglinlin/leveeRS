import pandas as pd 
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
plt.switch_backend('agg')

# matplotlib.rcParams['font.sans-serif'] = "Arial"
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['font.sans-serif'] = "Arial"

if __name__=='__main__':
	list_df = []
	mark_years = [1968,1973,1977,1982]
	for i in range(3,11,2):
		df = pd.read_csv('processed_data/cons_year_levee_effect_%syr_regr.csv'%i)
		df['levee_effect'] = (df['k_levee_2']/df['k_levee_1']-1) - (df['k_county_2']/df['k_county_1']-1)
		df['method'] = i
		df['sig'] = 0
		df.loc[(df['p_levee_1']<0.05)&(df['p_levee_2']<0.05)&(df['p_county_1']<0.05)&(df['p_county_2']<0.05),'sig'] = 1
		list_df.append(df[['Levee_year','levee_effect','method','sig']])

	df = pd.concat(list_df)

	x_sig = df[df.sig==1]['Levee_year'].values
	y_sig = df[df.sig==1]['method'].values

	df = df.pivot(index='method', columns='Levee_year', values='levee_effect')
	# df = df.reindex(index=df.index[::-1])

	x = np.arange(1947.5,1996.5)
	y = np.arange(2,12,2)

	levels = matplotlib.ticker.MaxNLocator(nbins=20).tick_values(-2, 2)
	# https://matplotlib.org/stable/tutorials/colors/colormaps.html
	cmap = plt.colormaps['seismic']
	norm = matplotlib.colors.BoundaryNorm(levels, ncolors=cmap.N, clip=True)
	
	fig, ax = plt.subplots(figsize=(9,4))
	c = ax.pcolormesh(x, y, df.values, cmap=cmap, norm=norm)
	ax.set_yticks([i for i in range(3,11,2)])
	ax.set_yticklabels([str(i)+'-yr composite' for i in range(3,11,2)])
	ax.set_ylim(2,10)

	# for yr in mark_years:
	# 	ax.axvline(yr, color='green', lw=4, alpha=0.8)
	ax.plot(mark_years,[1.8]*4, marker="^",color='red',linestyle = 'None',markersize=10,clip_on=False)
	# ax.plot(x_sig, y_sig, 'o', color='green')
	levels2=('-2','-1.8','-1.6','-1.4','-1.2','-1','-0.8','-0.6','-0.4','-0.2','0.0','0.2','0.4','0.6','0.8','1','1.2','1.4','1.6','1.8','2')
	fig.colorbar(c, ax=ax).set_ticklabels(levels2,fontname="Arial")
	# plt.title('levee effect as a function of levee construction year')
	
	plt.tight_layout()
	plt.savefig('plots/Fig3.pdf')



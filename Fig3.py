import pandas as pd 
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

if __name__=='__main__':
	list_df = []
	for i in range(3,11,2):
		df = pd.read_csv('processed_data/cons_year_levee_effect_%syr.csv'%i)
		df['method'] = i
		list_df.append(df[['Levee_year','levee_effect','method']])

	df = pd.concat(list_df)
	df = df.pivot(index='method', columns='Levee_year', values='levee_effect')
	df = df.reindex(index=df.index[::-1])

	x = np.arange(1947.5,1996.5)
	y = np.arange(2,12,2)

	levels = matplotlib.ticker.MaxNLocator(nbins=20).tick_values(-2, 2)
	# https://matplotlib.org/stable/tutorials/colors/colormaps.html
	cmap = plt.colormaps['seismic']
	norm = matplotlib.colors.BoundaryNorm(levels, ncolors=cmap.N, clip=True)
	
	fig, ax = plt.subplots(figsize=(10,3))
	c = ax.pcolormesh(x, y, df.values, cmap=cmap, norm=norm)
	ax.set_yticks([i for i in range(3,11,2)])
	ax.set_yticklabels([str(i)+' years composite' for i in range(3,11,2)])
	fig.colorbar(c, ax=ax)
	plt.title('levee effect as a function of levee construction year')
	plt.tight_layout()
	plt.savefig('plots/Fig3.pdf')



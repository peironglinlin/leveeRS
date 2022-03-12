import pandas as pd 
from sklearn import linear_model
import matplotlib.pyplot as plt

from plot_global_levee import load_data,plot_levee_effect

def resample():
	"""
	Resample systemID to make # of levees for each construct year uniform
	Return a list of systemId
	"""
	# read systemId - COMID map
	df_id = pd.read_csv('./data/P_systemID_year_Meng_0312.csv')

	list_df = []
	for y in df_id.Levee_year.unique():
		df0 = df_id[df_id.Levee_year==y].sample(n=25, random_state=111,replace=True)
		list_df.append(df0)

	# Resample
	df = pd.concat(list_df)

	plt.hist(df['Levee_year'], len(df['Levee_year'].unique()), density=False, facecolor='g', alpha=0.75,edgecolor='white')
	plt.title('levee construct year (Total %s levees)'%len(df))
	plt.xlabel("Year")
	plt.ylabel("# of Levees")

	plt.savefig('plots/yearConst_resampled_hist.png',dpi=500)

	return df.systemId.tolist()

if __name__=='__main__':
	ids_sampled = resample()

	df_levee = load_data()
	df_levee['global_sum'] = df_levee[ids_sampled].sum(axis=1)

	plot_levee_effect(df_levee,name='global_resampled',title='Global Levee Protected Area (Resampled)')

import pandas as pd 
from sklearn import linear_model
import matplotlib.pyplot as plt

if __name__ == '__main__':
	# read systemId - COMID map
	df = pd.read_csv('./data/P_systemID_year_Meng_0312.csv')

	plt.hist(df['Levee_year'], len(df['Levee_year'].unique()), density=False, facecolor='g', alpha=0.75,edgecolor='white')
	plt.title('levee construct year (Total %s levees)'%len(df))
	plt.xlabel("Year")
	plt.ylabel("# of Levees")

	plt.savefig('plots/yearConst_hist.png',dpi=500)

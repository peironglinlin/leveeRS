import pandas as pd 
from sklearn import linear_model
import matplotlib.pyplot as plt
import numpy as np

def calc_levee_effect_m1(df):
	try:
		return (df['levee_urban'][df.year_diff>0].mean()/df['levee_urban'][df.year_diff<0].mean() - \
						df['county_urban'][df.year_diff>0].mean()/df['county_urban'][df.year_diff<0].mean())*100
	except:
		return np.nan

if __name__=='__main__':
	df = pd.read_csv('processed_data/processed_levee_county_combined.csv')

	x = df.groupby('systemId').apply(calc_levee_effect_m1)
	x = x.reset_index()
	x.columns = ['systemId','levee_effect']

	df1 = pd.read_csv('data/COMID_systemID_intersection.csv')
	df1 = df1[['systemId','levee_areasqkm']].drop_duplicates()

	x = pd.merge(x,df1,on='systemId',how='left')
	x.to_csv('processed_data/5_levee_effect_foreach.csv',index=False)

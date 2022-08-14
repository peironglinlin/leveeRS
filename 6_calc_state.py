import pandas as pd
import numpy as np

states = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}

if __name__=='__main__':
	df = pd.read_csv('processed_data/processed_levee_county_combined.csv')

	# 计算全国的levee ratio
	x1 = df[df['year_diff'].isin([-10,-9,-8,-7,-6])][['levee_urban','county_urban']].mean()
	x2 = df[df['year_diff'].isin([-5,-4,-3,-2,-1])][['levee_urban','county_urban']].mean()
	x3 = df[df['year_diff'].isin([1,2,3,4,5])][['levee_urban','county_urban']].mean()
	x4 = df[df['year_diff'].isin([6,7,8,9,10])][['levee_urban','county_urban']].mean()
	x = (x4-x3)/(x2-x1)
	us_levee_effect = x['levee_urban']-x['county_urban']
	print("us levee = %s"%us_levee_effect)

	df1 = pd.read_csv('data/ID_link_systemId_STATE1.csv')
	df1 = df1[['systemId','STATE']].drop_duplicates()

	df = pd.merge(df,df1,on=['systemId'],how='left')
	df['STATE'] = df['STATE'].fillna('None')
	df = df.groupby(['year_diff','STATE'])[['levee_urban','county_urban']].apply(np.sum).reset_index()
	df.to_csv('state_urban.csv',index=False)

	df1 = df[df['year_diff'].isin([-10,-9,-8,-7,-6])].groupby('STATE')[['levee_urban','county_urban']]\
			.apply(np.mean).reset_index()\
			.rename(columns={'levee_urban':'levee_urban_1','county_urban':'county_urban_1'})
	df2 = df[df['year_diff'].isin([-5,-4,-3,-2,-1])].groupby('STATE')[['levee_urban','county_urban']]\
			.apply(np.mean).reset_index()\
			.rename(columns={'levee_urban':'levee_urban_2','county_urban':'county_urban_2'})
	df3 = df[df['year_diff'].isin([1,2,3,4,5])].groupby('STATE')[['levee_urban','county_urban']]\
			.apply(np.mean).reset_index()\
			.rename(columns={'levee_urban':'levee_urban_3','county_urban':'county_urban_3'})
	df4 = df[df['year_diff'].isin([6,7,8,9,10])].groupby('STATE')[['levee_urban','county_urban']]\
			.apply(np.mean).reset_index()\
			.rename(columns={'levee_urban':'levee_urban_4','county_urban':'county_urban_4'})
	
	df = df1.merge(df2,on='STATE').merge(df3,on='STATE').merge(df4,on='STATE')

	df['levee_urban_ratio'] = (df['levee_urban_4']-df['levee_urban_3'])/(df['levee_urban_2']-df['levee_urban_1'])-1
	df['levee_urban_ratio'] = df['levee_urban_ratio'].fillna(0)
	df['county_urban_ratio'] = (df['county_urban_4']-df['county_urban_3'])/(df['county_urban_2']-df['county_urban_1'])-1
	df['county_urban_ratio'] = df['county_urban_ratio'].fillna(0)
	df['levee_effect'] = df['levee_urban_ratio']-df['county_urban_ratio']
	df['levee_effect'].replace(np.inf, 999, inplace=True)
	df['levee_effect'].replace(-np.inf, -999, inplace=True)
	df['state'] = df['STATE'].map(states)
	df.to_csv('state_levee_effect.csv',index=False)

	




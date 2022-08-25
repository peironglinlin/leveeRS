import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import LinearSegmentedColormap
plt.switch_backend('agg')

# matplotlib.rcParams['font.sans-serif'] = "Arial"
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['font.sans-serif'] = "Arial"

fig,ax = plt.subplots(3,2,figsize=(12,12))
markersize = [6,4,3,2]
cmap = LinearSegmentedColormap.from_list('mycmap', [(0, 'lightblue'), (1, 'gold'),(2,'orange'),(3,'salmon'),(4,'red')])

levels = matplotlib.ticker.MaxNLocator(nbins=20).tick_values(-2, 2)
# https://matplotlib.org/stable/tutorials/colors/colormaps.html
cmap = plt.colormaps['seismic']
norm = matplotlib.colors.BoundaryNorm(levels, ncolors=cmap.N, clip=True)
colors = matplotlib.cm.seismic(np.linspace(0, 1, 20))

# 去掉所有图的axis
for i in ax.flat:
	i.axis('off')

ax[2][1].scatter([0.3],[10],color=colors[18],label=r"$e_{s}$>1")
ax[2][1].scatter([0.3],[10],color=colors[15],label=r"$e_{s}$>=0.5")
ax[2][1].scatter([0.3],[10],color=colors[13],label=r"$e_{s}$>=0.3")
ax[2][1].scatter([0.3],[10],color=colors[11],label=r"$e_{s}$>=0")
ax[2][1].scatter([0.3],[10],color=colors[7],label=r"$e_{s}$<0")
ax[2][1].scatter([0.3],[10],color=colors[9],label='NA')

ax[2][1].set_xlim(0,1)
ax[2][1].set_ylim(0,1)
ax[2][1].legend(loc='center',frameon=False, prop={'size': 20})

def plot_state(ax=ax):
	dff = pd.read_csv('processed_data/state_levee_effect_regr.csv')

	#calculate levee effect
	dff['levee_effect'] = (dff['k_levee_2']/dff['k_levee_1']-1) - (dff['k_county_2']/dff['k_county_1']-1)
	dff['sig'] = 0
	dff.loc[(dff['p_levee_1']<0.05)&(dff['p_levee_2']<0.05)&(dff['p_county_1']<0.05)&(dff['p_county_2']<0.05),'sig'] = 1


	dff = dff[['STATE','levee_effect','sig']]
	dff.rename(columns={'levee_effect':'ratio'},inplace=True)
	#geodataframe
	df0 = gpd.read_file('data/States/States.shp')
	df0.rename(columns={'STUSPS':'STATE'},inplace=True)
	# breakpoint()
	df0 = df0.merge(dff,on='STATE',how='inner')


	#break continuous variable into categorical variable
	# df0['e'] = 'NA'
	# df0.loc[df0['ratio']>=1,'e'] = 'Rank3: >1'
	# df0.loc[(df0['ratio']<1)&(df0['ratio']>=0.5),'e'] = 'Rank2: 0.5-1'
	# df0.loc[(df0['ratio']<0.5)&(df0['ratio']>=0.3),'e'] = 'Rank2: 0.3-0.5'
	# df0.loc[(df0['ratio']<0.3)&(df0['ratio']>=0),'e'] = 'Rank 1: 0-0.3'
	# df0.loc[df0['ratio']<0,'e'] = 'Rank 0: <0'

	df0['e'] = np.nan
	df0.loc[df0['ratio']>=1,'e'] = 1.5
	df0.loc[(df0['ratio']<1)&(df0['ratio']>=0.5),'e'] = 0.75
	df0.loc[(df0['ratio']<0.5)&(df0['ratio']>=0.3),'e'] = 0.4
	df0.loc[(df0['ratio']<0.3)&(df0['ratio']>=0),'e'] = 0.15
	df0.loc[df0['ratio']<0,'e'] = -0.1

	df0 = df0.dropna()
	df0['rank'] = df0['ratio'].rank(ascending=False).astype('int')
	#create geodataframe
	df0 = gpd.GeoDataFrame(df0,geometry=df0.geometry) #to make a valid GeoDataFrame 
	df0.plot(ax=ax,column='e',categorical=False,cmap=cmap,norm=norm,legend=False) #,label=[>10,'2-10','1-2','<1'])

	#draw significant
	df0 = df0[df0.sig==1]
	df0 = gpd.GeoDataFrame(df0,geometry=df0.geometry.centroid)
	df0.plot(ax=ax,marker='o',markersize=8,color='black')
	ax.text(-128,53,'e',fontsize=25,weight='bold')

for iii,ii in enumerate([2,4,6,8]):
	hucnow = 'HUC%s'%ii
	huclower = hucnow.lower()
	print('... drawing %s ...'%hucnow)

	dff = pd.read_csv('processed_data/watershed_levee_effect_%s_regr.csv'%huclower)
	dff = dff.dropna()

	#calculate levee effect
	dff['levee_effect'] = (dff['k_levee_2']/dff['k_levee_1']-1) - (dff['k_county_2']/dff['k_county_1']-1)
	dff['sig'] = 0
	dff.loc[(dff['p_levee_1']<0.05)&(dff['p_levee_2']<0.05)&(dff['p_county_1']<0.05)&(dff['p_county_2']<0.05),'sig'] = 1
	# breakpoint()
	# dff = dff[dff['levee_effect']!='inf']
	# dff.loc[dff['levee_effect']==np.inf,'levee_effect'] = 100. #positive infinity is positive levee effect
	dff = dff[['%s'%huclower,'levee_effect','sig']]
	dff.rename(columns={'levee_effect':'ratio'},inplace=True)

	#geodataframe
	df0 = gpd.read_file('data/HUC_and_County/%s.shp'%hucnow)
	# breakpoint()
	df0['%s'%huclower] = df0['%s'%huclower].astype('int64')
	df0 = df0.merge(dff,on='%s'%huclower,how='left')
	# breakpoint()
	#break continuous variable into categorical variable
	df0['e'] = np.nan
	df0.loc[df0['ratio']==np.nan,'e'] = np.nan
	# df0.loc[df0['ratio']>=1,'e'] = 'Rank 4: >1'
	# df0.loc[(df0['ratio']<1)&(df0['ratio']>=0.5),'e'] = 'Rank 3: 0.5-1'
	# df0.loc[(df0['ratio']<0.5)&(df0['ratio']>=0.3),'e'] = 'Rank 2: 0.3-0.5'
	# df0.loc[(df0['ratio']<0.3)&(df0['ratio']>=0),'e'] = 'Rank 1: 0-0.3'
	# df0.loc[df0['ratio']<0,'e'] = 'Rank 0: <0'

	df0.loc[df0['ratio']>=1,'e'] = 1.5
	df0.loc[(df0['ratio']<1)&(df0['ratio']>=0.5),'e'] = 0.75
	df0.loc[(df0['ratio']<0.5)&(df0['ratio']>=0.3),'e'] = 0.4
	df0.loc[(df0['ratio']<0.3)&(df0['ratio']>=0),'e'] = 0.15
	df0.loc[df0['ratio']<0,'e'] = -0.1
	# df0.loc[df0['sig']==0,'e'] = ''#missing

	# df0 = df0.dropna()
	# df0['rank'] = df0['ratio'].rank(ascending=False).astype('int')
	#create geodataframe
	df0 = gpd.GeoDataFrame(df0,geometry=df0.geometry) #to make a valid GeoDataFrame 

	# breakpoint()
	df0.plot(ax=ax.flat[iii],column='e',categorical=False,cmap=cmap,norm=norm,legend=False,\
		missing_kwds={"color": "lightgrey","edgecolor": 'none',"hatch": "","label": "NA"}) #'YlOrRd') #,label=[>10,'2-10','1-2','<1'])
	#draw significant
	df0 = df0[df0.sig==1]
	df0 = gpd.GeoDataFrame(df0,geometry=df0.geometry.centroid)
	df0.plot(ax=ax.flat[iii],marker='o',markersize=markersize[iii],color='black')

	##############################################################
	#read state boundary
	# df = gpd.read_file('data/shapefile/States.shp')
	df = gpd.read_file('data/HUC_and_County/HUC%s.shp'%ii)
	df.plot(ax=ax.flat[iii],edgecolor='darkgreen',facecolor='none',linewidth=0.1) #,alpha=0.01)
	ax.flat[iii].text(-128,53,'abcd'[iii],fontsize=25,weight='bold')
	# #read river network data
	# df1 = gpd.read_file('data/shapefile/USA_Major_Rivers_CONUS.shp')
	# df1.plot(ax=ax.flat[iii],color='blue',linewidth=0.5) #
	# # df0.plot(column='rank',legend=True,cmap='Reds_r')
	# ##############################################################

plot_state(ax=ax.flat[4])

plt.tight_layout()
fon = 'plot_le_by_watershed.jpg'
fig.savefig(fon,dpi=500)
print('... plotting to %s ...'%fon)
# plt.close()

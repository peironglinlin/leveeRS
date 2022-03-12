import pandas as pd 
from sklearn import linear_model
import matplotlib.pyplot as plt

# read systemId - COMID map
df_id = pd.read_csv('./data/P_systemID_year_Meng_0312.csv')
# read levee area data
df_levee = pd.read_csv('./data/USGS_urban_ts_by_leveearea.csv')

# 将数据堆积成systemId|year|levee的格式
df_levee = pd.melt(df_levee, id_vars=['systemId'], value_vars=[i for i in df_levee if i!='systemId'])
df_levee = df_levee.rename(columns = {'variable':'year','value':'levee'})
df_levee['year'] = df_levee['year'].astype(int)
df_levee['systemId'] = df_levee['systemId'].astype(int)

# 加上yearCons
df_levee = pd.merge(df_levee,df_id[['systemId','Levee_year','areaSquare(mile)']],on='systemId')
df_levee['year_diff'] = df_levee['year']-df_levee['Levee_year'].astype(int)
df_levee['levee'] = df_levee['levee']*df_levee['areaSquare(mile)']/100

# 计算所有systemID的总和
df_levee = df_levee.pivot_table(index='year_diff',columns='systemId',values='levee')
df_levee = df_levee[(df_levee.index<=10) & (df_levee.index>=-10)]
# 把有空值的levee去掉
df_levee.dropna(axis=1, how="any",inplace=True)
df_levee['global_sum'] = df_levee[df_levee.columns].sum(axis=1)

# 画图
data = df_levee['global_sum'].reset_index()
data_fit = data[data.year_diff<0]

regr = linear_model.LinearRegression()
regr.fit(data_fit[['year_diff']], data_fit['global_sum'])
data['global_sum_predict'] = regr.predict(data[['year_diff']])

# 画protected area with levee
plt.plot(data['year_diff'], data['global_sum'], color='blue', linewidth=3,label='protected area with levee')
plt.scatter(data['year_diff'], data['global_sum'],alpha=0.5,marker='o',facecolors='none', edgecolors='blue',linewidth=3)
# 画protected area without levee
plt.plot(data[data.year_diff<=0]['year_diff'], data[data.year_diff<=0]['global_sum_predict'], color='red', linewidth=3, linestyle='dashed')
plt.plot(data[data.year_diff>=0]['year_diff'], data[data.year_diff>=0]['global_sum_predict'], color='red', linewidth=3,label='protected area without levee')
plt.plot([0,0], [data['global_sum'].min(),data['global_sum'].max()], color='grey', linewidth=3, linestyle='dashed')

for i in range(1,11):
	plt.plot([i,i], [data['global_sum_predict'][data.year_diff==i],data['global_sum'][data.year_diff==i]], color='grey', linewidth=2, linestyle='dashed')

plt.legend()
plt.savefig('global.png')

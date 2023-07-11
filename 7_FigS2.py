import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import numpy as np
import seaborn as sns 
import matplotlib as mpl 
from matplotlib.ticker import PercentFormatter
 
df_dam = pd.read_csv(r'C:\Users\mengd\Desktop\02Levee\Extended figures\Dam_year_1882.csv',encoding= 'unicode_escape')
Years_dam = df_dam['Year Completed'].tolist()
df_levee = pd.read_csv(r'C:\Users\mengd\Dropbox\Levee_from_desktop\Figures\All_levee_1882_2021.csv',encoding= 'unicode_escape')
Years_levee = df_levee['yearCons'].tolist()

sns.set_palette("hls") 
mpl.rc("figure", figsize=(7,5)) 
sns.axes_style("white")
fig=sns.histplot(Years_dam,bins=50, kde=False, stat='percent',color="green")
fig.tick_params(direction='out', length=0.5, width=0.5, colors='black',
               grid_color='white', grid_alpha=0.4)

fig=sns.histplot(Years_levee,bins=48, kde=False, stat='percent',color="blue")
fig.tick_params(direction='out', length=0.5, width=0.5, colors='black',
               grid_color='white', grid_alpha=0.4)

plt.xlabel("Year", fontsize=14,color='black')
plt.ylabel("Percent", fontsize=14,color='black')
plt.legend(labels=["Dam","Levee"])
plt.xticks(color='black',fontsize=12)
plt.yticks(color='black',fontsize=12)

plt.tight_layout()
plt.savefig(r'C:\0_MD_Work\2_1_Levee\Levee_writing\Final_checklist\Figures\FigS2\dam_levee_distribution.pdf',dpi=600)
plt.close()

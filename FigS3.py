import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv(r'C:\Users\mengd\Desktop\02Levee\Extended figures\0428_Supplementary_Fig3\negative1_870.csv')
x = df['COMID'].tolist()
y = df['updated_id870'].tolist()


plt.plot(x, y, linestyle='-', marker='o', markersize=6, color='black', label='line with marker')
plt.text(1974,0.78,"construction year", fontsize=15,horizontalalignment='center',color='blue')
plt.arrow(1974,0.7,0,-0.2,head_width=1.4, head_length=0.09, linewidth=2.4,color='blue')
x1 = [1974]
y1 = [1.959936957]
plt.plot(x1, y1, marker="o", markersize=6, markeredgecolor="blue", markerfacecolor="blue")

plt.xlabel("Year", fontsize=15,color='black')
plt.ylabel("Urban percent", fontsize=15,color='black')
plt.xticks(color='black',fontsize=15)
plt.yticks(color='black',fontsize=15)
plt.tight_layout() 
plt.savefig(r'C:\Users\mengd\Desktop\02Levee\Extended figures\0428_Supplementary_Fig3\negative1_county870_2.jpg',dpi=600)

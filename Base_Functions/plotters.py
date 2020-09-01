'''This file contains all necessary information for plotting relevant information.
It's used by the respective 'Plot_processor'.py'''

import warnings
warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)

import locale
import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
import platform 
import seaborn as sns


if platform.system()=='Windows':
    locale.setlocale(locale.LC_ALL, '')

else:
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')





sns.set(style='whitegrid',font_scale=1.2) ##General setting for plots

def boxplotter(daten,data_month,boxplottitle,printname):
	plt.figure(figsize=(15,20))
	ax=sns.boxplot(data=daten,x="val",y="cat")
	ax.set_ylabel('Kategorie',fontweight='bold')
	ax.set_xlabel('Einzelumsätze',fontweight='bold',labelpad=10)
	ax.set_title(boxplottitle+f"\n({data_month.loc[len(data_month)-1][0]} bis {data_month.loc[0][0]})", fontsize=18, fontweight='bold',pad=25)

	plt.savefig(printname,orientation='portrait',quality=80,bbox_inches='tight')
	plt.close()

def violinplotter(daten,data_month,violintitle,printname):
	plt.figure(figsize=(17,20))
	ax=sns.violinplot(data=daten,x="val",y="cat",scale='width',palette='rainbow')
	ax=sns.swarmplot(data=daten,x="val",y="cat",color='black',size=6)
	ax.set_ylabel('Kategorie',fontweight='bold',labelpad=10)
	ax.set_xlabel('Einzelumsätze',fontweight='bold')
	ax.set_title(violintitle+f"\n({data_month.loc[len(data_month)-1][0]} bis {data_month.loc[0][0]})", fontsize=18, fontweight='bold',pad=25)

	plt.savefig(printname,orientation='portrait',quality=80,bbox_inches='tight')
	plt.close()

def overviewplot(top3,top3_adj,data_month,plotinfo):
	title_main,title_left,title_right,printname=plotinfo
	##Main plot configuration
	fig, ax =plt.subplots(figsize=(14,13),nrows=2,ncols=2)
	plt.suptitle(title_main+f"\n ({data_month.loc[len(data_month)-1][0]} bis {data_month.loc[0][0]})", fontsize=18, fontweight='bold',y=1.03)

	## Definition first Subplot top-left
	ax1 = sns.barplot(x="cat", y="val", data=top3,palette='rainbow',ax=ax[0,0]) ##Definition kind of plot & axis
	ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))##Get y_height

	#set labels and titles
	ax1.set_ylabel('Gesamtbeträge der Periode in €',fontweight='bold')
	ax1.set_title(title_left,pad=60,fontweight='bold')

	#get values for every column
	for i, v in enumerate(top3["val"].iteritems()):        # add values on top of the plot
	    ax1.text(i ,v[1], f"{v[1]:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45)

	## Definition second Subplot top-right
	ax2 = sns.barplot(x="cat", y="val", data=top3_adj,palette='rainbow',ax=ax[0,1])
	ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
	ax2.set_title(title_right,pad=60,fontweight='bold')

	#check which y-axis to use
	yminax1,ymaxax1=ax1.get_ylim()
	yminax2,ymaxax2=ax2.get_ylim()
	if (ymaxax1>=ymaxax2) and (yminax1<=yminax2):
                ax1.set(xlabel='',xticklabels=[])
                ax2.set(xlabel='',ylabel="",xticklabels=[],yticklabels=[],ylim=ax1.get_ylim())
	elif (ymaxax1<ymaxax2) and (yminax1<=yminax2):
		ax1.set(xlabel='',xticklabels=[],ylim=(yminax1,ymaxax2))
		ax2.set(xlabel='',ylabel="",xticklabels=[],yticklabels=[],ylim=(yminax1,ymaxax2))
	elif (ymaxax1>=ymaxax2) and (yminax1>yminax2):
		ax1.set(xlabel='',xticklabels=[],ylim=(yminax2,ymaxax1))
		ax2.set(xlabel='',ylabel="",xticklabels=[],yticklabels=[],ylim=(yminax2,ymaxax1))
	else:
		ax1.set(xlabel='',xticklabels=[],ylim=ax2.get_ylim())
		ax2.set(xlabel='',ylabel="",xticklabels=[],yticklabels=[])
	
	#get values for every column
	for i, v in enumerate(top3_adj["val"].iteritems()):        
	    ax2.text(i ,v[1], f"{v[1]:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45)

	## Definition third Subplot bottom-left
	ax3 = sns.barplot(x="cat", y="val_month", data=top3,palette='rainbow',ax=ax[1,0])
	ax3.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
	ax3.set_xlabel("Kategorie",fontweight='bold',labelpad=10)
	ax3.set_ylabel('Durschschnittliche Monatsbeträge in €',fontweight='bold')

	#get values for every column and rotate x-axis-labels
	for item in ax3.get_xticklabels(): item.set_rotation(90)
	for i, v in enumerate(top3["val_month"].iteritems()):
	    ax3.text(i ,v[1], f"{v[1]:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45)
	

	## Definition fourth Subplot bottom-right 
	ax4 = sns.barplot(x="cat", y="val_month", data=top3_adj,palette='rainbow',ax=ax[1,1])
	ax4.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
	ax4.set_xlabel("Kategorie",fontweight='bold',labelpad=10)

	#check which y-axis to use
	yminax3,ymaxax3=ax3.get_ylim()
	yminax4,ymaxax4=ax4.get_ylim()
	if (ymaxax3>=ymaxax4) and (yminax3<=yminax4):
		ax4.set(ylabel="",yticklabels=[],ylim=ax3.get_ylim())
	elif (ymaxax3<ymaxax4) and (yminax3<=yminax4):
		ax3.set(ylim=(yminax3,ymaxax4))
		ax4.set(ylabel="",yticklabels=[],ylim=(yminax3,ymaxax4))
	elif (ymaxax3>=ymaxax4) and (yminax3>yminax4):
		ax3.set(ylim=(yminax4,ymaxax3))
		ax4.set(ylabel="",yticklabels=[],ylim=(yminax4,ymaxax3))
	else:
		ax3.set(ylim=ax4.get_ylim())
		ax4.set(ylabel="",yticklabels=[])


	#get values for every column and rotate x-axis-labels
	for item in ax4.get_xticklabels(): item.set_rotation(90)
	for i, v in enumerate(top3_adj["val_month"].iteritems()):        
	    ax4.text(i ,v[1], f"{v[1]:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45)   
	    
	 
	sns.despine()
	plt.subplots_adjust(left=0.15)
	fig.savefig(printname,orientation='portrait',quality=80,bbox_inches='tight')
	plt.close(fig)

def costplotter(plotinfo,data_month):
	costs,costtitle,printname=plotinfo
	##Main plot configuration
	fig, ax =plt.subplots(figsize=(15,15),nrows=2,sharex=True)
	plt.suptitle(costtitle+f"\n({data_month.loc[len(data_month)-1][0]} bis {data_month.loc[0][0]})", fontsize=18, fontweight='bold',y=1.01)

	## Definition first Subplot
	ax1 = sns.barplot(x="cat", y="val", data=costs,palette='rainbow',ax=ax[0]) ##Definition kind of plot & axis
	ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))##Get y_height

	 ##set labels and titles
	ax1.set_xlabel("")
	ax1.set_ylabel('Gesamtbeträge der Periode in €',fontweight='bold')

	for item in ax1.get_xticklabels(): item.set_rotation(90) #alter plotting of x valuesticks
	for i, v in enumerate(costs["val"].iteritems()):        # add values on top of the plot
	    ax1.text(i ,v[1], f"{v[1]:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45)

	## Definition second Subplot
	ax2 = sns.barplot(x="cat", y="val_month", data=costs,palette='rainbow',ax=ax[1])
	ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

	ax2.set_xlabel("Kategorie",fontweight='bold',labelpad=10)
	ax2.set_ylabel('Durschschnittliche Monatsbeträge in €',fontweight='bold')
	for item in ax2.get_xticklabels(): item.set_rotation(90)
	for i, v in enumerate(costs["val_month"].iteritems()):        
	    ax2.text(i ,v[1], f"{v[1]:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45) # replace replaces thousand separator

	   
	sns.despine()
	plt.subplots_adjust(left=0.15)
	fig.savefig(printname,orientation='portrait',quality=80,bbox_inches='tight')
	plt.close(fig)

def monthplotter(plotinfo,data_month):
	monthtitle,printname=plotinfo

	balance=data_month['val'].sum()/(data_month['month'].nunique())##get total balance 

	##Main plot configuration
	plt.figure(figsize=(15,13))

	##Main title
	plt.suptitle(monthtitle+f"\n({data_month.loc[len(data_month)-1][0]} bis {data_month.loc[0][0]})", fontsize=18, fontweight='bold',y=1.01)


	## Definition Plot
	##get negative values red
	def bar_color(data_month,color1,color2):
		return np.where(data_month['val']>0,color1,color2).T

	#Plotting info
	ax = sns.barplot(x="month", y="val", data=data_month,palette=bar_color(data_month,'darkgreen','red')) ##Definition kind of plot & axis
	ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))##Get y_height


	#get x coordinates for horizontal line
	xleft,xright=ax.get_xlim()
	ax.hlines(y=balance,xmin=xleft,xmax=xright,linestyle='dashdot',linewidth=3) #plot horizontal line
	ax.text(xright, balance, "Ø-Monatssaldo des\n Gesamtzeitraums:\n",ha='left', va='bottom',fontsize=14,fontweight='heavy')#Label horizontal line
	ax.text(xright, balance,f"        {balance:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."), ha='left', va='center',fontsize=14,fontweight='heavy') #Value horizontal line

	##set labels and titles
	##set labels and titles
	ax.xaxis.set_tick_params(pad=25)
	ax.set_ylabel('Gesamtbeträge je Monat in €',fontweight='bold')
	ax.set_xlabel('Monate',fontweight='bold',labelpad=10)
	for item in ax.get_xticklabels(): item.set_rotation(90) #alter plotting of x valuesticks
	for i, v in enumerate(data_month["val"].iteritems()):# add values on top of the plot
		if v[1]>0:
			ax.text(i ,v[1], f"{v[1]:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45)  # reformat thousand separator and decimal comma
		else:
			ax.text(i ,v[1], f"{v[1]:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."), color='black',ha='right', va ='top',rotation=45)
	sns.despine()
	plt.savefig(printname,orientation='portrait',quality=80,bbox_inches='tight')
	plt.close()


def pieplotter(plotinfo_piechart,data_month):
    pie_data,plotinfo=plotinfo_piechart
    data_left,data_right=pie_data
    maintitle,left_title,right_title,printname=plotinfo

    pie_label_l=list(data_left['cat'])
    pie_size_l=list(data_left['ppt'])

    exploder1=[1]*len(data_left)
    for i in range(0,len(data_left)):
        if data_left['ppt'][i]<10:
            exploder1[i]=0.2
        else:  
            exploder1[i]=0.02

    exploder2=[1]*len(data_right)
    for i in range(0,len(data_right)):
        if data_right['ppt'][i]<10:
            exploder2[i]=0.2
        else:  
            exploder2[i]=0.02

    pie_label_r=list(data_right['cat'])
    pie_size_r=list(data_right['ppt'])

    ##Plot details
    fig, axes = plt.subplots(1, 2, figsize=(16, 12))
    plt.suptitle(maintitle+f"\n({data_month.loc[len(data_month)-1][0]} bis {data_month.loc[0][0]})", fontsize=18, fontweight='bold')
    ##Left plot
    ax2=axes[0].pie(pie_size_l, labels=pie_label_l, explode=exploder1, autopct=lambda p : f"{p:1.1f}%".replace(".", ","),shadow=True, startangle=180)# Equal aspect ratio ensures that pie is drawn as a circle
    axes[0].set_title(left_title,pad=40, fontweight='bold')

    ##Right plot
    ax2=axes[1].pie(pie_size_r, labels=pie_label_r, explode=exploder2, autopct=lambda p : f"{p:1.1f}%".replace(".", ","),shadow=True, startangle=75)# Equal aspect ratio ensures that pie is drawn as a circle
    axes[1].set_title(right_title,pad=40, fontweight='bold')

    plt.savefig(printname,orientation='landscape',quality=80,bbox_inches='tight')
    plt.close(fig)

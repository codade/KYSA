'''This file contains all necessary information for plotting relevant information.
It's used by the respective 'Plot_processor'.py
Plot function in Plot_processor hands over data, plottitle, printname and axadjustement for splitted plots
axadjust is send as tuple. First position (axadjust[0] contains get or set condition, second position (axadjust [1] holds axvalue'''


import warnings
warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)

import locale
import matplotlib
matplotlib.use("Agg")#necessary to avoid graphics crashing for plotting and simultaneous progressbar output
from matplotlib import pyplot as plt
import numpy as np
import platform 
import seaborn as sns

from Base_Functions.user_process import language_choice,langdict_used,currency_var 

langdict_all=langdict_used ##needed for plotter preprocessing file

#set locale for plotting
if language_choice=='eng':
    if platform.system()=='Windows':
        locale.setlocale(locale.LC_ALL, 'English')
    else:
        locale.setlocale(locale.LC_ALL, 'en_US.utf8')   
else:
    if platform.system()=='Windows':
        locale.setlocale(locale.LC_ALL, 'German')
    else:
        locale.setlocale(locale.LC_ALL, 'de_DE.utf8')

    

# language dictionary choice for this script
langdict_plot=langdict_used['Plotting_vars']


#main variables for category and time period 

axcatdata=langdict_plot['axcatdata'][0]
timesep_month=langdict_plot['timesep_month'][0]


sns.set(style='whitegrid',font_scale=1.2) ##General setting for plots

def boxplotter(plotinfo,axadjust,data_month):

	daten,boxplottitle,printname=plotinfo
	plt.figure(figsize=(15,20))
	ax=sns.boxplot(data=daten,x="val",y="cat")
	ax.set_ylabel(axcatdata,fontweight='bold')
	ax.set_xlabel(langdict_plot['box_violplot_xaxis'][0],fontweight='bold',labelpad=10)
	ax.set_title(boxplottitle+f"\n({data_month.loc[len(data_month)-1][0]} "+timesep_month+f" {data_month.loc[0][0]})", fontsize=18, fontweight='bold',pad=25)

	#get axvalues for splitted plots
	if axadjust[0]=='getval':
		axvalue=ax.get_xlim()
	elif axadjust[0]=='setval':
		axvalue=axadjust[1]
		ax.set(xlim=axvalue)
		
	else:
		pass

	#save plot
	plt.savefig(printname,orientation='portrait',bbox_inches='tight')
	plt.close()
	return axvalue

def violinplotter(plotinfo,axadjust,data_month):

	daten,violintitle,printname=plotinfo
	plt.figure(figsize=(17,20))
	ax=sns.violinplot(data=daten,x="val",y="cat",scale='width',palette='rainbow')
	ax=sns.swarmplot(data=daten,x="val",y="cat",color='black',size=6)
	ax.set_ylabel(axcatdata,fontweight='bold',labelpad=10)
	ax.set_xlabel(langdict_plot['box_violplot_xaxis'][0],fontweight='bold')
	ax.set_title(violintitle+f"\n({data_month.loc[len(data_month)-1][0]} "+timesep_month+f" {data_month.loc[0][0]})", fontsize=18, fontweight='bold',pad=25)

	#get axvalues for splitted plots
	if axadjust[0]=='getval':
		axvalue=ax.get_xlim()	
	elif axadjust[0]=='setval':
		axvalue=axadjust[1]
		ax.set(xlim=axvalue)
	else:
		pass

	#save plot
	plt.savefig(printname,orientation='portrait',bbox_inches='tight')
	plt.close()
	return axvalue

def overviewplot(top3,top3_adj,data_month,plotinfo):
	## overview plots are not splitted, therefore nor axadjust statements

	title_main,title_left,title_right,printname=plotinfo
	##Main plot configuration
	fig, ax =plt.subplots(figsize=(14,13),nrows=2,ncols=2)
	plt.suptitle(title_main+f"\n ({data_month.loc[len(data_month)-1][0]} "+timesep_month+f" {data_month.loc[0][0]})", fontsize=18, fontweight='bold',y=1.03)

	## Definition first Subplot top-left
	ax1 = sns.barplot(x="cat", y="val", data=top3,palette='rainbow',ax=ax[0,0]) ##Definition kind of plot & axis
	ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))##Get y_height

	#set labels and titles
	ax1.set_ylabel(langdict_plot['costplot_yaxes'][0],fontweight='bold')
	ax1.set_title(title_left,pad=60,fontweight='bold')

	#get values for every column
	for i, v in enumerate(top3["val"].iteritems()):        # add values on top of the plot
		if language_choice=='deu':
			ax1.text(i ,v[1], f"{v[1]:,.2f} {currency_var}".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45) #displays thounds separator correctly as dot according to german system
		else:
			ax1.text(i ,v[1], f"{v[1]:,.2f} {currency_var}", color='black', va ='bottom', rotation=45)

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
		if language_choice=='deu':
			ax2.text(i ,v[1], f"{v[1]:,.2f} {currency_var}".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45) #displays thounds separator correctly as dot according to german system
		else:
			ax2.text(i ,v[1], f"{v[1]:,.2f} {currency_var}", color='black', va ='bottom', rotation=45)        

	
	## Definition third Subplot bottom-left
	ax3 = sns.barplot(x="cat", y="val_month", data=top3,palette='rainbow',ax=ax[1,0])
	ax3.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
	ax3.set_xlabel(axcatdata,fontweight='bold',labelpad=10)
	ax3.set_ylabel(langdict_plot['costplot_yaxes'][1],fontweight='bold')

	#get values for every column and rotate x-axis-labels
	for item in ax3.get_xticklabels(): item.set_rotation(90)
	for i, v in enumerate(top3["val_month"].iteritems()):
		if language_choice=='deu':
			ax3.text(i ,v[1], f"{v[1]:,.2f} {currency_var}".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45) #displays thounds separator correctly as dot according to german system
		else:
			ax3.text(i ,v[1], f"{v[1]:,.2f} {currency_var}", color='black', va ='bottom', rotation=45)


	## Definition fourth Subplot bottom-right 
	ax4 = sns.barplot(x="cat", y="val_month", data=top3_adj,palette='rainbow',ax=ax[1,1])
	ax4.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
	ax4.set_xlabel(axcatdata,fontweight='bold',labelpad=10)


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
		if language_choice=='deu':
			ax4.text(i ,v[1], f"{v[1]:,.2f} {currency_var}".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45) #displays thounds separator correctly as dot according to german system
		else:
			ax4.text(i ,v[1], f"{v[1]:,.2f} {currency_var}", color='black', va ='bottom', rotation=45)    
	
	separator_loc=top3.index[-3]-0.5 #location to put vertical line to
	seperator_1=ax1.vlines(x=separator_loc,ymin=ax1.get_ylim()[0],ymax=ax1.get_ylim()[1],linestyle=(0, (3, 1, 1, 1, 1, 1)),linewidth=2,color='grey') #plot vertical dashdotted line between revenues and costs
	seperator_2=ax3.vlines(x=separator_loc,ymin=ax3.get_ylim()[0],ymax=ax3.get_ylim()[1],linestyle=(0, (3, 1, 1, 1, 1, 1)),linewidth=2,color='grey') #plot vertical dashdotted line between revenues and costs
	ax1.text(separator_loc-0.05,ax1.get_ylim()[1], langdict_plot['overviewplot_extralabel'][0],ha='right', va='top',fontsize=12,fontweight='heavy',rotation=90,color='grey')#Label horizontal line revenues
	ax1.text(separator_loc+0.07,ax1.get_ylim()[1], langdict_plot['overviewplot_extralabel'][1],ha='left', va='top',fontsize=12,fontweight='heavy',rotation=90,color='grey')#Label horizontal line revenues

	sns.despine()
	plt.subplots_adjust(left=0.15)
	fig.savefig(printname,orientation='portrait',bbox_inches='tight')
	plt.close(fig)

def costplotter(plotinfo,axadjust,data_month):
	costs,costtitle,printname=plotinfo
	##Main plot configuration
	fig, ax =plt.subplots(figsize=(15,15),nrows=2,sharex=True)
	plt.suptitle(costtitle+f"\n({data_month.loc[len(data_month)-1][0]} "+timesep_month+f" {data_month.loc[0][0]})", fontsize=18, fontweight='bold',y=1.01)

	## Definition Subplots
	ax1 = sns.barplot(x="cat", y="val", data=costs,palette='rainbow',ax=ax[0]) ##Definition kind of plot & axis
	ax2 = sns.barplot(x="cat", y="val_month", data=costs,palette='rainbow',ax=ax[1])

	#axadjustement for costplotters has to be performed on two axes. Second position in tuple is stored as tuple itself, so that first position in subtuple is overall axvalue, second position holds
	#the monthly plot axvalue

	if axadjust[0]=='getval':
		axvalue_1=ax1.get_ylim()		
		axvalue_2=ax2.get_ylim()		
	elif axadjust[0]=='setval':
		axvalue_1=axadjust[1][0]
		ax1.set(ylim=axvalue_1)
		axvalue_2=axadjust[1][1]
		ax2.set(ylim=axvalue_2)
	else:
		pass

	#First subplot preparations for labeling
	ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))##Get y_height


	##set labels and titles
	ax1.set_xlabel("")
	ax1.set_ylabel(langdict_plot['costplot_yaxes'][0],fontweight='bold')

	for item in ax1.get_xticklabels(): item.set_rotation(90) #alter plotting of x valuesticks
	for i, v in enumerate(costs["val"].iteritems()):        # add values on top of the plot
		if language_choice=='deu':
			ax1.text(i ,v[1], f"{v[1]:,.2f} {currency_var}".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45) #displays thounds separator correctly as dot according to german system
		else:
			ax1.text(i ,v[1], f"{v[1]:,.2f} {currency_var}", color='black', va ='bottom', rotation=45)

	#Second subplot preparations for labeling

	ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
	##set labels and titles
	ax2.set_xlabel(axcatdata,fontweight='bold',labelpad=10)
	ax2.set_ylabel(langdict_plot['costplot_yaxes'][1],fontweight='bold')
	for item in ax2.get_xticklabels(): item.set_rotation(90)
	for i, v in enumerate(costs["val_month"].iteritems()):        
		if language_choice=='deu':
			ax2.text(i ,v[1], f"{v[1]:,.2f} {currency_var}".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45) #displays thounds separator correctly as dot according to german system
		else:
			ax2.text(i ,v[1], f"{v[1]:,.2f} {currency_var}", color='black', va ='bottom', rotation=45)

	#save plot
	sns.despine()
	plt.subplots_adjust(left=0.15)
	fig.savefig(printname,orientation='portrait',bbox_inches='tight')
	plt.close(fig)
	return (axvalue_1,axvalue_2)

def monthplotter(plotinfo,axadjust,data_month):
	plot_data,monthtitle,printname=plotinfo

	balance=data_month['val'].sum()/(data_month['month'].nunique())##get total balance 

	##Main plot configuration
	plt.figure(figsize=(15,13))

	##Main title
	plt.suptitle(monthtitle+f"\n({data_month.loc[len(data_month)-1][0]} "+timesep_month+f" {data_month.loc[0][0]})", fontsize=18, fontweight='bold',y=1.01)


	## Definition Plot
	##get negative values red
	def bar_color(plot_data,color1,color2):
		return np.where(plot_data['val']>0,color1,color2).T

	#Plotting info
	ax = sns.barplot(x="month", y="val", data=plot_data,palette=bar_color(plot_data,'darkgreen','red')) ##Definition kind of plot & axis

	if axadjust[0]=='getval':
		axvalue=ax.get_ylim()
	elif axadjust[0]=='setval':
		axvalue=axadjust[1]
		ax.set(ylim=axvalue)
		

	ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))##Get y_height


	#get x coordinates for horizontal line
	xleft,xright=ax.get_xlim()
	ax.hlines(y=balance,xmin=xleft,xmax=xright,linestyle='dashdot',linewidth=3) #plot horizontal line
	ax.text(xright, balance, langdict_plot['monthplot_extralabel'][0],ha='left', va='bottom',fontsize=14,fontweight='heavy')#Label horizontal line
	if language_choice=='deu':
		ax.text(xright, balance,f"        {balance:,.2f} {currency_var}".replace(",", "X").replace(".", ",").replace("X", "."), ha='left', va='center',fontsize=14,fontweight='heavy') #Value horizontal line german number system
	else:
		ax.text(xright, balance,f"        {balance:,.2f} {currency_var}", ha='left', va='center',fontsize=14,fontweight='heavy')
	

	##set labels and titles
	##set labels and titles
	ax.xaxis.set_tick_params(pad=25)
	ax.set_ylabel(langdict_plot['monthplot_axes'][0],fontweight='bold')
	ax.set_xlabel(langdict_plot['monthplot_axes'][1],fontweight='bold',labelpad=10)
	for item in ax.get_xticklabels(): item.set_rotation(90) #alter plotting of x valuesticks
	for i, v in enumerate(plot_data["val"].iteritems()):# add values on top of the plot
		if v[1]>0:
			if language_choice=='deu':
				ax.text(i ,v[1], f"{v[1]:,.2f} {currency_var}".replace(",", "X").replace(".", ",").replace("X", "."), color='black', va ='bottom', rotation=45)  # reformat thousand separator and decimal comma for positive values (above plotted bar)
			else:
				ax.text(i ,v[1], f"{v[1]:,.2f} {currency_var}", color='black', va ='bottom', rotation=45)  # english number format for positive values (above plotted bar)
		else:
			if language_choice=='deu':
				ax.text(i ,v[1], f"{v[1]:,.2f} {currency_var}".replace(",", "X").replace(".", ",").replace("X", "."), color='black',ha='right', va ='top',rotation=45) # reformat thousand separator and decimal comma for negative values (belwo plotted bar)
			else:
				ax.text(i ,v[1], f"{v[1]:,.2f} {currency_var}", color='black',ha='right', va ='top',rotation=45) # english number format for negative values (belwo plotted bar)	

	sns.despine()
	
	#save plot
	plt.savefig(printname,orientation='portrait',bbox_inches='tight')
	plt.close()
	return axvalue


def pieplotter(plotinfo_piechart,data_month):
	#no axadjustment for piecharts necessary. 2% limitation is calculated in plot_process.py
	#tuple unpacking plotinfo piechart
	pie_data,plotinfo=plotinfo_piechart
	data_topl,data_topr,data_botl,data_botr=pie_data
	mainplotinfo,subplotinfo=plotinfo
	maintitle,fig_row_number,printname=mainplotinfo
	title_topl,title_topr,title_botl,title_botr=subplotinfo


	#create necessary lists for iteration through submitted data
	datalist=[data_topl,data_topr,data_botl,data_botr]
	subtitlelist=[title_topl,title_topr,title_botl,title_botr]

	# get categorical color scheme via seaborn 
	#blue_clr= sns.color_palette('Blues_r',7)
	#orange_clr=sns.color_palette('Oranges_r',7)
	#green_clr=sns.color_palette('Greens_r',7)
	#red_clr=sns.color_palette('Reds_r',7)

	#get categorical color scheme via matplotlib and make loopable list
	blue_clr= plt.get_cmap('Blues_r')(np.arange(2,15)*25)
	orange_clr=plt.get_cmap('Oranges_r')(np.arange(2,15)*25)
	green_clr=plt.get_cmap('Greens_r')(np.arange(2,15)*25)
	red_clr=plt.get_cmap('Reds_r')(np.arange(2,15)*25)



	
	#check for holiday entry in main categories for pie plots with 4 diagrams
	if fig_row_number>1:
		if (langdict_plot['pieplot_holidayexcl'][0] in data_topl['cat'][0:2].tolist()):
		#get index of holidays entries
			holiday_index=data_topl['cat'].index(langdict_plot['pieplot_holidayexcl'][0])
			if holiday_index==0: #holidays is biggest category
				colorslist=[None,orange_clr,green_clr,red_clr]
				#colorslist=['tab10','Oranges_r','Greens_r','Reds_r']
			elif holiday_index==1: #holidays is second biggest category
				colorslist=[None,blue_clr,green_clr,red_clr]
				#colorslist=[None,'Blues_r','Greens_r','Reds_r']
			else: #holidays is third biggest category
				colorslist=[None,blue_clr,orange_clr,red_clr]
				#colorslist=[None,'Blues_r','Oranges_r','Reds_r']
		else:#holidays is not in the top3 category
			colorslist=[None,blue_clr,orange_clr,green_clr]
			#colorslist=[None,'Blues_r','Oranges_r','Greens_r']

	else:
		colorslist=[None,None,None,None]


	angle_var=[180,75,245,0] #start angle upper left pie charts explodes parts are oriented to the upper left. Rotation in 105° steps

	#create mainframe for chart
	fig, axes = plt.subplots(figsize=(18, 15),nrows=fig_row_number,ncols=2)
	plt.suptitle(maintitle+f"\n({data_month.loc[len(data_month)-1][0]} "+timesep_month+f" {data_month.loc[0][0]})", fontsize=18, fontweight='bold')




	#iterate through data sets and prepare piecharts
	for chart_no in range(0,fig_row_number*2): #for loop preparing pie data
		
		pielabel=list(datalist[chart_no]['cat'])
		piesize=list(datalist[chart_no]['ppt'])
		use_color=colorslist[chart_no]

		#define ax indices row and col
		ax_index_col=chart_no%2
		if chart_no==0:
			ax_index_row=0
		else:
			ax_index_row=int((chart_no-ax_index_col)/2)
		

		explode_slices=[1]*len(piesize)
		# set explode factors for every entry. Pie slices smaller than 10% are shown in greater explosion 
		for item in range(0,len(piesize)):
			if piesize[item]<10:
				explode_slices[item]=0.2
			else:  
				explode_slices[item]=0.02



		#adaptions to axnumation for plots with just one row (fig_row_number==1)
		if fig_row_number==1:
			##Set subplots (single pie chart) and adjust number formatting for german and english
			if language_choice=='deu':
				axes[ax_index_col].pie(piesize, labels=pielabel, explode=explode_slices,colors=colorslist[chart_no], autopct=lambda p : f"{p:1.1f}%".replace(".", ","),shadow=True, startangle=angle_var[chart_no])# Equal aspect ratio ensures that pie is drawn as a circle german number separator	
			else:
				axes[ax_index_col].pie(piesize, labels=pielabel, explode=explode_slices,colors=colorslist[chart_no], autopct=lambda p : f"{p:1.1f}%",shadow=True, startangle=angle_var[chart_no])# Equal aspect ratio ensures that pie is drawn as a circle german number separator

			#set info
			axes[ax_index_col].set_title(subtitlelist[chart_no],pad=40, fontweight='bold')
		
		else: #more than 2 pie charts
			if language_choice=='deu':
				axes[ax_index_row,ax_index_col].pie(piesize, labels=pielabel,colors=colorslist[chart_no], explode=explode_slices, autopct=lambda p : f"{p:1.1f}%".replace(".", ","),shadow=True, startangle=angle_var[chart_no])# Equal aspect ratio ensures that pie is drawn as a circle german number separator
			else:
				axes[ax_index_row,ax_index_col].pie(piesize, labels=pielabel,colors=colorslist[chart_no], explode=explode_slices, autopct=lambda p : f"{p:1.1f}%",shadow=True, startangle=angle_var[chart_no])# Equal aspect ratio ensures that pie is drawn as a circle german number separator
		
			axes[ax_index_row,ax_index_col].set_title(subtitlelist[chart_no],pad=40, fontweight='bold')


	plt.savefig(printname,orientation='landscape',bbox_inches='tight') # save created chart
	plt.close(fig)

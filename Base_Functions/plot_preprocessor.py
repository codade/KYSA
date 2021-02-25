
'''This file is needed to preprocess the submitted data to fit the needed format for the plotting functions. Cost data is separated with regards to investment costs and total costs.
Pie relative portion charts are created for cost components >2%, and shown separately according to investment and holiday costs with regards to total costs.'''

from Base_Functions import plotters
import numpy as np
import pandas as pd
import platform 

if platform.system()=='Windows':
    folder_sep='\\'

else:
    folder_sep='/'


langdict_plotp=plotters.langdict_all['Plot_Proc_vars']

class Plotters:

    def __init__(self,accounts_data):

        self.plot_elements=list(accounts_data.plotting_list.keys())
        self.plotting_choice=accounts_data.plotting_list
        self.basis_data=accounts_data.basis_data
        self.month_data=accounts_data.month_data
        self.cat_data=accounts_data.cat_data
        self.top3={}
        self.top3_adj={}
        self.plotinfo_month={}
        self.plotinfo_costs={}
        self.plotinfo_boxplot={}
        self.plotinfo_vioplot={}
        self.plotinfo_piechart={}
        self.folder_sep=folder_sep
        self.folder_res=accounts_data.folder_res

        
    ##Prepare Plot-Data:
    def makeplotdata(self):
        
        ##Shuffle through items:
        for element_name in self.plot_elements:
            
            '''tuple unpacking cat data:
            1. savecent and holiday cat_data doesn't hold a main_cat data set
            2. Within the Cashbook dataset the main_cat variable holds the categorised account origins of cash payments
            3. All other dataframes have both datasets
            '''

            subcat_data,main_cat_data=self.cat_data[element_name]
            #create filepath
            file_resultpath=self.folder_res[element_name]+self.folder_sep

            #define local variable for indication if income plots should be calculated
            plot_revenues=False

            ##create dataframe containing all income categories for further usage:
            
#______________________________________________________________________Define basic costplots and monthplots for every dataframe ______________________________________
           
            ## prepare cost and month plots for accounts 
            # do specific adjustements for savecents, holidays and cashbook cat_data as these categorial elements are stored in a different manner than normal account cat_data
            if element_name==langdict_plotp['costplot_savecent'][0]:
                #savecents cat data differs from other cat_data. Therefore separate handling is necessar
                self.plotinfo_costs[element_name]=[(subcat_data,eval(f"f'''{langdict_plotp['costplot_savecent'][1]}'''"),file_resultpath+langdict_plotp['costplot_savecent'][2])]#cost plot data & info
                
                #separate month data for possible plot splittung
                month_plot=self.month_data[element_name].copy()
                self.plotinfo_month[element_name]=[(month_plot,eval(f"f'''{langdict_plotp['monthplot_savecent'][1]}'''"),file_resultpath+langdict_plotp['monthplot_savecent'][2])] #month plot data & info
            
            elif element_name==langdict_plotp['costplot_holiday'][0]:
                # specific actions necessary to specifically created "holiday" account

                cost_total=subcat_data.copy()
                cost_total[['val','val_month']]=cost_total[['val','val_month']].abs() #do sign reversal for better cost depicting 
                cost_total=cost_total.sort_values('val',ascending=False).reset_index(drop=True) #sorting descending
                self.plotinfo_costs[element_name]=[(cost_total,langdict_plotp['costplot_holiday'][1],file_resultpath+langdict_plotp['costplot_holiday'][2])] #cost plot data & info
                
                #separate month data for possible plot splittung
                month_plot=self.month_data[element_name].copy()
                self.plotinfo_month[element_name]=[(month_plot,langdict_plotp['monthplot_holiday'][1],file_resultpath+langdict_plotp['monthplot_holiday'][2])] #month plot data & info

            elif element_name==langdict_plotp['costplot_cashbook1'][0]:

                #plot cashbook expenditures by category
                self.plotinfo_costs[element_name]=[(subcat_data,langdict_plotp['costplot_cashbook1'][1],file_resultpath+langdict_plotp['costplot_cashbook1'][2])] #cost plot data & info
                #plot cashbook expenditures by account origin

                self.plotinfo_costs[element_name].append((main_cat_data,langdict_plotp['costplot_cashbook2'][1],file_resultpath+langdict_plotp['costplot_cashbook2'][2])) #cost plot data & info
                
                #separate month data for possible plot splittung
                month_plot=self.month_data[element_name].copy()
                self.plotinfo_month[element_name]=[(month_plot,langdict_plotp['monthplot_cashbook'][1],file_resultpath+langdict_plotp['monthplot_cashbook'][2])] #month plot data & info
                
            else:##Cost & month plot remaining data frames
                total_revenues=subcat_data[(subcat_data['main cat'].str.contains(langdict_plotp['costplot_search'][0])==False)&(subcat_data['val']>0)].copy() #all main categories without total balance, holidays and cash payments
                
                #set plot_revenues true if more than 2 income sources are found
                if len(total_revenues)>2: 
                    plot_revenues=True
                else:
                    pass
                #NEW auto-adjust plottypes for excels and concats, if total income is empty
                if (len(total_revenues)==0)&(self.plotting_choice[element_name]==""):
                    self.plotting_choice[element_name]='normal'
                elif (self.plotting_choice[element_name]==""):
                    self.plotting_choice[element_name]='complete'
                else:
                    pass

                #plot overview of all cost categories
                cost_total=subcat_data[(subcat_data['cat'].isin(total_revenues['cat'].tolist()+[langdict_plotp['costplot_basis_subcats'][0]])==False)&(subcat_data['val']<0)].copy()
                cost_total[['val','val_month']]=cost_total[['val','val_month']].abs() #do sign reversal for better cost depicting
                cost_total=cost_total.sort_values('val',ascending=False).reset_index(drop=True) #sorting descending
                self.plotinfo_costs[element_name]=[(cost_total,eval(f"f'''{langdict_plotp['costplot_basis_subcats'][1]}'''"),file_resultpath+langdict_plotp['costplot_basis_subcats'][2])] #cost plot data & info
                
                #plot overview of main categories without income
                main_cost_total=main_cat_data[(main_cat_data['main cat'].isin(total_revenues['main cat'].tolist()+[langdict_plotp['costplot_basis_subcats'][0]])==False)&(main_cat_data['val']<0)].copy()
                main_cost_total[['val','val_month']]=main_cost_total[['val','val_month']].abs() #do sign reversal for better cost depicting
                main_cost_total.columns=['cat','val','val_month'] #rename columns for plotting function
                main_cost_total=main_cost_total.sort_values('val',ascending=False).reset_index(drop=True) #sorting descending
                self.plotinfo_costs[element_name].append((main_cost_total,eval(f"f'''{langdict_plotp['costplot_basis_maincats'][1]}'''"),file_resultpath+langdict_plotp['costplot_basis_maincats'][2])) #cost plot data & info

                #separate month data for possible plot splittung
                month_plot=self.month_data[element_name].copy()
                self.plotinfo_month[element_name]=[(month_plot,eval(f"f'''{langdict_plotp['monthplot_basis'][1]}'''"),file_resultpath+langdict_plotp['monthplot_basis'][2])] #month plot data & info
           

#______________________________________________________________________Prepare specific plots ______________________________________ 

################################################################### pie plot for main categories and the 3 biggest main categories ##############################
                #still inside else clause for main data frames
                list_top_maincosts_nohol=list(main_cost_total['cat'].loc[0:2]) #get top3 main categories

                if langdict_plotp['cost_piechart_adjust'][0] in list_top_maincosts_nohol: #if holiday category is in list get fourth biggest main category and drop holiday entry
                    list_top_maincosts_nohol.append(main_cost_total['cat'].loc[3])
                    list_top_maincosts_nohol.remove(langdict_plotp['cost_piechart_adjust'][0]) #remove holiday category
                else:
                    pass #nothing to do

              
                ## create category pie chart for main categories (top left) and three biggest main categories (top right to bottom right)
                pieplot_costs_prepdata=[]
                pieplot_costs_finaldata=[]
                pieplot_costs_subplotinfo=[]
                #Icreate data sets
                for num in range(0,4):
                    #1)get data sets
               
                    if num==0:
                        # 1. main cat data
                        costs_pie_prep_data=main_cost_total.copy() #get data
                        
                    else:
                        # 2. cat data for three biggest main categories
                        top3_maincatname=list_top_maincosts_nohol[num-1] #needed for subplot info as well
                       

                        costs_pie_prep_data=cost_total[cost_total['main cat']==top3_maincatname].copy() #get data of subcat data set depending on main cat name
                        costs_pie_prep_data.drop(['main cat'],axis=1,inplace=True)#drop main cat column

                        #delete line breaks in maincatname if present
                        if '\n' in top3_maincatname:
                            if '(-\n)' in top3_maincatname:
                                top3_maincatname=''.join(top3_maincatname.split('-\n'))
                            else:
                                top3_maincatname=' '.join(top3_maincatname.split('\n'))
                        else:
                            pass

                    
                    pieplot_costs_prepdata.append(costs_pie_prep_data) #append it to preparation datalist

                    #2) create percentages and group slices together if necessary
                    pieplot_costs_prepdata[num]=pieplot_costs_prepdata[num].assign(ppt=(pieplot_costs_prepdata[num]['val']*100/pieplot_costs_prepdata[num]['val'].sum()).round(2)) #create percentages for every entry
                    pieplot_costs_prepdata[num].drop(['val','val_month'],axis=1,inplace=True) #drop columns not needed anymore
                    costs_pie_final=pieplot_costs_prepdata[num].loc[pieplot_costs_prepdata[num]['ppt']>=2.5].copy() #get slices with more than 2.5% 

                    #group slices smaller than 2.5% together if those slices grouped together are bigger than 0
                    if sum(pieplot_costs_prepdata[num].loc[pieplot_costs_prepdata[num]['ppt']<2.5]['ppt'])>0:
                        #create slice named remaing stakes <2.5%
                        costs_pie_final=costs_pie_final.append(pd.DataFrame([[langdict_plotp['piechart_2%name'][0],sum(pieplot_costs_prepdata[num].loc[pieplot_costs_prepdata[num]['ppt']<2.5]['ppt'])]],columns=list(pieplot_costs_prepdata[num].columns)),ignore_index=True)
                    else:
                        pass #nothing to do
                    pieplot_costs_finaldata.append(costs_pie_final) #append final subdataset to dataset list
                    
                    #3) add subplotinfo
                    pieplot_costs_subplotinfo.append(eval(f"f'''{langdict_plotp['costs_piechart_sub'][num]}'''"))
                

                #II pack data and plotinfo and store it in dictionary
                pieplot_costs_maininfo=(eval(f"f'''{langdict_plotp['costs_piechart_main'][0]}'''"),2,file_resultpath+langdict_plotp['costs_piechart_main'][1])

                plotinfo_pieplot_costs=(pieplot_costs_maininfo,tuple(pieplot_costs_subplotinfo)) #transform subplotlist into tuple
                self.plotinfo_piechart[element_name]=[(tuple(pieplot_costs_finaldata),plotinfo_pieplot_costs)] #transform final datalist into tuple

################################################################### detailed income plots if more than 2 income categories present ##############################

            #plot detailed infos for multiple sources of income
            if plot_revenues:
                #plot income categories as cost plot
                self.plotinfo_costs[element_name].append((total_revenues,eval(f"f'''{langdict_plotp['revenues_costplot'][0]}'''"),file_resultpath+langdict_plotp['revenues_costplot'][1]))
   
                #Create pie plot for multiple sources of income (right without standard salary)
                
                ##Pie income without wages (right side)
                income_nowage=total_revenues[total_revenues['cat'].str.contains(langdict_plotp['revenues_adjust_words1'][0])==False].reset_index(drop=True) ##Get income without wages/salaries
                income_nowage=income_nowage.assign(ppt=(income_nowage['val']*100/income_nowage['val'].sum()).round(2))
                income_nowage.drop(['main cat','val','val_month'],axis=1,inplace=True)
                income_pie_nowage=income_nowage.loc[income_nowage['ppt']>=2.5].copy()

                #Append sum of cost parts <2%, if sum is >0:
                if sum(income_nowage.loc[income_nowage['ppt']<2.5]['ppt'])>0:
                    income_pie_nowage=income_pie_nowage.append(pd.DataFrame([[langdict_plotp['piechart_2%name'][0],sum(income_nowage.loc[income_nowage['ppt']<2.5]['ppt'])]],columns=list(income_nowage.columns)),ignore_index=True)
                else:
                    pass

                ##Pie costs with wages (left side)
                income_wage=total_revenues.copy()
                income_wage=income_wage.assign(ppt=(income_wage['val']*100/income_wage['val'].sum()).round(2))
                income_wage.drop(['main cat','val','val_month'],axis=1,inplace=True)
                income_pie_wage=income_wage.loc[income_wage['ppt']>=2.5].copy()

                #Append sum of cost parts <2%, if sum is >0:
                if sum(income_wage.loc[income_wage['ppt']<2.5]['ppt'])>0:
                    income_pie_wage=income_pie_wage.append(pd.DataFrame([[langdict_plotp['piechart_2%name'][0],sum(income_wage.loc[income_wage['ppt']<2.5]['ppt'])]],columns=list(income_wage.columns)),ignore_index=True)
                else:
                    pass

                pieplot_income_data=(income_pie_wage,income_pie_nowage,'','')
                pieplot_income_maininfo=(eval(f"f'''{langdict_plotp['revenues_piechart_main'][0]}'''"),1,file_resultpath+langdict_plotp['revenues_piechart_main'][1])
                
                #create subplotinfo list
                pieplot_income_subplotinfo=[]
                for i in range(0,4):
                    pieplot_income_subplotinfo.append(langdict_plotp['revenues_piechart_sub'][i])
                plotinfo_pieplot_income=(pieplot_income_maininfo,tuple(pieplot_income_subplotinfo))
                self.plotinfo_piechart[element_name].append((pieplot_income_data,plotinfo_pieplot_income)) 
                
               
            else: # no action needed
                pass


################################################################### create overview plot with top3-income sources and main costs #################################


            ##Prepare TOP3-Plots:
            if self.plotting_choice[element_name]=='complete':
                
                ##create Top3-List (depending on length of total_revenues list) (left side of plot)


                if plot_revenues:
                    self.top3[element_name]=total_revenues.loc[0:2].copy()
                else:
                    self.top3[element_name]=total_revenues.copy()
                #get top3-main cost categories
                top3_maincosts=main_cost_total.loc[0:2].copy()
                top3_maincosts.columns=['cat','val','val_month'] #rename columns to get it plotted
                self.top3[element_name].drop('main cat',axis=1,inplace=True) #drop main cat axis for further processing
                self.top3[element_name]=self.top3[element_name].append(top3_maincosts,ignore_index=True) #append both data frames

                
                ##Adjusted TOP3 without investments / get rent and total balance
                list_searchwords=[langdict_plotp['overviewplot_searchwords'][0],langdict_plotp['overviewplot_searchwords'][1]]
                top3_adj=main_cat_data[main_cat_data['main cat'].isin(list_searchwords)].copy()
                
                # ##make values positive for category living
                 
                #make values positive for category living
                top3_adj.loc[top3_adj['main cat']==langdict_plotp['overviewplot_searchwords'][0],['val','val_month']]=top3_adj.loc[top3_adj['main cat']==langdict_plotp['overviewplot_searchwords'][0],['val','val_month']].abs()
                
                #get net total income
                list_searchwords=list_searchwords+[langdict_plotp['overviewplot_searchwords'][2]]#add investments to searchword list
                total_net_income=main_cat_data[(main_cat_data['main cat'].isin(list_searchwords)==False)&(main_cat_data['val']>0)].copy()
                
                ##get net total of income and invest 
                income_inv_val=total_net_income['val'].sum()+main_cat_data[main_cat_data['main cat'].isin([langdict_plotp['overviewplot_searchwords'][2]])]['val'].sum()
                income_inv_valmonth=total_net_income['val_month'].sum()+main_cat_data[main_cat_data['main cat'].isin([langdict_plotp['overviewplot_searchwords'][2]])]['val_month'].sum()
                
                
                #append net total of invest
                top3_adj=top3_adj.append(pd.DataFrame([[langdict_plotp['overviewplot_newnames'][0], income_inv_val,income_inv_valmonth]],columns=list(top3_adj.columns)),ignore_index=True)
                
                #get net total of remaining costs categories
                remain_cat_neglist=list_searchwords+total_net_income['main cat'].tolist()

                remain_costs_val=abs(main_cat_data[(main_cat_data['main cat'].isin(remain_cat_neglist)==False)]['val'].sum())
                remain_costs_valmonth=abs(subcat_data[(subcat_data['main cat'].isin(remain_cat_neglist)==False)]['val_month'].sum())
                
                #append net total of remaining costs
                top3_adj=top3_adj.append(pd.DataFrame([[langdict_plotp['overviewplot_newnames'][1],remain_costs_val,remain_costs_valmonth]],columns=list(top3_adj.columns)),ignore_index=True)
                
                #sort dataframe
                top3_adj=top3_adj.sort_values(['val'],ascending=False).reset_index(drop=True)
                top3_adj.columns=['cat','val','val_month'] #rename columns to get it plotted#

                self.top3_adj[element_name]=top3_adj
            
            else:#no action needed    
                pass




    
    def plotsplitter(self,element_name,plottype):
        #split large data frames an create subplots (month-data basis stays constant)

        if plottype=='monthplot':
            plottinglist=self.plotinfo_month[element_name].copy()

        elif plottype=='costplot':
            plottinglist=self.plotinfo_costs[element_name].copy()

        elif plottype=='boxplot':
            plottinglist=self.plotinfo_boxplot[element_name].copy()

        elif plottype=='vioplot':
            plottinglist=self.plotinfo_vioplot[element_name].copy()

        
        else:
            pass

        adjusted_plots=[]

        #split dataframes if necessary (necessary if more than 18 categories)
        for plotinfo in plottinglist:
            data_old,title_old,path_old=plotinfo

            if plottype=='vioplot' or plottype=='boxplot':
                #split box and violinplot every 22 categories
                box_cat_nums=data_old['cat'].unique()
               
                if len(box_cat_nums)>22:
                    if len(box_cat_nums)>66:
                        var3=4
                    elif len(box_cat_nums)>44:
                        var3=3
                    else:
                        var3=2

                    plotslicing=True
                    #do first data slice
                    box_slicejump=21 #21 as 0 ist counted as index, as well
                    box_index_new=data_old[data_old['cat']==box_cat_nums[box_slicejump]].index[-1]      
                    slice_var=[0,box_index_new+1] #adjustments for boxplot slicing #+1 for upper slice_var as the final line of the last category has to be included (range [x:y) goes up to y but not including y])
                else:#if dataframe has less then 22 cats, do no slicing
                    plotslicing=False

            #slices for cost and monthplots
            else:
                #split month and cost data every 18 entries
                if len(data_old)>18:#0-17=18 (setting >18 (+1) prevents that a single entry dataframe is created)
                    if len(data_old)>54:
                        var3=4
                    elif len(data_old)>36:
                        var3=3
                    else:
                        var3=2
                    slice_var=[0,18]
                    plotslicing=True

                else:#if cost or monthplot has less than 18 entries, do no slicing
                    plotslicing=False


            name_var="I"#enumerator für plots
            sublist=[]

            #start plot sclicing
            if plotslicing:

                for x in range (0,var3):
                    #do slicing and renaming
                    new_data=data_old[slice_var[0]:slice_var[1]] 
                    new_title=title_old+langdict_plotp['boxsplit_partname'][0]+name_var
                    new_path=path_old[:-4]+"_"+name_var+".png"

                    #add subplot to plotting list
                    sublist.append((new_data,new_title,new_path))

                    if plottype=='vioplot' or plottype=='boxplot':
                        #adjust slicer for boxplots (every 22 categories a new plot)  
        
                        if x+2<var3:
                            box_index_old=data_old[data_old['cat']==box_cat_nums[box_slicejump]].index[-1]+1 #row number of last category + 1 row
                            box_slicejump+=22
                            box_index_new=data_old[data_old['cat']==box_cat_nums[box_slicejump]].index[-1]
                        
                        else:
                            box_index_old=data_old[data_old['cat']==box_cat_nums[box_slicejump]].index[-1]+1 #row number of last category + 1 row                       
                            box_index_new=data_old.index[-1]

                        slice_var=[box_index_old,box_index_new+1] #+1 for upper slice_var as the final line of the last category has to be included (range [x:y) goes up to y but not including y])
                    else:
                        #adjust slicer for month&costplot (every 18 entries a new plot)
                        slice_var = [x+18 for x in slice_var]

                    #adjust name enumerator
                    if x==2:
                        name_var='IV'
                    elif x==3:
                        name_var='V'
                    else:
                        name_var=name_var+"I"

            else:
                #add plot without slicing to plotting list (basically equal to old list)
                sublist.append(plotinfo)
        #     
        # #plot data
            for subindex in range(len(sublist)):
                if subindex==0:
                    axadjust=("getval",(0,0))

                else:
                    axadjust=("setval",axvalue)

                #choose plotter
                if plottype=='monthplot':
                    axvalue=plotters.monthplotter(sublist[subindex],axadjust,self.month_data[element_name])

                elif plottype=='costplot':
                    axvalue=plotters.costplotter(sublist[subindex],axadjust,self.month_data[element_name])
                    

                elif plottype=='boxplot':
                    axvalue=plotters.boxplotter(sublist[subindex],axadjust,self.month_data[element_name])

                elif plottype=='vioplot':
                    axvalue=plotters.violinplotter(sublist[subindex],axadjust,self.month_data[element_name])





    def plotdata(self):
        
        for element_name in self.plot_elements:
            #plot loop for every element in plot_elements including savecent, cashbook and holiday
            #every element has its own plot selection saved in plotting choice. Basic choice contains month plot and cost plot
            plot_selection=self.plotting_choice[element_name]
            file_resultpath=self.folder_res[element_name]+self.folder_sep
            ##Plot selection
            ###Plot basic choice (monthplot and costplot)

            #Month plot
            self.plotsplitter(element_name,'monthplot')

            #Categorical cost plot
            self.plotsplitter(element_name,'costplot')

            ###Plot normal choice (basic choice + box & violinplot)

            if plot_selection=='normal' or plot_selection=='complete':

                #Boxplot
                #copy data for possible plot slicing
                box_vioplot_data=self.basis_data[element_name].copy()
                box_vioplot_data=box_vioplot_data.sort_values(['cat']).reset_index()#sort by categories
                #create plotinfo
                self.plotinfo_boxplot[element_name]=[(box_vioplot_data,eval(f"f'''{langdict_plotp['boxplot_info'][0]}'''"),file_resultpath+langdict_plotp['boxplot_info'][1])]
                self.plotsplitter(element_name,'boxplot')

                #Violinplot
                #use same dataframe as for boxplots
                self.plotinfo_vioplot[element_name]=[(box_vioplot_data,eval(f"f'''{langdict_plotp['vioplot_info'][0]}'''"),file_resultpath+langdict_plotp['vioplot_info'][1])]
                self.plotsplitter(element_name,'vioplot')

                if plot_selection=='complete':
                    #complete plot includes top3 overview and pie charts

                    #"TOP3" / Overwiew Plot
                    plotinfo_overview=(eval(f"f'''{langdict_plotp['overviewplot_plotinfo'][0]}'''"),langdict_plotp['overviewplot_plotinfo'][1],langdict_plotp['overviewplot_plotinfo'][2],file_resultpath+langdict_plotp['overviewplot_plotinfo'][3])
                    plotters.overviewplot(self.top3[element_name],self.top3_adj[element_name],self.month_data[element_name],plotinfo_overview)

                    #Pie charts
                    for pie_entry in self.plotinfo_piechart[element_name]: 
                        plotters.pieplotter(pie_entry,self.month_data[element_name])

                else:
                    pass

            else:
                pass


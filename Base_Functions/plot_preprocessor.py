
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
                        
            ##create dataframe containing all income categories for further usage:
            total_income=self.cat_data[element_name][(self.cat_data[element_name]['cat'].str.contains('Urlaub|Gesamtsaldo|Sonstiges|Abhebung|Bargeld')==False)&(self.cat_data[element_name]['val']>0)].copy()
           
            ## prepare cost and month plots for accounts 
            # do specific adjustements for savecents, holidays and cashbook cat_data as these categorial elements are stored in a different manner than normal account cat_data
            if element_name=='Sparcents':
                #savecents cat data differs from other cat_data. Therefore separate handling is necessar
                self.plotinfo_costs[element_name]=[(self.cat_data[element_name],f'Übersicht über die Herkunft und Summe der "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Übersicht Sparcents.png')]#cost plot data & info
                
                #separate month data for possible plot splittung
                month_plot=self.month_data[element_name].copy()
                self.plotinfo_month[element_name]=[(month_plot,f'Absteigend sortierte Aufstellung der "{element_name}" je Monat',self.folder_res[element_name]+self.folder_sep+'Monatliche Sparcents.png')] #month plot data & info
            
            elif element_name=='Urlaube':
                # specific actions necessary to specifically created "holiday" account

                self.cat_data[element_name].loc[self.cat_data[element_name]['cat']=='Gesamtsaldo\nder Periode','cat']='Summe aller\nUrlaubsausgaben'#rename total amount to total holiday spendings in cat_data
                cost_total=self.cat_data[element_name]
                cost_total[['val','val_month']]=cost_total[['val','val_month']].abs() #do sign reversal for better cost depicting 
                cost_total=cost_total.sort_values('val',ascending=False).reset_index(drop=True) #sorting descending
                self.plotinfo_costs[element_name]=[(cost_total,f'Kostensummen der einzelnen Urlaube',self.folder_res[element_name]+self.folder_sep+'Übersicht Urlaubskosten.png')] #cost plot data & info
                
                #separate month data for possible plot splittung
                month_plot=self.month_data[element_name].copy()
                self.plotinfo_month[element_name]=[(month_plot,'Monatliche Aufstellung der Urlaubsausgaben',self.folder_res[element_name]+self.folder_sep+'Monatsaufstellung Urlaube.png')] #month plot data & info

            elif element_name=='Haushaltsbuch':

                cashbook_cats=self.cat_data[element_name].copy()
                cashbook_cats1=cashbook_cats[cashbook_cats.columns[[0,1,2]]] #first cat_dataset (grouped by cost categories)
                cashbook_cats2=cashbook_cats[cashbook_cats.columns[[3,4,5]]] #second cat_dataset (grouped by account types)
                cost_cat1=cashbook_cats1[cashbook_cats1['val'].isnull()==False] #delete null values
                cost_cat2=cashbook_cats2[cashbook_cats2['val_2'].isnull()==False].copy() #delete null values
                cost_cat2.columns=["cat","val","val_month"]

                self.plotinfo_costs[element_name]=[(cost_cat1,'Übersicht über die Bargeldzahlungen nach Kostenkategorien',self.folder_res[element_name]+self.folder_sep+'Übersicht Bargeldzahlungen.png')] #cost plot data & info
                self.plotinfo_costs[element_name].append((cost_cat2,'Übersicht über die Bargeldabhebungen nach Kontokategorie',self.folder_res[element_name]+self.folder_sep+'Übersicht Bargeldabhebungen.png')) #cost plot data & info
                
                #separate month data for possible plot splittung
                month_plot=self.month_data[element_name].copy()
                self.plotinfo_month[element_name]=[(month_plot,'Monatliche Aufstellung der Bargeldzahlungen',self.folder_res[element_name]+self.folder_sep+'Monatsaufstellung Bargeldzahlungen.png')] #month plot data & info
                
            else:##Cost & month plot Main Data
                
                
                #NEW auto-adjust plottypes for excels and concats, if total income is empty
                if (len(total_income)==0)&(self.plotting_choice[element_name]==""):
                    self.plotting_choice[element_name]='normal'
                elif (self.plotting_choice[element_name]==""):
                    self.plotting_choice[element_name]='complete'
                else:
                    pass

                cost_total=self.cat_data[element_name][self.cat_data[element_name]['cat'].isin(total_income['cat'].tolist()+['Gesamtsaldo\nder Periode'])==False].copy()
                cost_total[['val','val_month']]=cost_total[['val','val_month']].abs() #do sign reversal for better cost depicting
                cost_total=cost_total.sort_values('val',ascending=False).reset_index(drop=True) #sorting descending
                self.plotinfo_costs[element_name]=[(cost_total,f'Detaillierte Gesamtübersicht der Kostenkategorien für "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Komplettübersicht Kostenkategorien.png')] #cost plot data & info
                
                #separate month data for possible plot splittung
                month_plot=self.month_data[element_name].copy()
                self.plotinfo_month[element_name]=[(month_plot,f'Aufstellung der Monatssalden für "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Monatsaufstellung.png')] #month plot data & info
           

            ##Prepare TOP3-Plots:
            if 'o' in self.plotting_choice[element_name]:
                
                ##create Top3-List (depending on length of total_income list)
                
                if len(total_income)>3:
                    self.top3[element_name]=total_income.loc[0:2].copy()
                    self.top3[element_name]=self.top3[element_name].append(cost_total.loc[0:2],ignore_index=True)
                else:
                    self.top3[element_name]=total_income.copy()
                    self.top3[element_name]=self.top3[element_name].append(cost_total.loc[0:2],ignore_index=True)

                
                ##Adjusted TOP3 without invest/get rent and total balance
                top3_adj=self.cat_data[element_name][self.cat_data[element_name]['cat'].isin(['Miete','Gesamtsaldo\nder Periode'])].copy()
                ##make values positive for category rent
                top3_adj.loc[top3_adj.cat=='Miete',['val','val_month']]=top3_adj.loc[top3_adj.cat=='Miete',['val','val_month']].abs()
               
                ##get net total of income and invest 
                lohn_inv_val=total_income['val'].sum()+self.cat_data[element_name][self.cat_data[element_name]['cat'].isin(['Aktien-\ngeschäfte','ETFS / Wert-\npapiersparen'])]['val'].sum()
                lohn_inv_valmonth=total_income['val_month'].sum()+self.cat_data[element_name][self.cat_data[element_name]['cat'].isin(['Aktien-\ngeschäfte','ETFS / Wert-\npapiersparen'])]['val_month'].sum()
                
                #append net total of invest
                top3_adj=top3_adj.append(pd.DataFrame([['Einkünfte inkl.\nInvestergebnis', lohn_inv_val,lohn_inv_valmonth]],columns=list(top3_adj.columns)),ignore_index=True)
                
                #get net total of remaining costs
                cost_sum_val=abs(self.cat_data[element_name][self.cat_data[element_name]['cat'].isin(total_income['cat'].tolist()+['Miete','Gesamtsaldo\nder Periode','Aktien-\ngeschäfte','ETFS / Wert-\npapiersparen'])==False]['val'].sum())
                cost_sum_valmonth=abs(self.cat_data[element_name][self.cat_data[element_name]['cat'].isin(total_income['cat'].tolist()+['Miete','Gesamtsaldo\nder Periode','Aktien-\ngeschäfte','ETFS / Wert-\npapiersparen'])==False]['val_month'].sum())

                #append net total of remaining costs
                top3_adj=top3_adj.append(pd.DataFrame([['Restliche Kosten-\npositionen',cost_sum_val,cost_sum_valmonth]],columns=list(top3_adj.columns)),ignore_index=True)
                
                #sort dataframe
                top3_adj=top3_adj.sort_values(['val'],ascending=False).reset_index(drop=True)
                self.top3_adj[element_name]=top3_adj
            
            else:#no action needed    
                pass
            ##Pie Chart holiday-->every account with 'a' or 't'

            cost_hol=cost_total.loc[cost_total['cat'].str.contains('Urlaub')]
            cost_nothol=cost_total.loc[cost_total['cat'].str.contains('Urlaub')==False]
            
            ##Adjust total cost with holidays grouped together
            cost_total_adj=cost_nothol.append(pd.DataFrame([['Urlaube gesamt',sum(cost_hol['val']),sum(cost_hol['val_month'])]], columns=list(cost_nothol.columns)),ignore_index=True)
            cost_total_adj=cost_total_adj.sort_values('val',ascending=False).reset_index(drop=True)

            ##print cost categories with holidays grouped together
            if (len(cost_hol.index)>1) and not (element_name=='Sparcents' or element_name=='Urlaube' or element_name=='Haushaltsbuch'):
                cost_hol_group=cost_total_adj.copy()
                self.plotinfo_costs[element_name].append((cost_hol_group,f'Übersicht der Kostenkategorien mit Urlauben (gesamt) für "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Kostenübersicht Kosten_Urlaube (gesamt).png'))


            ##Pie costs without holidays (right side)
            cost_intermediate_hol=cost_nothol.assign(ppt=(cost_nothol['val']*100/cost_nothol['val'].sum()).round(2))
            cost_intermediate_hol.drop(['val','val_month'],axis=1,inplace=True)
            cost_pie_nothol=cost_intermediate_hol.loc[cost_intermediate_hol['ppt']>=2.0]

            #Append sum of cost parts <2%, if sum is >0:
            if sum(cost_intermediate_hol.loc[cost_intermediate_hol['ppt']<2.0]['ppt'])>0:
                cost_pie_nothol=cost_pie_nothol.append(pd.DataFrame([['Restliche mit <2%',sum(cost_intermediate_hol.loc[cost_intermediate_hol['ppt']<2.0]['ppt'])]],columns=list(cost_intermediate_hol.columns)),ignore_index=True)
            else:
                pass

            ##Pie costs with holidays together (left side)
            cost_intermediate2_hol=cost_total_adj.assign(ppt=(cost_total_adj['val']*100/cost_total_adj['val'].sum()).round(2))
            cost_intermediate2_hol.drop(['val','val_month'],axis=1,inplace=True)
            cost_pie_total_holadj=cost_intermediate2_hol.loc[cost_intermediate2_hol['ppt']>=2.0]

            #Append sum of cost parts <2%, if sum is >0:
            if sum(cost_intermediate2_hol.loc[cost_intermediate2_hol['ppt']<2.0]['ppt'])>0:
                cost_pie_total_holadj=cost_pie_total_holadj.append(pd.DataFrame([['Restliche mit <2%',sum(cost_intermediate2_hol.loc[cost_intermediate2_hol['ppt']<2.0]['ppt'])]],columns=list(cost_intermediate2_hol.columns)),ignore_index=True)
            else:
                pass

            data_pie_hol=(cost_pie_total_holadj,cost_pie_nothol)
            plotinfo_pieplot_hol=(f'Tortendiagramm Kostenkategorien >2% Anteil für "{element_name}"','Anteilsübersicht mit Urlauben zusammengefasst','Anteilsübersicht ohne Urlaube',self.folder_res[element_name]+self.folder_sep+'Tortendiagramm Kostenanteile_Urlaub.png')
            self.plotinfo_piechart[element_name]=[(data_pie_hol,plotinfo_pieplot_hol)]
            
            ##Adjust Cost & pie plots for invest
            if len(self.cat_data[element_name][self.cat_data[element_name]['cat'].isin(['Aktien-\ngeschäfte','ETFS / Wert-\npapiersparen'])].index) > 0:
                cost_hol_group=cost_total_adj.copy()
                cost_notinv=cost_hol_group[cost_hol_group['cat'].isin(['Aktien-\ngeschäfte','ETFS / Wert-\npapiersparen'])==False].reset_index(drop=True)
                self.plotinfo_costs[element_name].append((cost_notinv,f'Detaillierte Übersicht Kostenkategorien mit Urlauben (gesamt) ohne Investkosten für "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Kostenübersicht_ohne Invest.png'))
            
                ##Get second pie plot, if invest is existing
                
                ##Pie costs without invest (right side)
                cost_notinv_adj=cost_total_adj[cost_total_adj['cat'].isin(['Aktien-\ngeschäfte','ETFS / Wert-\npapiersparen'])==False].reset_index(drop=True) ##Get costs without invest with holidays together
                cost_intermediate_inv=cost_notinv_adj.assign(ppt=(cost_notinv_adj['val']*100/cost_notinv_adj['val'].sum()).round(2))
                cost_intermediate_inv.drop(['val','val_month'],axis=1,inplace=True)
                cost_pie_notinv=cost_intermediate_inv.loc[cost_intermediate_inv['ppt']>=2.0]

                #Append sum of cost parts <2%, if sum is >0:
                if sum(cost_intermediate_inv.loc[cost_intermediate_inv['ppt']<2.0]['ppt'])>0:
                    cost_pie_notinv=cost_pie_notinv.append(pd.DataFrame([['Restliche mit <2%',sum(cost_intermediate_inv.loc[cost_intermediate_inv['ppt']<2.0]['ppt'])]],columns=list(cost_intermediate_inv.columns)),ignore_index=True)
                else:
                    pass

                ##Pie costs with invest (left side)
                cost_intermediate2_inv=cost_total_adj.assign(ppt=(cost_total_adj['val']*100/cost_total_adj['val'].sum()).round(2))
                cost_intermediate2_inv.drop(['val','val_month'],axis=1,inplace=True)
                cost_pie_total_invadj=cost_intermediate2_inv.loc[cost_intermediate2_inv['ppt']>=2.0]

                #Append sum of cost parts <2%, if sum is >0:
                if sum(cost_intermediate2_inv.loc[cost_intermediate2_inv['ppt']<2.0]['ppt'])>0:
                    cost_pie_total_invadj=cost_pie_total_invadj.append(pd.DataFrame([['Restliche mit <2%',sum(cost_intermediate2_inv.loc[cost_intermediate2_inv['ppt']<2.0]['ppt'])]],columns=list(cost_intermediate2_inv.columns)),ignore_index=True)
                else:
                    pass

                data_pie_inv=(cost_pie_total_invadj,cost_pie_notinv)
                plotinfo_pieplot_inv=(f'Tortendiagramm Kostenkategorien >2% Anteil für "{element_name}"','Anteilsübersicht mit Invest','Anteilsübersicht ohne Invest',self.folder_res[element_name]+self.folder_sep+'Tortendiagramm Kostenanteile_Invest.png')
                self.plotinfo_piechart[element_name].append((data_pie_inv,plotinfo_pieplot_inv))                             

            else:#no action needed
                pass
            
            #plot detailed infos for multiple sources of income
            if len(total_income)>3 and not (element_name=='Sparcents' or element_name=='Urlaube'or element_name=='Haushaltsbuch'):
                #plot income categories as cost plot
                self.plotinfo_costs[element_name].append((total_income,f'Detaillierte Übersicht über die verschiedenen Einkommensquellen für "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Einkommensübersicht.png'))
   
                #Create pie plot for multiple sources of income (right without standard salary)
                
                ##Pie imcome without wages (right side)
                income_nowage=total_income[total_income['cat'].isin(['Lohn','Gehalt'])==False].reset_index(drop=True) ##Get costs without invest with holidays together
                income_nowage=income_nowage.assign(ppt=(income_nowage['val']*100/income_nowage['val'].sum()).round(2))
                income_nowage.drop(['val','val_month'],axis=1,inplace=True)
                income_pie_nowage=income_nowage.loc[income_nowage['ppt']>=2.0].copy()

                #Append sum of cost parts <2%, if sum is >0:
                if sum(income_nowage.loc[income_nowage['ppt']<2.0]['ppt'])>0:
                    income_pie_nowage=income_pie_nowage.append(pd.DataFrame([['Restliche mit <2%',sum(income_nowage.loc[income_nowage['ppt']<2.0]['ppt'])]],columns=list(income_nowage.columns)),ignore_index=True)
                else:
                    pass

                ##Pie costs with wages (left side)
                income_wage=total_income.copy()
                income_wage=income_wage.assign(ppt=(income_wage['val']*100/income_wage['val'].sum()).round(2))
                income_wage.drop(['val','val_month'],axis=1,inplace=True)
                income_pie_wage=income_wage.loc[income_wage['ppt']>=2.0].copy()

                #Append sum of cost parts <2%, if sum is >0:
                if sum(income_wage.loc[income_wage['ppt']<2.0]['ppt'])>0:
                    income_pie_wage=income_pie_wage.append(pd.DataFrame([['Restliche mit <2%',sum(income_wage.loc[income_wage['ppt']<2.0]['ppt'])]],columns=list(income_wage.columns)),ignore_index=True)
                else:
                    pass

                data_pie_income=(income_pie_wage,income_pie_nowage)
                plotinfo_pieplot_income=(f'Tortendiagramm Einkommensquellen >2% Anteil für "{element_name}"','Anteilsübersicht mit Lohn / Gehalt','Anteilsübersicht ohne Lohn / Gehalt',self.folder_res[element_name]+self.folder_sep+'Tortendiagramm Einkommensquellen.png')
                self.plotinfo_piechart[element_name].append((data_pie_income,plotinfo_pieplot_income))   
                
                
                
            else: # no action needed
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
                    new_title=title_old+" Teil "+name_var
                    new_path=path_old[:-4]+"_"+name_var+".png"

                    #add subplot to plotting list
                    sublist.append((new_data,new_title,new_path))

                    if plottype=='vioplot' or plottype=='boxplot':
                        #adjust slicer for boxplots (every 22 categories a new plot)  
                        if x+2<var3:
                            box_index_old=data_old[data_old['cat']==box_cat_nums[box_slicejump]].index[-1]+1 #row number of last category + 1 row
                            box_slicejump+=22 #box_slice_jump + 22 as every 22 categories a new plot is generated
                            box_index_new=data_old[data_old['cat']==box_cat_nums[box_slicejump]].index[-1]
                        
                        else:
                            box_index_old=data_old[data_old['cat']==box_cat_nums[box_slicejump]].index[-1]+1 #row number of last category + 1 row                       
                            box_index_new=data_old.index[-1]

                                              
                        slice_var=[box_index_old,box_index_new+1]#+1 for upper slice_var as the final line of the last category has to be included (range [x:y) goes up to y but not including y])
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
                self.plotinfo_boxplot[element_name]=[(box_vioplot_data,f'Boxplot aller Umsätze nach Kategorie für "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Boxplot.png')]
                self.plotsplitter(element_name,'boxplot')

                #Violinplot
                #use same dataframe as for boxplots
                self.plotinfo_vioplot[element_name]=[(box_vioplot_data,f'Violinplot aller Umsätze nach Kategorie für "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Violinplot.png')]
                self.plotsplitter(element_name,'vioplot')

                if plot_selection=='complete':
                    #complete plot includes top3 overview and pie charts

                    #"TOP3" / Overwiew Plot
                    plotinfo_overview=(f'Überblicksübersicht Kosten und Einkünfte für "{element_name}"','Einkünfte und TOP-Kostenblöcke','Einkünfte inkl. Saldo Kapitalanlagen\n & Restliche Kostenpositionen',self.folder_res[element_name]+self.folder_sep+'Überblicksübersicht.png')
                    plotters.overviewplot(self.top3[element_name],self.top3_adj[element_name],self.month_data[element_name],plotinfo_overview)

                    #Pie charts
                    for pie_entry in self.plotinfo_piechart[element_name]: 
                        plotters.pieplotter(pie_entry,self.month_data[element_name])

                else:
                    pass

            else:
                pass


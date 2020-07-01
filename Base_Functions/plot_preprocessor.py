
'''This file is needed to preprocess the submitted data to fit the needed format for the plotting functions. Cost data is separated with regards to investment costs and total costs.
Pie relative portion charts are created for cost components >2%, and shown separately according to investment and holiday costs with regards to total costs.'''

from Base_Functions import plotters
import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
import platform 
import seaborn as sns
import matplotlib.pyplot as plt 


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
        self.plotinfo_piechart={}
        self.folder_sep=folder_sep
        self.folder_res=accounts_data.folder_res

        
    ##Prepare Plot-Data:
    def makeplotdata(self):
        
        ##Shuffle through items:
        for item in range(0,len(self.plot_elements)):
            element_name=self.plot_elements[item]


            ##create dataframe containing all income categories:
            total_income=self.cat_data[element_name][(self.cat_data[element_name]['cat'].str.contains('Urlaub|Gesamtsaldo|Sonstiges')==False)&(self.cat_data[element_name]['val']>0)].copy()
            
            #NEW auto-adjust plottypes, if total income is empty
           
            ##adjust plot_data if savecent was selected
            if element_name=='Sparcents':
                self.plotinfo_costs[element_name]=[(self.cat_data[element_name],f'Übersicht über die Herkunft und Summe der "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Übersicht Sparcents.jpg')]
                self.plotinfo_month[element_name]=(f'Aufstellung der "{element_name}" nach Monaten',self.folder_res[element_name]+self.folder_sep+'Monatliche Sparcents.jpg')
            
            else:##Cost & month plot Main Data
                #NEW auto-adjust plottypes for excels and concats, if total income is empty
                if (len(total_income)==0)&(self.plotting_choice[element_name]==[]):
                    self.plotting_choice[element_name]=['c','m','v']
                elif (self.plotting_choice[element_name]==[]):
                    self.plotting_choice[element_name]=['a','o']
                else:
                    pass

                cost_total=self.cat_data[element_name][self.cat_data[element_name]['cat'].isin(total_income['cat'].tolist()+['Gesamtsaldo\nder Periode'])==False].copy()
                cost_total[['val','val_month']]=cost_total[['val','val_month']].abs()
                cost_total=cost_total.sort_values('val',ascending=False).reset_index(drop=True)
                self.plotinfo_costs[element_name]=[(cost_total,f'Detaillierte Gesamtübersicht der Kostenkategorien für "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Komplettübersicht Kostenkategorien.jpg')]
                self.plotinfo_month[element_name]=(f'Monatsaufstellung für "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Monatsaufstellung.jpg')
           

            ##Prepare TOP3-Plots:
            if 'o' in self.plotting_choice[element_name]:
                
                ##create Top3-List (depending on length of total_income list)
                
                if len(total_income)>3:
                    self.top3[element_name]=total_income.loc[0:3].copy()
                    self.top3[element_name]=self.top3[element_name].append(cost_total[0:3],ignore_index=True)
                else:
                    self.top3[element_name]=total_income.copy()
                    self.top3[element_name]=self.top3[element_name].append(cost_total[0:3],ignore_index=True)

                
                ##Adjusted TOP3 without invest/get rent and total balance
                top3_adj=self.cat_data[element_name][self.cat_data[element_name]['cat'].isin(['Miete','Gesamtsaldo\nder Periode'])].copy()
               
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
            if (len(cost_hol.index)>1) and not (element_name=='Sparcents'):
                cost_hol_group=cost_total_adj.copy()
                self.plotinfo_costs[element_name].append((cost_hol_group,f'Übersicht der Kostenkategorien mit Urlauben (gesamt) für "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Kostenübersicht Kosten_Urlaube (gesamt).jpg'))


            ##Pie costs without holidays (right side)
            cost_intermediate_hol=cost_nothol.assign(ppt=(cost_nothol['val']*100/cost_nothol['val'].sum()).round(2))
            cost_intermediate_hol.drop(['val','val_month'],axis=1,inplace=True)
            cost_pie_nothol=cost_intermediate_hol.loc[cost_intermediate_hol['ppt']>=2.0]
            cost_pie_nothol=cost_pie_nothol.append(pd.DataFrame([['Restliche mit <2%',sum(cost_intermediate_hol.loc[cost_intermediate_hol['ppt']<2.0]['ppt'])]],columns=list(cost_intermediate_hol.columns)),ignore_index=True)

            ##Pie costs with holidays together (left side)
            cost_intermediate2_hol=cost_total_adj.assign(ppt=(cost_total_adj['val']*100/cost_total_adj['val'].sum()).round(2))
            cost_intermediate2_hol.drop(['val','val_month'],axis=1,inplace=True)
            cost_pie_total_holadj=cost_intermediate2_hol.loc[cost_intermediate2_hol['ppt']>=2.0]
            cost_pie_total_holadj=cost_pie_total_holadj.append(pd.DataFrame([['Restliche mit <2%',sum(cost_intermediate2_hol.loc[cost_intermediate2_hol['ppt']<2.0]['ppt'])]],columns=list(cost_intermediate2_hol.columns)),ignore_index=True)
            
            data_pie_hol=(cost_pie_total_holadj,cost_pie_nothol)
            plotinfo_pieplot_hol=(f'Tortendiagramm Kostenkategorien >2% Anteil für "{element_name}"','Anteilsübersicht mit Urlauben zusammengefasst','Anteilsübersicht ohne Urlaube',self.folder_res[element_name]+self.folder_sep+'Tortendiagramm Kostenanteile_Urlaub.jpg')
            self.plotinfo_piechart[element_name]=[(data_pie_hol,plotinfo_pieplot_hol)]
            
            ##Adjust Cost & pie plots for invest
            if len(self.cat_data[element_name][self.cat_data[element_name]['cat'].isin(['Aktien-\ngeschäfte','ETFS / Wert-\npapiersparen'])].index) > 0:
                cost_hol_group=cost_total_adj.copy()
                cost_notinv=cost_hol_group[cost_hol_group['cat'].isin(['Aktien-\ngeschäfte','ETFS / Wert-\npapiersparen'])==False].reset_index(drop=True)
                self.plotinfo_costs[element_name].append((cost_notinv,f'Detaillierte Übersicht Kostenkategorien mit Urlauben (gesamt) ohne Investkosten für "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Kostenübersicht_ohne Invest.jpg'))
            
                ##Get second pie plot, if invest is existing
                
                ##Pie costs without invest (right side)
                cost_notinv_adj=cost_total_adj[cost_total_adj['cat'].isin(['Aktien-\ngeschäfte','ETFS / Wert-\npapiersparen'])==False].reset_index(drop=True) ##Get costs without invest with holidays together
                cost_intermediate_inv=cost_notinv_adj.assign(ppt=(cost_notinv_adj['val']*100/cost_notinv_adj['val'].sum()).round(2))
                cost_intermediate_inv.drop(['val','val_month'],axis=1,inplace=True)
                cost_pie_notinv=cost_intermediate_inv.loc[cost_intermediate_inv['ppt']>=2.0]
                cost_pie_notinv=cost_pie_notinv.append(pd.DataFrame([['Restliche mit <2%',sum(cost_intermediate_inv.loc[cost_intermediate_inv['ppt']<2.0]['ppt'])]],columns=list(cost_intermediate_inv.columns)),ignore_index=True)

                ##Pie costs with invest (left side)
                cost_intermediate2_inv=cost_total_adj.assign(ppt=(cost_total_adj['val']*100/cost_total_adj['val'].sum()).round(2))
                cost_intermediate2_inv.drop(['val','val_month'],axis=1,inplace=True)
                cost_pie_total_invadj=cost_intermediate2_inv.loc[cost_intermediate2_inv['ppt']>=2.0]
                cost_pie_total_invadj=cost_pie_total_invadj.append(pd.DataFrame([['Restliche mit <2%',sum(cost_intermediate2_inv.loc[cost_intermediate2_inv['ppt']<2.0]['ppt'])]],columns=list(cost_intermediate2_inv.columns)),ignore_index=True)
                
                data_pie_inv=(cost_pie_total_invadj,cost_pie_notinv)
                plotinfo_pieplot_inv=(f'Tortendiagramm Kostenkategorien >2% Anteil für "{element_name}"','Anteilsübersicht mit Invest','Anteilsübersicht ohne Invest',self.folder_res[element_name]+self.folder_sep+'Tortendiagramm Kostenanteile_Invest.jpg')
                self.plotinfo_piechart[element_name].append((data_pie_inv,plotinfo_pieplot_inv))                             

            else:#no action needed
                pass
            
            #plot detailed infos for multiple sources of income
            if len(total_income)>3:
                #plot income categories as cost plot
                self.plotinfo_costs[element_name].append((total_income,f'Detaillierte Übersicht über die verschiedenen Einkommensquellen für "{element_name}"',self.folder_res[element_name]+self.folder_sep+'Einkommensübersicht.jpg'))
                
                #Create pie plot for multiple sources of income (right without standard salary)
                
                ##Pie imcome without wages (right side)
                income_nowage=total_income[total_income['cat'].isin(['Lohn','Gehalt'])==False].reset_index(drop=True) ##Get costs without invest with holidays together
                income_nowage=income_nowage.assign(ppt=(income_nowage['val']*100/income_nowage['val'].sum()).round(2))
                income_nowage.drop(['val','val_month'],axis=1,inplace=True)
                income_pie_nowage=income_nowage.loc[income_nowage['ppt']>=2.0].copy()
                income_pie_nowage=income_pie_nowage.append(pd.DataFrame([['Restliche mit <2%',sum(income_nowage.loc[income_nowage['ppt']<2.0]['ppt'])]],columns=list(income_nowage.columns)),ignore_index=True)

                ##Pie costs with wages (left side)
                income_wage=total_income.copy()
                income_wage=income_wage.assign(ppt=(income_wage['val']*100/income_wage['val'].sum()).round(2))
                income_wage.drop(['val','val_month'],axis=1,inplace=True)
                income_pie_wage=income_wage.loc[income_wage['ppt']>=2.0].copy()
                income_pie_wage=income_pie_wage.append(pd.DataFrame([['Restliche mit <2%',sum(income_wage.loc[income_wage['ppt']<2.0]['ppt'])]],columns=list(income_wage.columns)),ignore_index=True)

                data_pie_income=(income_pie_wage,income_pie_nowage)
                plotinfo_pieplot_income=(f'Tortendiagramm Einkommensquellen >2% Anteil für "{element_name}"','Anteilsübersicht mit Lohn / Gehalt','Anteilsübersicht ohne Lohn / Gehalt',self.folder_res[element_name]+self.folder_sep+'Tortendiagramm Einkommensquellen.jpg')
                self.plotinfo_piechart[element_name].append((data_pie_income,plotinfo_pieplot_income))   
                
                
                
            else: # no action needed
                pass

    def plotdata(self):
        
        for item in range(0,len(self.plot_elements)):
            element_name=self.plot_elements[item]
            for choice in range(0,len(self.plotting_choice[element_name])):
                
                plot_selection=self.plotting_choice[element_name][choice]
                
                ##Plot selection
                #Boxplot
                if plot_selection=='b':
                    boxplottitle=f'Umsatzübersicht (Boxplot) nach Kategorie für "{element_name}"'
                    printname_box=self.folder_res[element_name]+self.folder_sep+'Boxplot Übersicht.jpg'
                    plotters.boxplotter(self.basis_data[element_name],self.month_data[element_name],boxplottitle,printname_box)

                #Violinplot
                elif plot_selection=='v':
                    
                    violintitle=f'Detaillierte Umsatzübersicht (Violinplot) nach Kategorie für "{element_name}"'
                    printname_vio=self.folder_res[element_name]+self.folder_sep+'Violinplot Übersicht.jpg'
                    plotters.violinplotter(self.basis_data[element_name],self.month_data[element_name],violintitle,printname_vio)

                #Monthplot
                elif plot_selection=='m':

                        plotters.monthplotter(self.plotinfo_month[element_name],self.month_data[element_name])

                #TOP3-Plots
                elif plot_selection=='o':
                    plotinfo_overview=(f'Überblicksübersicht Kosten und Einkünfte für "{element_name}"','Einkünfte und TOP-Kostenblöcke','Einkünfte inkl. Saldo Kapitalanlagen\n & Restliche Kostenpositionen',self.folder_res[element_name]+self.folder_sep+'Überblickübersicht.jpg')
                    plotters.overviewplot(self.top3[element_name],self.top3_adj[element_name],self.month_data[element_name],plotinfo_overview)

                #Categorical cost plot
                elif plot_selection=='c':
                    for cost_entry in range(0,len(self.plotinfo_costs[element_name])):
                        cost_plotinfo=self.plotinfo_costs[element_name][cost_entry]                        
                        plotters.costplotter(cost_plotinfo,self.month_data[element_name])
                        
                #Pie chart
                elif plot_selection=='t':
                    for pie_entry in range(0,len(self.plotinfo_piechart[element_name])):
                        pie_plotinfo=self.plotinfo_piechart[element_name][pie_entry]  
                        plotters.pieplotter(pie_plotinfo,self.month_data[element_name])
                #Alltogether
                else: 
                    #Boxplot
                    boxplottitle=f'Umsatzübersicht (Boxplot) nach Kategorie für "{element_name}"'
                    printname_box=self.folder_res[element_name]+self.folder_sep+'Boxplot Übersicht.jpg'
                    plotters.boxplotter(self.basis_data[element_name],self.month_data[element_name],boxplottitle,printname_box)

                    #Violinplot
                    violintitle=f'Detaillierte Umsatzübersicht (Violinplot) nach Kategorie für "{element_name}"'
                    printname_vio=self.folder_res[element_name]+self.folder_sep+'Violinplot Übersicht.jpg'
                    plotters.violinplotter(self.basis_data[element_name],self.month_data[element_name],violintitle,printname_vio)

                    #Month plot
                    plotters.monthplotter(self.plotinfo_month[element_name],self.month_data[element_name])
                    
                    #Categorical cost plot
                    for cost_entry in range(0,len(self.plotinfo_costs[element_name])):
                        cost_plotinfo=self.plotinfo_costs[element_name][cost_entry]                        
                        plotters.costplotter(cost_plotinfo,self.month_data[element_name])
                        
                    #Pie chart
                    for pie_entry in range(0,len(self.plotinfo_piechart[element_name])):
                        pie_plotinfo=self.plotinfo_piechart[element_name][pie_entry]  
                        plotters.pieplotter(pie_plotinfo,self.month_data[element_name])

'''KYSA - Know your spendings application. Small lightweight software to analyse account transactions. Daniel Krezdorn 2020'''


'''This is the main script started by the user. After asking whether data shall be processed or just plotted the data is categorized and preprocessed for plotting.
If data is just read in for plotting the user can choose between the different types of plots. For raw data from csv-files beeing processed the plotting choice is predetermined.
After preprocessing the data is saved as excel files in the same folder as the plots. Plot data-format is *.jpg. Have fun using the script'''




from Base_Functions import data_processor as datp
from Base_Functions import GUI_builder as guib
from Base_Functions import plot_preprocessor as pltp

import numpy as np
import pandas as pd
import datetime
import locale
import re


# #create start window

mainwindow=guib.Main_Window()
#save variables

main_select=mainwindow.importtype_var.get()
holiday=mainwindow.holiday_var.get()
do_savecent=mainwindow.savecent_var.get()
concatting_term=mainwindow.csv_concat_var.get()
concatting_longterm=mainwindow.xlsx_concat_var.get()

#check for window closure
if not main_select=='close_program':
    accounts_data=mainwindow.accounts_data

    # #concat holiday data
    if holiday==1:
        accounts_data.bundle_holiday()

    else:#no action needed
        pass


    #concat data if selected
    if concatting_term==1:
        input_list_term=accounts_data.imported_files
        concat_choice=guib.concat_Window(input_list_term)
        concat_list_term=concat_choice.concat_list
        if not concat_list_term==[]:
            accounts_data.concatter(concat_list_term)
    else:#no action needed
        pass

    if concatting_longterm==1:
        #get files already processed
        processed_data=list(accounts_data.basis_data.keys())
        #import excels for longterm
        longterm_import=guib.Longtermimport_Window(accounts_data)

        #get filenames of filenames list
        imported_list=longterm_import.successlist
        #check if importing process was successful
        if not imported_list==[]:

            #get filenames of filenames list
            imported_names=[]
            for item in imported_list:
                filename,filepath=item
                imported_names.append(filename)
            
            iput_list_longterm=processed_data+imported_names
            concat_longterm_choice=guib.concat_Window(iput_list_longterm)

            concat_list_longterm=concat_longterm_choice.concat_list
            print(concat_list_longterm)
            if not concat_list_longterm==[]:
                accounts_data.concatter(concat_list_longterm)
            else:#no action needed
                pass
            print(accounts_data.basis_data.keys())

    #make categorical sorting
    accounts_data.month_cat_maker()
    #action if savecent_calculation if selected
    if do_savecent==1:
        accounts_data.savecent_calculation()

    else:#no action needed
            pass

    #create folders and excel output files
    accounts_data.makefolder_excel()

    ##Start plotting section
    plot_data=pltp.Plotters(accounts_data)
    #Preprocess Plotting Data
    guib.process_info('Die Daten werden nun aufbereitet und visualisiert. Bitte haben Sie einen Moment Geduld!')
    plot_data.makeplotdata()
    #Create Plots and save 'jpgs'
    plot_data.plotdata()
    guib.process_info(f'Die Datenauswertung ist jetzt abgeschlossen, die Ergebnisse wurden in folgendem Ordner abgelegt:\n\n{accounts_data.folder_raw}Ergebnisse\n\nDas Programm wird jetzt geschlossen werden.')

   

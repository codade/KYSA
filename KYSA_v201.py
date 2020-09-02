'''KYSA - Know your spendings application. Small lightweight software to analyse account transactions. Daniel Krezdorn 2020'''


'''This is the main script started by the user. After asking whether data shall be processed or just plotted the data is categorized and preprocessed for plotting.
If data is just read in for plotting the user can choose between the different types of plots. For raw data from csv-files beeing processed the plotting choice is predetermined.
After preprocessing the data is saved as excel files in the same folder as the plots. Plot data-format is *.jpg. Have fun using the script'''

from Base_Functions import GUI_final as guib ##change back later
from Base_Functions import plot_preprocessor as pltp
import tkinter as tk
import platform
if platform.system()=='Windows':
    import multiprocess as mtp
else:
    import multiprocessing as mtp
# #create start window

#show info on process status
def process_info(messagetext,messagetyp):
    info_window=tk.Tk()
    info_window.withdraw()

    if messagetyp=='errormessage':
        tk.messagebox.showerror(message=messagetext)
    else:
        tk.messagebox.showinfo(message=messagetext)
    info_window.destroy

#progressbar class running in separate process
class ProgressProc(mtp.Process):

    def __init__(self,queue):
        mtp.Process.__init__(self)
        self.queue=queue
        
    def queuecheck(self):        
        try:
            msg=self.queue.get(0)
            if msg=='hide':
                self.progres_root.withdraw()
                self.progres_root.after(100, self.queuecheck)
            elif msg=='show':
                self.progres_root.deiconify()
                self.progres_root.after(100, self.queuecheck)
        except:
            self.progres_root.after(100, self.queuecheck)

    def run(self):
        from Base_Functions import GUI_final as guib ##change back later
        import tkinter as tk
        self.progres_root=tk.Tk()
        self.progres_root.withdraw()
        test1=guib.Progressbar(self.progres_root)        
        self.queuecheck()
        self.progres_root.mainloop()


if __name__ == '__main__':
    mtp.freeze_support()
    progressqueue=mtp.Queue()
    progressbar=ProgressProc(progressqueue)
    progressbar.start()

    mainwindow=guib.Main_Window()

    #check for window closure
    if not mainwindow.importtype_var.get()=='close_program':

        accounts_data=mainwindow.accounts_data
        
        
        
        #try create folders and excel output files
        try:
            accounts_data.makefolder_excel()
            guib.process_info('Die Daten werden nun aufbereitet und visualisiert. Bitte haben Sie einen Moment Geduld!','infomessage')
            continue_plot=True
            plot_data=pltp.Plotters(accounts_data)
            progressqueue.put('show')
        except:
            guib.process_info('Der Excelexport konnte nicht abgeschlossen werden (Err04)','errormessage')
            continue_plot=False
        
        ##Start plotting section
        #Preprocess Plotting Data
        
        while continue_plot:
            try:
                plot_data.makeplotdata()
            except:
                progressqueue.put('hide')
                guib.process_info(f'Die Datenaufbereitung konnte nicht abgeschlossen werden (Err05). Die Excelexporte wurden im jeweiligen Unterordner unter folgendem Pfad abgelegt:\n\n{accounts_data.folder_raw}Ergebnisse\n\nDas Programm wird jetzt geschlossen.','errormessage')
                break

            #Create Plots and save 'pngs'

            try:
                plot_data.plotdata()
                progressqueue.put('hide')
                guib.process_info(f'Die Datenauswertung ist jetzt abgeschlossen. Die Ergebnisse wurden in folgendem Ordner abgelegt:\n\n{accounts_data.folder_raw}Ergebnisse\n\nDas Programm wird jetzt geschlossen.','infomessage')
            except:
                progressqueue.put('hide')
                guib.process_info(f'Diagramme konnten nicht erstellt werden (Err06). Die Excelexporte wurden im jeweiligen Unterordner unter folgendem Pfad abgelegt:\n\n{accounts_data.folder_raw}Ergebnisse\n\nDas Programm wird jetzt geschlossen.','errormessage')
            break

    progressbar.terminate()


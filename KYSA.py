import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

#multiprocessing
import platform
if platform.system()=='Windows':
    import multiprocess as mtp
else:
    import multiprocessing as mtp

from Base_Functions import GUI_GTK_final as guib
from Base_Functions import plot_preprocessor as pltp






#-------------------------------------- Progressbar Subprocess Class -----------------------------------

class ProgressProcess(mtp.Process):

    def __init__(self,queue):
        #initalize class as process
        mtp.Process.__init__(self)
        self.queue=queue

    def queue_check(self):
        #continously check queue pipeline if the calculation process sent information relevant for progressbar behavior
        try:
            msg,data=self.queue.get(0) #get tuple of latest queue entry. msg states type of action (process start/error/end or show progressbar)

            if 'process' in msg:
                self.progress.userinformation(msg,data)
                self.queue.put(('success',""))
            elif 'show' in msg:
                self.progress.show_all()
        except:
            pass

        return True

    def run(self): #start showing progress bar
        import gi
        from gi.repository import Gtk, GLib

        self.progress = guib.ProgressBarWindow()

        #set timeout for queue checking (timeout means every 100ms the function will be called)
        GLib.timeout_add(100, self.queue_check)
        self.progress.hide()#hide progressbar until plotting Process is started (necessary for different multiprocess handling in Windows and Linux)
        Gtk.main()


#-------------------------------------- Calculation and Plotting mainprocess Class -----------------------------------

class PlottingProcess():

    def __init__(self,queue,accounts_data):

        
        self.queue=queue
        self.accounts_data=accounts_data
        self.plot_data=pltp.Plotters(self.accounts_data)
        self.queue.put(('show','')) #show progressbar

        

    def start_process(self):
        #process script executed as soon as class gets started
        
        self.data_pre_visualisation()
        if self.continue_plot:
            self.data_visualisation()


    def queue_waiting(self):
        # as this process isn't embedded within a GUI a while-loop has to be used to check for queue entries sent from progressbar process 
        # This construction is used provisionally until a better and stable solution is found. Progressbar returns msg=success after process action(start/error/end) has been executed

        while True:
            
            try:
                msg,data=self.queue.get(0)
                if msg=='success':
                    break
               
            except:
                continue


#################################### Data Excel Export and Plotting Halt/Start #################################  
    def data_pre_visualisation(self):
        #export datasets to excel. if successful continue with plotting; if not stop processes
        
        try:
            self.accounts_data.makefolder_excel() 
            self.continue_plot=True #process to next section

            info_text=('Datenaufbereitung abgeschlossen','Die Daten werden nun visualisiert. Bitte haben Sie einen Moment Geduld!')
            self.queue.put(('process_start',info_text)) #send process cintinuation message to progressbar process and wait until "success" is reported back
            time.sleep(0.5)
            self.queue_waiting()
        #     print('start plotting')
        except:
            info_text=('Datenaufbereitung abgebrochen','Der Excelexport konnte nicht abgeschlossen werden (Err04). Das Programm wird geschlossen.')
            self.continue_plot=False #stop programm
            self.queue.put(('process_error',info_text)) #send error message to progressbar and stop program (in porgressbar process)
 
     

#################################### Data Plotting Part #################################     
    def data_visualisation(self):

    #prepare data to be plotted and execute plotting
        while True:
            #prepare plot data. If successful start plotting. Else stop program

            try:
                self.plot_data.makeplotdata() 
            except:
                info_text=('Datenvisualisierung abgebrochen','Die Diagrammvorverarbeitung konnte nicht abgeschlossen werden (Err05). Das Programm wird jetzt geschlossen')
                self.queue.put(('process_error',info_text))  #send error message to progressbar and stop program (in porgressbar process)

                break

            #Create Plots and save 'pngs'

            try:
                self.plot_data.plotdata()
                info_text=('Datenvisualisierung erfolgreich abgeschlossen',f'Die Ergebnisse wurden unter folgendem Ordner abgelegt:\n\n{self.accounts_data.res_dir}\n\nDas Programm wird jetzt geschlossen.')
                self.queue.put(('process_end',info_text))  #send successful data analysis message to progressbar and end program (in porgressbar process)

            except:
                info_text=('Datenvisualisierung abgebrochen','Diagramme konnten nicht erstellt werden (Err06). Das Programm wird jetzt geschlossen')
                self.queue.put(('process_error',info_text)) #send error message to progressbar and stop program (in porgressbar process)
            break



#----------------------------------------------Starting Script--------------------------------------

if __name__ == '__main__':

    mtp.freeze_support() #necessary for windows

    #set variables
    progressqueue=mtp.Queue()
    progressbar = ProgressProcess(progressqueue)


    # necessary differentiation between windows and Linux, as Widnows handles multiprocessing differently (processes are spawned, that's why subprocess has to be started at beginning)
    if platform.system()=='Windows':
        #start hidden progressbar befor Main GUI
        progressbar.start()        
        win = guib.Main_Window()
        Gtk.main()
        
        # Proceed with calculation after Main GUi was closed through script for data analysis 
        if win.proceed:
            plot_process=PlottingProcess(progressqueue, win.mfunc.accounts_data)
            plot_process.start_process()

        #if Main GUI was closed through user via buttons "quit" or "cancel"
        else:
            progressbar.terminate()

    #Linux forks multiple processed. That's why the progressbar process can be started after the Main Window was closed
    elif platform.system()=='Linux':
        win = guib.Main_Window()
        Gtk.main()
        if win.proceed:
            progressbar.start()
            plot_process=PlottingProcess(progressqueue, win.mfunc.accounts_data)
            plot_process.start_process()
        else:
        	pass

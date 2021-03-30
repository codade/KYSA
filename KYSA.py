'''Main script coordinating the opening and closing of the GUI main window and the GUI progressbar. Furthermore the functions for data export
plotting will be started'''

import time

#multiprocessing different Packages on Windows and Darwin
import platform
import multiprocessing as mtp


    
#-------------------------------------- Calculation and Plotting subprocess Class -----------------------------------

class DataProcess(mtp.Process):
    '''Plotting and Excel export process part'''
    def __init__(self, queue, shutdown_event):

        mtp.Process.__init__(self)

        self.queue = queue
        self.accounts_data = None
        self.plot_data = None
        self.continue_plot = False
        self.shutdown_event = shutdown_event

    def run(self):    
        
        self.queue_waiting()

    def queue_waiting(self):
        '''function to constantly check for signal words (msg) in queue'''
       
        while not self.shutdown_event.is_set():
            try:
                msg, data = self.queue.get(block=True, timeout=0.15)

            except Exception:
                continue

            if msg == 'rawimport_start':

                self.import_rawdata(data)
                break

            elif msg == 'start_export':
                
                self.start_exportprocess(data)
                break
                
            elif msg == 'success':
                break

    def import_rawdata(self, data): 


        accounts_data, filenames, importtype = data
        self.accounts_data = accounts_data

        for item in filenames:
            self.accounts_data.process_data(item, importtype)

        self.queue.put(('rawimport_end', self.accounts_data))
        time.sleep(0.3)
        self.queue_waiting()

    def start_exportprocess(self, data):
        '''process script executed as soon as class gets started'''
        from basefunctions import plot_preprocessor as pltp
        
        #hide icon in Mac which is generated after import
        if platform.system() == 'Darwin':
            import AppKit 
            AppKit.NSApp.setActivationPolicy_(2)

        self.accounts_data = data
        self.plot_data =pltp.Plotters(self.accounts_data)

        self.data_pre_visualisation()
        if self.continue_plot:
            self.data_visualisation()
        self.shutdown_event.set()


#################################### Data Excel Export and Plotting Halt/Start #################################
    def data_pre_visualisation(self):
        '''export datasets to excel. if successful continue with plotting; if not stop processes'''

        try:
            self.accounts_data.makefolder_excel()
            self.continue_plot = True #process to next section

            self.queue.put(('process_start', 'data_prep_succ')) #send process continuation message to progressbar process and wait until "success" is reported back
            time.sleep(0.3)
            self.queue_waiting()

        except:
            self.continue_plot = False #stop programm
            self.queue.put(('process_error', 'data_prep_err7')) #send error message to progressbar and stop program (in porgressbar process)




#################################### Data Plotting Part #################################
    def data_visualisation(self):
        '''prepare data to be plotted and execute plotting'''

        while True:
            #prepare plot data. If successful start plotting. Else stop program

            try:
                self.plot_data.makeplotdata()
            except:                
                self.queue.put(('process_error', 'data_vis_err8'))  #send error message to progressbar and stop program (in porgressbar process)
                break
            #Create Plots and save 'pngs'

            try:
                self.plot_data.plotdata()
                self.queue.put(('process_end', 'data_vis_succ'))  #send successful data analysis message to progressbar and end program (in porgressbar process)

            except:
                self.queue.put(('process_error', 'data_vis_err9')) #send error message to progressbar and stop program (in porgressbar process)
            break



#----------------------------------------------Starting Script--------------------------------------

if __name__ == '__main__':

    mtp.freeze_support() #necessary for Windows and Darwin to stop building Gui Windows

    #set variables
    progressqueue = mtp.Queue() #queue needed for the communication between the processes  
    shutdown_event = mtp.Event() #create shutdown event to be used as information about process state in both processes

    data_proc = DataProcess(progressqueue, shutdown_event) #initalize data process class


    data_proc.start()

    #dictionary for user messages posted during plot processing 
    from basefunctions import gui_classes as guicl
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GLib

    #start hidden progressbar process before starting Main GUI
    
    win = guicl.MainWindow(progressqueue)
    Gtk.main()
    data_proc.terminate()
    data_proc.join()

from tkinter import *
from tkinter import ttk
from emails import DailyEmail
from scheduler import Scheduler
import json

class GUI:
    # The GUI should enable the admin to...
    #     - configure which content sources to include in email
    #     - add recipients
    #     - remove recipients
    #     - schedule daily time to send email
    #     - configure sender credentials
    
    
    def __init__(self, root):
        # build the GUI window
        self.__root = root
        self.__root.title('Daily Digest')
        title_label = ttk.Label(self.__root, text = ' \U0001F4DC START YOUR DAY \U0001F4DC',
                                font = 'Algerian 32 bold', justify = CENTER)
        title_label.pack(padx = 5, pady = 5)

        self.__style = ttk.Style()
        self.__style.configure('TButton', font = ('Arial', 12, 'bold'))
        self.__style.configure('Header.TLabel', font = ('Arial', 18, 'bold')) 

        # GUI listbox for recipients
        recipients_frame = ttk.Frame(self.__root)
        recipients_frame.pack(padx = 5, pady = 5)
        self.__add_recipient_var = StringVar()
        self.__recipient_list_var = Variable()
        self.__build_gui_recipients(recipients_frame,
                                   self.__add_recipient_var,
                                   self.__recipient_list_var)

        # GUI elements to schedule delivery time
        schedule_frame = ttk.Frame(self.__root)
        schedule_frame.pack(padx = 5, pady = 5)
        self.__hour_var = StringVar()
        self.__minute_var = StringVar()
        self.__build_gui_schedule(schedule_frame,
                                 self.__hour_var,
                                 self.__minute_var)

        # GUI checkboxes of content to include in email
        contents_frame = ttk.Frame(self.__root)
        contents_frame.pack(padx = 5, pady = 5)
        self.__quote_var = IntVar()
        self.__weather_var = IntVar()
        self.__wikipedia_var = IntVar()
        self.__build_gui_contents(contents_frame,
                                 self.__quote_var, 
                                 self.__weather_var,
                                 self.__wikipedia_var)

        # GUI fields for sender email/password credentials
        sender_frame = ttk.Frame(self.__root)
        sender_frame.pack(padx = 5, pady = 5)
        self.__sender_email_var = StringVar()
        self.__sender_password_var = StringVar()
        self.__build_gui_sender(sender_frame,
                                self.__sender_email_var, 
                                self.__sender_password_var)

        # GUI field for controls
        controls_frame = ttk.Frame(self.__root)
        controls_frame.pack(padx = 5, pady = 5)
        self.__build_gui_controls(controls_frame)

        # set initial values for variables
        try:
           self.__load_settings()
        except: 
            self.__email = DailyEmail()

            self.__add_recipient_var.set('')
            self.__recipient_list_var.set(self.__email.recipient_list)
                
            self.__hour_var.set('07') # defaul send time
            self.__minute_var.set('30')
                
            self.__quote_var.set(self.__email.content['quote']['include'])
            self.__weather_var.set(self.__email.content['weather']['include'])
            self.__wikipedia_var.set(self.__email.content['wikipedia']['include']) 

            self.__sender_email_var.set(self.__email.sender_credentials['email'])
            self.__sender_password_var.set(self.__email.sender_credentials['password'])

        # initialize scheduler
        self.__scheduler = Scheduler()
        self.__scheduler.start()
        self.__root.protocol("WM_DELETE_WINDOW", self.__shutdown) # shuts down the scheduler

    """
    Build GUI elements to add/remove recipients 
    """
    def __build_gui_recipients(self, master, add_recipient_var, recipient_list_var):
        # create GUI widgets
        header = ttk.Label(master, text = 'Recipients:', style = 'Header.TLabel')
        spacer_frame = ttk.Frame(master) # used as GUI spacer

        recipients_entry = ttk.Entry(master, width = 40, textvariable = add_recipient_var)      
        recipients_scrollbar = ttk.Scrollbar(master, orient=VERTICAL)
        recipients_scrollbar.grid(row = 4, column = 1, sticky = N+S+W+E)
        recipient_listbox = Listbox(master, listvariable = recipient_list_var,
                                     selectmode  = 'multiple', width = 40, height = 5)
        recipient_listbox.configure(yscrollcommand=recipients_scrollbar.set)
        recipients_scrollbar.config(command=recipient_listbox.yview)

        add_button = ttk.Button(master, text='Add Recipient', command=self.__add_recipient)
        remove_button = ttk.Button(master, text = 'Remove Selected',
                                   command = lambda: self.__remove_selected_recipients(recipient_listbox.curselection()))
        
        # place GUI widgets using grid geometry manager
        header.grid(row = 0, column = 0)
        recipients_entry.grid(row = 1, column = 0)
        add_button.grid(row=2, column = 0)
        spacer_frame.grid(row = 3, column = 0, pady = 5)
        recipient_listbox.grid(row = 4, column = 0)
        remove_button.grid(row = 5, column = 0)

    """
    Build GUI elements to schedule send time
    """
    def __build_gui_schedule(self, master, hour_var, minute_var):
        # create GUI widgets
        header = ttk.Label(master, text = 'Scheduled Time (24hr):', style = 'Header.TLabel')
        hour_spinbox = ttk.Spinbox(master, from_ = 0, to = 23, textvariable = hour_var,
                                     wrap = True, width = 3, justify = CENTER, font = 'Arial 12')
        minute_spinbox = ttk.Spinbox(master, from_ = 0, to = 59, textvariable = minute_var,
                                     wrap = True, width = 3, justify = CENTER, font = 'Arial 12')

        # place GUI widgets using grid geometry manager
        header.grid(row = 0, column = 0, columnspan = 2)
        hour_spinbox.grid(row = 1, column = 0, sticky = E, padx = 2, pady= 5)
        minute_spinbox.grid(row = 1, column = 1, sticky = W, padx = 2, pady= 5)

    """
    Build GUI elements to select content to include
    """
    def __build_gui_contents(self, master, quote_var, weather_var, wikipedia_var):
        # create GUI widgets
        header = ttk.Label(master, text = 'Digest Contents:', style = 'Header.TLabel')
        quote_checkbox = Checkbutton(master, text = 'Motivational Quote',
                                     onvalue = True, offvalue = False, 
                                     variable = quote_var)
        weather_checkbox = Checkbutton(master, text = 'Weather Forecast',
                                          onvalue = True, offvalue = False, 
                                          variable = weather_var)
        wikipedia_checkbox = Checkbutton(master, text = 'Wikipedia Article',
                                            onvalue = True, offvalue = False, 
                                            variable = wikipedia_var)
       
        # place GUI widgets using grid geometry manager
        header.grid(row = 0, column = 0, columnspan=2)
        quote_checkbox.grid(row = 1, column = 0, sticky = W)
        weather_checkbox.grid(row = 2, column = 0, sticky = W)
        wikipedia_checkbox.grid(row = 2, column = 1, sticky = W)

    """
    Build GUI elements to configure sender credentials
    """
    def __build_gui_sender(self, master, sender_email_var, sender_password_var):
        # create GUI widgets
        header = ttk.Label(master, text = 'Sender Credentials:', style = 'Header.TLabel')
        email_label = ttk.Label(master, text = "Email:")
        email_entry = ttk.Entry(master, width = 40,
                                textvariable = sender_email_var)
        password_label = ttk.Label(master, text = 'Password:')
        password_entry = ttk.Entry(master, width = 40, show = '*',
                                   textvariable = sender_password_var)

        # place GUI widgets using grid geometry manager
        header.grid(row = 0, column = 0, columnspan = 2)
        email_label.grid(row = 1, column = 0, pady = 2, sticky = E)
        email_entry.grid(row = 1, column = 1, pady = 2, sticky = W)
        password_label.grid(row = 2, column = 0, pady = 2, sticky = E)
        password_entry.grid(row = 2, column = 1, pady = 2, sticky = W)   

    """
    Build GUI elements to update settings & manually send digest email
    """
    def __build_gui_controls(self, master):
        # create GUI widgets
        update_button = ttk.Button(master, text = 'Update Settings', command = self.__update_settings)
        send_button = ttk.Button(master, text = 'Manual Send', command = self.__manual_send)
        
        # place GUI widgets using grid geometry manager
        update_button.grid(row = 0, column = 0, padx = 5, pady = 5)
        send_button.grid(row = 0, column = 1, padx = 5, pady = 5)

    """
    Callback function to add recipient
    """
    def __add_recipient(self):
        new_recipient = self.__add_recipient_var.get()
        if new_recipient != '':
            recipient_list = self.__recipient_list_var.get()
            if recipient_list != '':
                self.__recipient_list_var.set(recipient_list + (new_recipient,))
            else:
                self.__recipient_list_var.set([new_recipient])
            self.__add_recipient_var.set('') # clear entry field        

    """
    Callback function to remove selected recipient(s)
    """
    def __remove_selected_recipients(self, selection):
        recipient_list = list(self.__recipient_list_var.get())
        for index in reversed(selection):
            recipient_list.pop(index)
        self.__recipient_list_var.set(recipient_list)

    """
    Callback function to update settings
    """       
    def __update_settings(self):
        print('Updating settings...')
        self.__email.recipient_list = list(self.__recipient_list_var.get())

        self.__email.content['quote']['include'] = self.__quote_var.get()
        self.__email.content['weather']['include'] = self.__weather_var.get()
        self.__email.content['wikipedia']['include'] = self.__wikipedia_var.get()

        self.__email.sender_credentials = {'email': self.__sender_email_var.get(),
                                           'password': self.__sender_password_var.get()}

        self.__scheduler.schedule_task(int(self.__hour_var.get()),
                                        int(self.__minute_var.get()),
                                        self.__email.send_email)

    """
    Callback function to manually send digest email
    """ 
    def __manual_send(self):
        # note: settings are not updated before manual send
        print('Manually sending email digest...')
        self.__email.send_email()
        
    """
    save configuration settings to a file
    """
    # def __save_settings(self,file_path='settings.json'):
    #     settings = {
    #         'recipients': self.__email.recipient_list,
    #         'quote': self.__quote_var.get(),
    #         'weather': self.__weather_var.get(),
    #         'wikipedia': self.__wikipedia_var.get(),
    #         'hour': self.__hour_var.get(),
    #         'minute': self.__minute_var.get(),
    #         'sender_email': self.__sender_email_var.get(),
    #         'sender_password': self.__sender_password_var.get()
    #     }
    #     with open(file_path, 'w') as file:
    #         json.dump(settings, file, indent=4)
    #     print('Settings saved to settings.json')
        
    """
    Load configuration settings from a file
    """
    def __load_settings(self, file_path='settings.json'):
        try:
            with open(file_path, 'r') as file:
                settings = json.load(file)
                self.__recipient_list_var.set(settings['recipients'])
                self.__quote_var.set(settings['quote'])
                self.__weather_var.set(settings['weather'])
                self.__wikipedia_var.set(settings['wikipedia'])
                self.__hour_var.set(settings['hour'])
                self.__minute_var.set(settings['minute'])
                self.__sender_email_var.set(settings['sender_email'])
                self.__sender_password_var.set(settings['sender_password'])
            self.__update_settings()
        except FileNotFoundError:
            print('No settings file found...')
        except json.JSONDecodeError:
            print('Error loading settings file...')

    """
    Shutdown the scheduler before closing the GUI window
    """ 
    def __shutdown(self):
        print('Shutting down the scheduler...')
        self.__scheduler.stop()
        self.__scheduler.join()
        try:
            self.__save_settings()
        except Exception as e:
            self.__root.destroy() # close the GUI window

if __name__ == '__main__':
    root = Tk()
    app = GUI(root)
    root.mainloop()
    
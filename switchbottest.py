import yaml
import json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from src.switchbot import SwitchBotController

class SwitchBotApp(tk.Tk):
    def __init__(self, controller):
        """
        Initializes the SwitchBot Command Sender App.

        :param controller: An instance of the SwitchBotController class.
        """
        super().__init__()
        self.controller = controller
        
        # Set up the main window
        self.title('SwitchBot Command Sender')
        
        # Define variables for storing user inputs
        self.device_id_var = tk.StringVar()
        self.command_var = tk.StringVar()
        self.parameter_var = tk.StringVar()
        self.custom_command_var = tk.StringVar()
        
        # Retrieve device lists from the controller
        device_list = self.controller.get_device_list()['deviceList']
        virtual_device_list = self.controller.get_device_list()['infraredRemoteList']
        # Create a dictionary mapping device names to device IDs
        self.device_dict = {device['deviceName']: device['deviceId'] for device in device_list + virtual_device_list}
        self.device_names = list(self.device_dict.keys())

        # Create and pack widgets for device selection
        tk.Label(self, text='Device:').pack()
        self.device_menu = ttk.Combobox(self, textvariable=self.device_id_var, values=self.device_names)
        self.device_menu.pack()
        
        # Define available commands
        self.commands = ['turnOn', 'turnOff', 'Other']  # Replace with actual commands
        tk.Label(self, text='Command:').pack()
        self.command_menu = ttk.Combobox(self, textvariable=self.command_var, values=self.commands)
        self.command_menu.bind('<<ComboboxSelected>>', self.on_command_selected)
        self.command_menu.pack()

        # Create and pack widgets for custom command input
        tk.Label(self, text='Custom Command:').pack()
        self.custom_command_entry = tk.Entry(self, textvariable=self.custom_command_var)
        self.custom_command_entry.pack()
        self.custom_command_entry.config(state='disabled')  # Initially disabled

        # Create and pack widgets for parameter input
        tk.Label(self, text='Parameter:').pack()
        self.parameter_entry = tk.Entry(self, textvariable=self.parameter_var)
        self.parameter_entry.pack()
        
        # Create and pack buttons for sending and saving commands
        self.send_button = tk.Button(self, text='Send', command=self.send_command)
        self.send_button.pack()
        self.save_button = tk.Button(self, text='Save', command=self.save_command)
        self.save_button.pack()
        
        # Create and pack widgets for managing saved commands
        self.command_list_var = tk.StringVar()
        tk.Label(self, text='Saved Commands:').pack()
        self.command_list_menu = ttk.Combobox(self, textvariable=self.command_list_var, values=[])
        self.command_list_menu.bind('<<ComboboxSelected>>', self.on_command_selected_from_list)
        self.command_list_menu.pack()
        self.open_button = tk.Button(self, text='Open', command=self.open_command)
        self.open_button.pack()

    def on_command_selected(self, event):
        """
        Handles the event when a command is selected from the dropdown.
        Enables or disables custom command entry based on selection.
        """
        if self.command_var.get() == 'Other':
            self.custom_command_entry.config(state='normal')  # Enable entry for custom command
        else:
            self.custom_command_entry.config(state='disabled')  # Disable entry for predefined commands
        
    def save_command(self):
        """
        Saves the current command configuration to a JSON file.
        """
        # Construct the command dictionary
        command = {
            'device_name': self.device_id_var.get(),
            'command': self.command_var.get() if self.command_var.get() != 'Other' else self.custom_command_var.get(),
            'parameter': self.parameter_var.get()
        }
        # Read existing data from file or initialize an empty list
        try:
            with open('config/command_data.json', 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = []
        # Append the new command and save back to the file
        existing_data.append(command)
        with open('config/command_data.json', 'w') as file:
            json.dump(existing_data, file)

    def send_command(self):
        """
        Sends the configured command to the selected device using the controller.
        """
        device_name = self.device_id_var.get()
        device_id = self.device_dict[device_name]
        command = self.command_var.get()
        if command == 'Other':
            command = self.custom_command_var.get()
        parameter = self.parameter_var.get()
        # Send the command and receive response
        response = self.controller.send_command(device_id, command, parameter)
        print(response)  # Display or handle the response as needed

    def open_command(self):
        """
        Opens a file dialog to select and load a saved commands file.
        """
        file_path = filedialog.askopenfilename(title='Select a file', filetypes=[('JSON files', '*.json')])
        if file_path:
            with open(file_path, 'r') as file:
                commands = json.load(file)
            # Extract command names for display
            command_names = [f"{cmd['device_name']} - {cmd['command']}" for cmd in commands]
            self.command_list_menu['values'] = command_names
    
    def on_command_selected_from_list(self, event):
        """
        Handles the event when a saved command is selected from the dropdown.
        Sets the current configuration to the selected command.
        """
        with open('config/command_data.json', 'r') as file:
            commands = json.load(file)
        selected_command_name = self.command_list_var.get()
        selected_command = next((cmd for cmd in commands if f"{cmd['device_name']} - {cmd['command']}" == selected_command_name), None)
        if selected_command:
            self.device_id_var.set(selected_command['device_name'])
            self.command_var.set(selected_command['command'])
            self.parameter_var.set(selected_command['parameter'])

# Usage example
# This part is typically placed outside the class definition, in the main section of the script
with open('config/switchbot_config.yaml', 'r') as file:
    config_data = yaml.safe_load(file)
controller = SwitchBotController(config_data['OPEN_TOKEN'])
app = SwitchBotApp(controller)
app.mainloop()
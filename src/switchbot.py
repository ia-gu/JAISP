import requests
import json

class SwitchBotController:
    # Base URL for the SwitchBot API
    API_HOST = 'https://api.switch-bot.com'
    # Endpoint URL for retrieving the device list
    DEVICE_LIST_URL = f'{API_HOST}/v1.0/devices'

    def __init__(self, token: str):
        """
        Initializes the SwitchBotController with the given API token.

        :param token: The API token for authentication with the SwitchBot API.
        """
        # Set up headers for API requests with authorization token and content type
        self.headers = {
            'Authorization': token,
            'Content-Type': 'application/json; charset=utf8'
        }

    def _get_request(self, url: str) -> dict:
        """
        Performs a GET request to the specified URL and returns the response data.

        :param url: URL to send the GET request to.
        :return: JSON response as a dictionary if successful, empty dictionary otherwise.
        """
        # Perform a GET request to the specified URL
        res = requests.get(url, headers=self.headers)
        data = res.json()
        # Check if the request was successful and return the response data
        if data['message'] == 'success':
            return data
        return {}

    def _post_request(self, url: str, params: dict) -> dict:
        """
        Performs a POST request to the specified URL with given parameters.

        :param url: URL to send the POST request to.
        :param params: Parameters for the POST request.
        :return: JSON response as a dictionary if successful, empty dictionary otherwise.
        """
        # Perform a POST request to the specified URL with the given parameters
        res = requests.post(url, data=json.dumps(params), headers=self.headers)
        data = res.json()
        # Check if the request was successful and return the response data
        if data['message'] == 'success':
            return data
        return {}

    def get_device_list(self) -> dict:
        """
        Retrieves the list of devices registered under the SwitchBot account.

        :return: A dictionary of device details if successful, None otherwise.
        """
        try:
            # Fetch device list using the _get_request method
            return self._get_request(self.DEVICE_LIST_URL)['body']
        except:
            # Return None in case of an exception
            return

    def get_virtual_device_list(self) -> dict:
        """
        Retrieves a list of virtual devices (such as infrared remote devices).

        :return: A dictionary containing the list of virtual devices.
        """
        # Fetch the complete device list
        devices = self.get_device_list()
        # Return the list of infrared remote devices
        return devices.get('infraredRemoteList', {})

    def send_air_condition(self, device_id: str, temperature: int, mode: str, fanspeed: str, power_state: str) -> dict:
        """
        Sends a command to an air conditioning unit through the SwitchBot API.

        :param device_id: The ID of the air conditioner device.
        :param temperature: Desired temperature setting.
        :param mode: Operating mode of the air conditioner.
        :param fanspeed: Fan speed setting.
        :param power_state: Power state of the device ('on' or 'off').
        :return: Response from the API as a dictionary.
        """
        # Construct the URL for sending commands
        url = f'{self.API_HOST}/v1.0/devices/{device_id}/commands'
        # Define the parameters for the command
        params = {
            'command': 'setAll',
            'parameter': f'{temperature},{mode},{fanspeed},{power_state}',
            'commandType': 'command'
        }
        # Send the command using the _post_request method
        return self._post_request(url, params)

    def send_command(self, device_id: str, command: str, parameter: str = 'default', command_type: str = 'command') -> dict:
        """
        Sends a custom command to a specific device through the SwitchBot API.

        :param device_id: The ID of the device to control.
        :param command: The command to send.
        :param parameter: Additional parameters for the command.
        :param command_type: The type of the command.
        :return: Response from the API as a dictionary.
        """
        # Construct the URL for sending commands
        url = f'{self.API_HOST}/v1.0/devices/{device_id}/commands'
        # Define the parameters for the command
        params = {
            'command': command,
            'parameter': parameter,
            'commandType': command_type
        }
        # Send the command using the _post_request method
        return self._post_request(url, params)

    def send_light_on(self, device_id: str) -> dict:
        """
        Sends a command to turn on a light device through the SwitchBot API.

        :param device_id: The ID of the light device.
        :return: Response from the API as a dictionary.
        """
        # Construct the URL for sending the turn on command
        url = f'{self.API_HOST}/v1.0/devices/{device_id}/commands'
        # Define the parameters for the turn on command
        params = {
            'command': 'turnOn',
            'parameter': 'default',
            'commandType': 'command'
        }
        # Send the command using the _post_request method
        return self._post_request(url, params)

    def send_light_off(self, device_id: str) -> dict:
        """
        Sends a command to turn off a light device through the SwitchBot API.

        :param device_id: The ID of the light device.
        :return: Response from the API as a dictionary.
        """
        # Construct the URL for sending the turn off command
        url = f'{self.API_HOST}/v1.0/devices/{device_id}/commands'
        # Define the parameters for the turn off command
        params = {
            'command': 'turnOff',
            'parameter': 'default',
            'commandType': 'command'
        }
        # Send the command using the _post_request method
        return self._post_request(url, params)

    def send_set_color(self, device_id: str, color: list[int] = [255, 255, 255]) -> dict:
        """
        Sends a command to set the color of a light device through the SwitchBot API.

        :param device_id: The ID of the light device.
        :param color: The RGB color values to set (default is white).
        :return: Response from the API as a dictionary.
        """
        # Construct the URL for sending the set color command
        url = f'{self.API_HOST}/v1.0/devices/{device_id}/commands'
        # Define the parameters for the set color command
        params = {
            'command': 'setColor',
            'parameter': f'{color[0]}:{color[1]}:{color[2]}',
            'commandType': 'command'
        }
        # Send the command using the _post_request method
        return self._post_request(url, params)

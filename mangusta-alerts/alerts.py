from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from .utils import id_generator
from .email import send_email
import pandas as pd

class Alert(ABC):
    def __init__(self, name: str, email: str, params: dict()):
        self.name = name
        self.params = params
        self.update_function = []
        self.running = False
        self.email = email
        self.first_run = True   # not used
        self.last_alert = ''
        self.type = ''
        self.description = ''
        self.id = id_generator()
        self.form_controls = [] # list of tuples [(name, value), ...]

    def start(self, message: str = ''):
        if message != '': 
            send_email(self.email, message)
        self.running = True

    def stop(self, message: str = ''):
        if message != '': 
            send_email(self.email, message)
        self.running = False

    def alert(self, message: str):
        send_email(self.email, message)
        self.last_alert = datetime.now()

    def set_type(self, type: str):
        self.type = type

    @abstractmethod
    def monitor_function():
        pass

class Alerts_manager():
    def __init__(self) -> None:
        self.alert_list = []

    def add_alert(self, alert_class: str, name: str, email: str, params: dict()):
        new_alert_class = Alert_types.get(alert_class)
        new_alert = new_alert_class(name=name, email=email, params=params)
        new_alert.set_type(alert_class)
        self.alert_list.append(new_alert)
        
    def delete(self, id: str, message: str = ''):
        index = 0
        for alert in self.alert_list:
            if alert.id == id:
                self.alert_list.pop(index)
                alert.stop(message)
            index += 1

    def get_alert_types(self):
        types_list = list(Alert_types.keys())
        types_list.insert(0, '') # agregamos primer item en blanco para que sea el default en el control del form
        return types_list

    def get_alert_controls(self, alert_class):
        new_alert_class = Alert_types.get(alert_class)
        if new_alert_class == None:
            return []
        new_alert = new_alert_class(name='', email='', params={})
        return new_alert.form_controls

    def get_alert_description(self, alert_class):
        new_alert_class = Alert_types.get(alert_class)
        if new_alert_class == None:
            return ''
        new_alert = new_alert_class(name='', email='', params={})
        return new_alert.description

    def monitor_alerts(self):
        print('Monitoring active alerts')
        for alert in self.alert_list:
            if alert.running is True:
                print(f'--monitoring {alert.name} alert')
                alert.monitor_function()


#### ALERTS Implementations ####

from .defi_llama import get_llama_tvl, get_llama_projects_list
class Llama_TVL_alert(Alert):
    """
    ##  Llama TVL Alerts
    Alert triggers whenever the TVL value of a specific project moves more than the defined trigger value (%/hour)

    ### Project
    'project': string of the form 'Uniswap' 

    ### Variation (TVL % variation within an hour)
    'tvl_change': float number between -100.0 and 100.0 

    """
    def __init__(self, name: str, email: str, params: dict()):
        super().__init__(name, email, params)

        self.description = "Alert triggers whenever the TVL value of a specific project moves more than the defined trigger value (%/hour)"
        self.form_controls = [
            {
                'name': 'project',
                'label': 'Project',
                'control': 'select',
                'type': 'text',
                'default_value': '',
                'values': get_llama_projects_list()
            },
            {
                'name': 'tvl_change',
                'label': 'TVL % variation within an hour (number between -100.0 and 100.0)',
                'control': 'input',
                'type': 'text',
                'default_value': '' 
            }
        ]

        try:
            self.project = self.params['project']
            self.tvl_change = float(self.params['tvl_change'])
            self.last_tvl = get_llama_tvl(self.project)
            self.last_time = datetime.now()
        except Exception:
            print('Error in params dict')

    def monitor_function(self):
        delta_time = datetime.now() - self.last_time
        delta_time_hours = delta_time.seconds / 60 / 24

        if delta_time_hours >= 1:
            tvl = get_llama_tvl(self.project)
            tvl_var = 100 * (tvl - self.last_tvl) / self.last_tvl / delta_time_hours # tvl_change is specified in 0-100%
            self.last_tvl = tvl
            self.last_time = datetime.now()

            print('TVL: ', tvl)

            if (tvl > 0 and tvl_var > self.tvl_change) or (tvl < 0 and tvl_var < self.tvl_change):
                message = f"Subject: ALERT! - {self.name}\n\nProject: {self.project}\nTVL: {tvl}\nTVL change: {tvl_var}%"
                self.alert(message)

from .tulip import get_tulip_tvl
class Tulip_TVL_alert(Alert):
    """
        ##  Tulip TVL Alerts
        Alert triggers whenever the TVL value of the specified Tulip Vault moves more than the defined trigger value (%/min)
        Available only for Raydium platform vaults

        ### Tulip Vault
        'vault': string of the form 'RAY-USDT' of a valid Tulip vault (Raydium platform only) 

        ### Variation (TVL % variation within a minute)
        'tvl_change': float number between -100.0 and 100.0 

        ### Period (variation in minutes)
        'period': number 
    """
    def __init__(self, name: str, email: str, params):
        super().__init__(name, email, params)

        self.description = "Alert triggers whenever the TVL value of the specified Tulip Vault moves more than the defined trigger value (%/min).\nAvailable only for Raydium platform vaults in Tulip."
        self.form_controls = [
           {
                'name': 'vault',
                'label': 'Vault',
                'control': 'select',
                'type': 'text',
                'default_value': '', 
                'values': [('RAY-USDT', 'RAY-USDT'), ('RAY-USDC', 'RAY-USDC')]
            },
            {
                'name': 'tvl_change',
                'label': 'TVL % variation (number between -100.0 and 100.0)',
                'control': 'input',
                'type': 'text',
                'default_value': '1.0' 
            },
            {
                'name': 'period',
                'label': 'Period to meassure variation (in minutes)',
                'control': 'input',
                'type': 'text',
                'default_value': '0' 
            }
        ]

        try:
            self.vault = self.params['vault']
            self.tvl_change = float(self.params['tvl_change'])
            self.period = float(self.params['period'])
            self.last_tvl = get_tulip_tvl(self.vault)
            self.last_time = datetime.now()
        except Exception:
            print('Error in params dict')

    def monitor_function(self):
        delta_time = datetime.now() - self.last_time
        delta_time_minutes = delta_time.seconds / 60

        print('delta_time_minutes:', delta_time_minutes)
        if delta_time_minutes >= self.period:
            tvl = get_tulip_tvl(self.vault)

            tvl_var = 100 * (tvl - self.last_tvl) / self.last_tvl / delta_time_minutes # tvl_change is specified in 0-100%
            self.last_tvl = tvl
            self.last_time = datetime.now()

            print('TVL: ', tvl)

            if (tvl > 0 and tvl_var > self.tvl_change) or (tvl < 0 and tvl_var < self.tvl_change):
                message = f"Subject: ALERT! - {self.name}\n\nVault: {self.vault}\nTVL: {tvl}\nTVL change: {tvl_var}%"
                self.alert(message)

from .raydium import get_raydium_pool_info, get_raydium_pool_tvl, get_raydium_pools_list, get_token_price
class Raydium_TVL_alert(Alert):
    """
    ##  Raydium TVL Alerts
    Alert triggers whenever the TVL value of a specific Raydium pool moves more than the defined trigger value

    ### Pool
    'pool': string of the form 'RAY-USDT' 

    ### Variation (TVL % variation)
    'tvl_change': float number between -100.0 and 100.0 

    ### Period (variation in minutes)
    'period': number 

    """
    def __init__(self, name: str, email: str, params: dict()):
        super().__init__(name, email, params)

        self.description = "Alert triggers whenever the TVL value of a specific Raydium pool moves more than the defined trigger value (%/period).\nConsider for the period, that the TVL value refreshes every 10 minutes."
        self.form_controls = [
            {
                'name': 'pool',
                'label': 'Pool',
                'control': 'select',
                'type': 'text',
                'default_value': '',
                'values': get_raydium_pools_list()
            },
            {
                'name': 'tvl_change',
                'label': 'TVL % variation (number between -100.0 and 100.0)',
                'control': 'input',
                'type': 'text',
                'default_value': '1.0' 
            },
            {
                'name': 'period',
                'label': 'Period to meassure variation (in minutes)',
                'control': 'input',
                'type': 'text',
                'default_value': '0' 
            }
        ]

        try:
            self.pool = self.params['pool']
            self.tvl_change = float(self.params['tvl_change'])
            self.period = float(self.params['period'])
            self.last_tvl = get_raydium_pool_tvl(self.pool)
            self.last_time = datetime.now()
        except Exception:
            print('Error in params dict')

    def monitor_function(self):
        delta_time = datetime.now() - self.last_time
        delta_time_minutes = delta_time.seconds / 60

        if delta_time_minutes >= self.period:
            tvl = get_raydium_pool_tvl(self.pool)
            tvl_var = 100 * (tvl - self.last_tvl) / self.last_tvl / delta_time_minutes # tvl_change is specified in 0-100%
            self.last_tvl = tvl
            self.last_time = datetime.now()

            print('TVL: ', tvl)

            if (tvl > 0 and tvl_var > self.tvl_change) or (tvl < 0 and tvl_var < self.tvl_change):
                message = f"Subject: ALERT! - {self.name}\n\nPool: {self.pool}\nTVL: {tvl}\nTVL change: {tvl_var}%"
                self.alert(message)

from .ftx_exchange import ftx_init, get_ftx_balance
from .gsheets import GoogleSheetsClient
GSHEETS_JSON = 'gsheets01.json'
GSHEETS_SPREADSHEET_ID = '1VZWqW79yTQOn4mytu2mQqghtiuGu8E9FwBjm1OJ8-To'
GSHEETS_WORKSHEET_NAME = 'Mangusta_FTX_tracker'
class FTX_balance_tracker(Alert):
    """
    ##  FTX Balance Tracker
    Reads FTX balance every 'period' time and registers the value on 'gsheet_name' google sheet
    Api Key and Secret Key should be defined as environ variables (API_KEY, SECRET_KEY)

    ### Period
    'period': period in minutes 

    ### Google Sheet
    'gsheet_name': string, name of the google sheet to write to

    """
    def __init__(self, name: str, email: str, params: dict()):
        super().__init__(name, email, params)

        self.description = "Reads FTX balance every 'period' time and registers the value on 'gsheet_name' google sheet.\nApi Key and Secret Key should be defined as environ variables (API_KEY, SECRET_KEY)"
        self.form_controls = [
            {
                'name': 'period',
                'label': 'Period (in minutes)',
                'control': 'input',
                'type': 'text',
                'default_value': ''            
            },
            {
                'name': 'sub_account',
                'label': 'FTX Subaccount name (leave blank for main account)',
                'control': 'input',
                'type': 'text',
                'default_value': '' 
            }
        ]

        try:
            self.period = float(self.params['period'])
            self.gsheet_name = GSHEETS_WORKSHEET_NAME
            self.sub_account = self.params['sub_account']
            self.last_time = datetime.now()
            self.ftx_exchange = ftx_init(sub_account=self.sub_account)
            self.gsheet_client = GoogleSheetsClient(GSHEETS_JSON, GSHEETS_SPREADSHEET_ID)
            self.gsheet_client.new_sheet(self.gsheet_name)
        except Exception:
            print('Error in params dict')


    def monitor_function(self):
        delta_time = datetime.now() - self.last_time
        delta_time_minutes = delta_time.seconds / 60

        if delta_time_minutes >= self.period:
            self.last_time = datetime.now()
            ftx_balance = get_ftx_balance(self.ftx_exchange)
            print('FTX balance: ', ftx_balance)
            date = datetime.now(timezone(-timedelta(hours=3))).strftime("%Y-%m-%d, %H:%M:%S")
            data = pd.DataFrame({'Fecha y hora': [date], 'Free': [ftx_balance['free']], 'Used': [ftx_balance['used']], 'Total': [ftx_balance['total']]})
            self.gsheet_client.write_at_bottom(self.gsheet_name, data)

# Por caca nuevo tipo de alerta se implementa la clase y se agrega al listado
Alert_types = {
    'DeFi TVLs': Llama_TVL_alert,
    'Raydium Pools TVL variation': Raydium_TVL_alert,
    # 'Tulip Vaults TVL variation': Tulip_TVL_alert
    'FTX Balance tracker': FTX_balance_tracker
}


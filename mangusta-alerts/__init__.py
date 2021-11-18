from flask import Flask, render_template, redirect, url_for, request, flash
from .Infinite_Thread import Infinite_Thread
# from flask_sqlalchemy import SQLAlchemy
# from flask_session import Session
# from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from . import config
import threading
import signal
import pandas as pd
from datetime import datetime, timezone, timedelta
import time
import os
from .alerts import Alerts_manager

APP = 'mangusta-alerts'
APP_URI = f'https://{APP}.herokuapp.com'
# DB_NAME = 'database.db'

UPDATE_INTERVAL = 6 # 6*10 = 60 segundos = 1 minuto

# db = SQLAlchemy()

# def create_db(app):
# 	database_file = APP + '/' + DB_NAME

# 	if not os.path.exists(database_file):
# 		db.create_all(app=app)
# 		print(f'Se creo una nueva base de datos: {database_file}')
# 	else:
# 		print(f'Base de datos existente: {database_file}')

def create_app():
	app = Flask(__name__)

	app.config['SECRET_KEY'] = config.APP_SECRET_KEY
	# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
	# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

	# db.init_app(app)

	# from .models import User
	# create_db(app)

	# login_manager = LoginManager()
	# login_manager.login_view = 'login'
	# login_manager.init_app(app)

	# @login_manager.user_loader
	# def load_user(user_id):
	#     return User.query.get(user_id)

	return app

app = create_app()
# from .models import User

# @app.route('/w')
# def w():
# 	nuevo_usuario = User(
# 		nombre = "admin", 
# 		apellido = "admin", 
# 		email = "admin2", 
# 		password = generate_password_hash("mangustaadmin"),
# 		porcentaje_actual = 1.0, 
# 		monto_usdt_inicial = 15000, 
# 		perfil = "admin"
# 	)

# 	db.session.add(nuevo_usuario)
# 	db.session.commit()
# 	print("usuario agregado")

# 	return redirect(url_for('index'))

@app.route('/', methods=['GET'])
# @login_required
def index():
	return redirect(url_for('current_alerts'))

@app.route('/current_alerts', methods=['GET'])
# @login_required
def current_alerts():
	return render_template('alerts.html', alerts_manager=alerts_manager)

@app.route('/new_alert', methods=['GET', 'POST'])
def new_alert_blank():
	if request.method == 'POST':
		alert_type = request.form['selected_type']
		name = request.form['name']
		email = request.form['email']

		params = dict()
		for field_name in request.form.keys():
			if field_name != 'selected_type' and field_name != 'name' and field_name != 'email':
				params[field_name] = request.form[field_name]

		alerts_manager.add_alert(alert_type, name, email, params)
		return redirect(url_for('current_alerts'))

	return render_template('new_alert.html', 
		alerts_manager=alerts_manager,
		alert_type='',
		description='',
		form_controls = []
	)

@app.route('/new_alert/<alert_type>', methods=['GET'])
# @login_required
def new_alert(alert_type):
	return render_template('new_alert.html', 
		alerts_manager = alerts_manager,
		alert_type = alert_type,
		description = alerts_manager.get_alert_description(alert_class=alert_type),
		form_controls = [] if alert_type == '' else alerts_manager.get_alert_controls(alert_class=alert_type)
	)

@app.route('/start/<id>', methods=['GET'])
def start(id):
	if request.method == 'GET':
		for alert in alerts_manager.alert_list:
			if alert.id == id:
				message = f"Subject: CryptoAlert ACTIVATED\n\n{alert.name} alert ACTIVATED."
				alert.start(message)

	return redirect(url_for('current_alerts'))

@app.route('/stop/<id>', methods=['GET'])
def stop(id):
	if request.method == 'GET':
		for alert in alerts_manager.alert_list:
			if alert.id == id:
				message = f"Subject: CryptoAlert DISABLED\n\n{alert.name} alert DISABLED."
				alert.stop(message)

	return redirect(url_for('current_alerts'))

@app.route('/delete/<id>', methods=['GET'])
def delete(id):
	if request.method == 'GET':
		for alert in alerts_manager.alert_list:
			if alert.id == id:
				message = f"Subject: CryptoAlert DISABLED and DELETED\n\n{alert.name} alert DELETED."
				alerts_manager.delete(id, message)

	return redirect(url_for('current_alerts'))

def update_function():	
	alerts_manager.monitor_alerts()

def update_thread():
	global update_thread_counter

	print('Running update thread...\n')
	#update_thread_counter = 0

	while update_thread_active:
		update_thread_counter += 1

		#hacemos un update de la data cada UPDATE_INVERVAL*10/60 minutos
		if update_thread_counter > UPDATE_INTERVAL:
			update_thread_counter = 0
			update_function()

		#cuando se recive una señal SIGTERM, tenemos 30 segundos para cerrar bien antes de recibir la SIGKILL 
		time.sleep(10) # => el time.sleep tiene que ser corto

	print('Update thread stopped\n')
	return

@app.route('/init_update_thread')
def init_update_thread(init_value=0):
	global update_thread_active
	global update_thread_counter

	if not update_thread_active:
		update_thread_active = True
		update_thread_counter = init_value

		print('Creating update thread')
		update__thread = threading.Thread(target=update_thread)
		update__thread.setDaemon(True)
		update__thread.start()

		update_thread_init_time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
		print('Update thread created at: {}'.format(update_thread_init_time))

		return 'Update thread started at: ' + update_thread_init_time
	else:
		return 'Update thread already active'

@app.route('/stop_threads')
def stop_threads():
	global update_thread_active

	infinite_thread.stop()
	update_thread_active = False

	return "Stopping infinite thread <br> Stopping update thread"

@app.route('/restart_update_thread')
def restart_update_thread():
	global update_thread_active

	print('Stopping update thread...')
	update_thread_active = False

	print('Initiating update thread...')
	init_update_thread(UPDATE_INTERVAL)

	return "Restarting update thread"

##########
## Misc ##
##########

def precision(number):

	number_string = str(number)
	integer_and_fraction = number_string.split('.')

	return len(integer_and_fraction[-1])

@app.context_processor
def precision_filter():
	def _precision_filter(num, precision):
		return round(num, precision)

	return dict(precision_filter=_precision_filter)

def handle_SIGTERM(signalnum, stackframe):
	global update_thread_active

	print('SIGTERM signal received.')
	infinite_thread.stop()
	update_thread_active = False

	print('Exiting app')
	if ENV != 'development':
		time.sleep(15) #esperamos a las threads para que se cierren 

	exit()

##############
#### Main ####
##############

alerts_manager = Alerts_manager()

# alertas de ejemplo
# alerts_manager.add_alert('Tulip Vaults TVL variation', 'Tulip RAY-USDT Vault', 'ccamogli@yahoo.com', params={
# 	'vault': 'RAY-USDT',
# 	'tvl_change': -1.2
# })
# alerts_manager.add_alert('DeFi TVLs', 'Spooky Swap project TVL', 'cachocamogli@gmail.com', params={
# 	'project': 'spookyswap',
# 	'tvl_change': -1.0
# })
# alerts_manager.add_alert('DeFi TVLs', 'Uniswap project TVL', 'cachocamogli@gmail.com', params={
# 	'project': 'uniswap',
# 	'tvl_change': 1.5
# })
alerts_manager.add_alert('Mangusta USD', 'FTX Balance tracker', 'ccamogli@yahoo.com', params={
	'period': '30',
	'sub_account': 'RAY2'
})

for alert in alerts_manager.alert_list:
	message = f"Subject: CryptoAlert ACTIVATED\n\n{alert.name} alert ACTIVATED."
	alert.start(message)

update_thread_active = False
update_thread_counter = 0
init_update_thread(init_value=UPDATE_INTERVAL)

ENV = os.environ.get('FLASK_ENV')
if ENV == 'development':
	print('WARNING: Development mode.\n')
else:
	signal.signal(signal.SIGTERM, handle_SIGTERM)
	if config.INFINITE_THREAD_AUTOSTART:
		print('Creating infinite thread')	
		infinite_thread = Infinite_Thread(APP_URI + '/ping')
		infinite_thread.start()

		# TODO: recuperar settings para la update thread desde una base de datos
		# print('Inicializando update thread...')
		# init_update_thread(UPDATE_INTERVAL)



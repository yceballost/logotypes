import logging
from datetime import datetime
import requests
from flask import request

# Configurar el logger
logging.basicConfig(filename='api_usage.log', level=logging.INFO)

GA_TRACKING_ID = 'G-KQCFQFWW6V'  # Reemplaza esto con tu Google Analytics Tracking ID

def send_event(category, action, label=None, value=0):
    data = {
        'v': '1',
        'tid': GA_TRACKING_ID,
        'cid': '555',  # Puedes usar un ID único o un valor constante
        't': 'event',
        'ec': category,
        'ea': action,
        'el': label,
        'ev': value,
    }
    response = requests.post('https://www.google-analytics.com/collect', data=data)
    return response.status_code

def log_request_info():
    endpoint = request.path
    method = request.method
    ip_address = request.remote_addr
    send_event('API Request', f'{method} {endpoint}', ip_address)
    logging.info(f"Time: {datetime.now()} Endpoint: {endpoint} Method: {method} IP: {ip_address}")

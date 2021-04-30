import requests
import logging
import os


ROOT_LOG_LEVEL = os.environ["ROOT_LOG_LEVEL"]
LOG_LEVEL = os.environ["LOG_LEVEL"]
API_URL_BASE = os.environ["API_URL_BASE"]

root_logger = logging.getLogger()
root_logger.setLevel(ROOT_LOG_LEVEL)
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# LEX FUNCTIONS START ---------------------------------

def get_slots(intent_request):
    response = intent_request['currentIntent']['slots']
    return response

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    return response

# LEX FUNCTIONS END ---------------------------------
def get_api_currentprice(original_coin, destination_coin):
    url_funtion = "/exchange/prices/"
    request_url = API_URL_BASE + url_funtion + original_coin + destination_coin
    payload={}
    headers = {}
    response = requests.request("GET", request_url, headers=headers, data=payload).json()
    logger.debug(f"API response: {response}")
    logger.debug(f"Length: {len(response['latestPrices'])}")
    if len(response['latestPrices'])==1:
        logger.debug(f"Got a response with price")
        return response
    else:
        logger.debug(f"Got a response, but no price")
        request_url = API_URL_BASE + url_funtion + destination_coin + original_coin
        reversepair_response = requests.request("GET", request_url, headers=headers, data=payload).json()
        reversepair_price = reversepair_response['latestPrices'][0]['price']
        logger.debug(f"Reverse Pair {destination_coin}{original_coin} price: {reversepair_price}")
        pair_price = 1 / reversepair_price
        logger.debug(f"Calc price = {pair_price}")
        reversepair_response['latestPrices'][0]['price'] = pair_price
        return reversepair_response
    logger.debug(f"API Response: {response.text}")
    return response

def get_currentprice_price(currentprice_rawdata):
    response = currentprice_rawdata['latestPrices'][0]['price']
    logger.debug(f"Current Price: {response}")
    return response

def get_coin_symbol(coin, value):
    currencySymbol = {
        'EUR': '€',
        'USD': '$',
        'GBP': '£'
    }
    logger.debug(f"Checking if {coin} is in {currencySymbol}")
    if coin in currencySymbol:
        return currencySymbol[coin] + str(round(float(value), 2))
    else:
        return f"{coin} {value}"

def lambda_handler(event, context):
    logger.debug(f"Event: {event}")
    intent_slots = get_slots(event)
    original_coin = intent_slots['Original_Coin'].upper()
    destination_coin = intent_slots['Destination_Coin'].upper()

    currentprice_rawdata = get_api_currentprice(original_coin, destination_coin)
    try:
        currentprice_price = get_currentprice_price(currentprice_rawdata)
    except IndexError:
        response = close({"Session": "Attributes"},
            'Fulfilled',
            {'contentType': 'PlainText',
            'content': 'Sorry, that pair is not currently supported'})
        return response

    destination_coin_value = get_coin_symbol(destination_coin, currentprice_price)

    response_message = f"Current Price of {original_coin} in {destination_coin} is: {destination_coin_value}"
    response = close({"Session": "Attributes"},
        'Fulfilled',
        {'contentType': 'PlainText',
        'content': response_message})
    
    logger.debug(f"Final Response: {response}")
    return response
import logging
import requests
from django.core.cache import cache

from flyFinder.config import *

TOKEN_CACHE_KEY = "auth_token"

def get_token():

    """
    Fetches the authentication token from the Amadeus API.

    This function sends a POST request to the Amadeus authentication API
    to retrieve an access token required for making subsequent API calls.
    The token is valid for a limited time and should be cached for reuse.

    Returns
    -------
    str or None
        The access token if successfully retrieved, or None if there was
        an error during the process.
    """

    try:
        url = AMADEUS_TOKEN_API_URL
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        payload = {
            'grant_type': 'client_credentials',
            'client_id': AMADEUS_API_ACCESS_KEY,
            'client_secret': AMADEUS_API_SECRET_KEY,
        }

        token_response = requests.post(url, headers=headers, data=payload)
        
        

        if token_response.status_code == 200:
            token_data = token_response.json()
            token = token_data.get("access_token")
            return token
        else:
            logging.error(f'Error in fetching token from amadeus : {str(error)}')

    except Exception as error:
        logging.error(f'Error in fetching token from amadeus : {str(error)}')

    return None

def get_cheapest_flight(params,token):

    """
    Fetches the cheapest available flight based on the provided parameters.

    This function sends a request to the Amadeus API using the provided
    access token and flight search parameters (origin, destination, and date).
    It returns the cheapest flight offer found.

    Parameters
    ----------
    params : dict
        A dictionary containing the search parameters for the flight:
        - origin: IATA code of the origin airport.
        - destination: IATA code of the destination airport.
        - date: Departure date in 'yyyy-mm-dd' format.

    token : str
        The access token for authenticating the request to the Amadeus API.

    Returns
    -------
    dict 
        A dictionary containing the cheapest flight price for given params if successful
    """

    try:
        url = AMADEUS_FLIGHT_SEARCH_API_URL
        headers = {'Authorization': f'Bearer {token}'}
        required_params = {
                "originLocationCode":params.get("origin"),
                "destinationLocationCode":params.get("destination"),
                "departureDate":params.get("date"),
                "adults":"1",
                "max":"1"
        }
        result = {'status':500,'data':'Internal Server Error'}
        flight_data_response = requests.get(url=url,headers=headers,params=required_params)
        json_response = flight_data_response.json()
        result['status'] = flight_data_response.status_code
        if flight_data_response.status_code == 401:
            token = get_token()
            cache.set(TOKEN_CACHE_KEY, token, timeout=1800)
            get_cheapest_flight()
        elif flight_data_response.status_code == 400:
            result['data'] = json_response['errors'][0]
        elif flight_data_response.status_code == 200:
            result['data'] = json_response['data'][0]['price']['total'] +" "+ json_response['data'][0]['price']['currency'] 

        return result
        
    except Exception as error:
            logging.error(f'Error in fetching cheapest flight price from amadeus : {str(error)}')
            return {'status':500,'data':'Internal Server Error'}
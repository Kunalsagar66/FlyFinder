from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

import logging

from flyFinder.config import *
from flights.services import (get_token,get_cheapest_flight)



class Ping(APIView):
    """
    A simple class to handle ping requests.

    This class provides an API endpoint to check if the server is active by
    responding with a "pong" message when a GET request is made.

    Methods
    -------
    get(self, request):
        Handles the GET request and returns a "pong" response.
    """

    def get(self,request):
        """
        Handles the GET request and returns a simple 'pong' response.

        This function is typically used as a ping/pong test to check if the API
        endpoint is responding correctly.

        Parameters
        ----------
        request : Request
            The incoming HTTP GET request.

        Returns
        -------
        Response
            A Response object containing a 'pong' message and an HTTP 200 OK status.
        """
        return Response(data={"data":"pong"},status=status.HTTP_200_OK)

class Price(APIView):

    """
    A class to handle flight price-related operations.

    This class provides an API endpoint to fetch the cheapest flight prices
    based on the origin, destination, and travel date.
    """
    def get(self,request):
        """
        Handles the GET request to fetch the cheapest flight price.

        This endpoint returns the cheapest flight offer available for the given
        origin, destination, and travel date.

        Parameters
        ----------
        request : Request
            The incoming HTTP GET request containing query parameters:
            - origin: The IATA code of the origin airport.
            - destination: The IATA code of the destination airport.
            - date: The departure date in the format 'yyyy-mm-dd'.
            - nocache: For providing the fresh data.

        Returns
        -------
        Response
            A JSON response with the cheapest flight offer, including the origin, 
            destination, departure date, and price.
        """

        try:
            query_params = {'origin': request.query_params.get('origin', None),
                            'destination': request.query_params.get('destination', None),
                            'date': request.query_params.get('date', None)}

            origin = request.query_params.get('origin')
            destination = request.query_params.get('destination')
            date = request.query_params.get('date')
            nocache = request.query_params.get('nocache')


            FLIGHT_DATA_CACHE_KEY = f"flight_data:{origin}:{destination}:{date}"
            TOKEN_CACHE_KEY = "auth_token"

            final_response = {}

            if nocache != "1":
                cached_flight_data = cache.get(FLIGHT_DATA_CACHE_KEY)
                if cached_flight_data:
                    return Response(data=cached_flight_data, status=status.HTTP_200_OK)
            
            token = cache.get(TOKEN_CACHE_KEY)

            if not token:
                token = get_token()
                cache.set(TOKEN_CACHE_KEY, token, timeout=1800)
            
            flight_response = get_cheapest_flight(query_params,token)
            if flight_response['status'] == 200:
                final_response['data'] = query_params
                final_response['data']['departure_date'] = final_response['data']['date']
                del final_response['data']['date']
                final_response['data']['price'] = flight_response['data']
                if nocache != "1":
                    cache.set(FLIGHT_DATA_CACHE_KEY,final_response,timeout=600)
            else:
                final_response['data'] = flight_response['data']

            return Response(data=final_response,status=flight_response['status'])
        except Exception as error:
            logging.error(f'Error in searching flight prices : {str(error)}')
            return Response(data= {"message":str(error)}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)

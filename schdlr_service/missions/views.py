from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions


class MissionControlAPIView(APIView):
    """
    """
    authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (permissions.IsAdminUser,)
    
    def get(self, request, format=None):
        """
        """
        print "GET Hello World"
        return Response({})
    
    def post(self, request, format=None):
        """
        """
        print "POST Hello World"
        return Response({}) 
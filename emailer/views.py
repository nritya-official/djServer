from django.shortcuts import render
from django.http import JsonResponse
from .emailService import load_templates, render_template, send_email_passkey
from django.views.decorators.csrf import csrf_exempt
from utils.flags import FIREBASE_AUTH
import logging
import jwt
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

def authVerifier():
    try:
        id_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjFkYmUwNmI1ZDdjMmE3YzA0NDU2MzA2MWZmMGZlYTM3NzQwYjg2YmMiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiQXl1c2ggUmFqIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0p6WXV4UUNCRHc1V2l3QXAxblBPV1VSS1ZFZXQ4emNoZVgxUHp2Zmctaz1zOTYtYyIsImlzcyI6Imh0dHBzOi8vc2VjdXJldG9rZW4uZ29vZ2xlLmNvbS9ucml0eWEtN2U1MjYiLCJhdWQiOiJucml0eWEtN2U1MjYiLCJhdXRoX3RpbWUiOjE3MjI4NjkzMTIsInVzZXJfaWQiOiI4emNzb1VtNUhzYU94bmlETGNuSDVMSGU1ODkyIiwic3ViIjoiOHpjc29VbTVIc2FPeG5pRExjbkg1TEhlNTg5MiIsImlhdCI6MTcyMjg2OTMxMiwiZXhwIjoxNzIyODcyOTEyLCJlbWFpbCI6ImF5dXNocmFqNzYzQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7Imdvb2dsZS5jb20iOlsiMTAzOTExMjAwOTI3MzY4NDYxNzU2Il0sImVtYWlsIjpbImF5dXNocmFqNzYzQGdtYWlsLmNvbSJdfSwic2lnbl9pbl9wcm92aWRlciI6Imdvb2dsZS5jb20ifX0.fviRLSgNyQHY-T9NijhOrZojkikEpCSdl2wl7jsJo4S3jPBdLaVZlAwLGd3LbXjAbpnFY7aCmLU3cnFrIJmlKHVCmI7vGQHIK8UY_nVEBotiAZaCVnRCaRgFWaihS9J3bDOT_pocbNaaQOLDVUCnMNogLeX5ktjN-J4Ikuh7hQun9b36J-pZC7DT9UTuzGlEDcliwyezwCvxHjyZoYoZySQOqz-uRx9WEXjc24mBcNgIiogGq2KNw-_lnmwHru23NnITwK1cM54udDueG9HCICgtJPeNyjL0hgWL51VJsaYVPT9E1FuYury134yBfR5G6HeLYqEzqGFIQtgWjaFRaQ"
        decoded_token = FIREBASE_AUTH.verify_id_token(id_token)
        logging.info("UID: %s", (decoded_token['uid']))
        logging.info("Email: %s", (decoded_token['email']))
    except Exception as e:
        if("Token expired" in str(e)):
            try:
                decoded_token = jwt.decode(id_token, options={"verify_signature": False}, algorithms=["RS256"])
                logging.info("Decoded token: %s", decoded_token)
            except jwt.InvalidTokenError:
                logging.error("Invalid token")
        else:
            logging.error("Error processing token %s", (e))

@method_decorator(csrf_exempt, name='dispatch')
class StudioAdd(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []      # Disable permissions

    def post(self, request):
        try:
            variables = {
                "studio_name": request.data.get("studio_name"),
                "studio_id": request.data.get("studio_id"),
                "city": request.data.get("city")
            }
            templates = load_templates()
            subject, body = render_template("StudioAdd", variables, templates)
            send_email_passkey(request.data.get("receiver_emails"), subject, body)
            return Response({"status": "success", "message": "Email sent successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class StudioUpdate(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []      # Disable permissions

    def post(self, request):
        try:
            variables = {
                "studio_name": request.data.get("studio_name"),
                "studio_id": request.data.get("studio_id"),
                "city": request.data.get("city")
            }
            templates = load_templates()
            subject, body = render_template("StudioUpdate", variables, templates)
            send_email_passkey(request.data.get("receiver_emails"), subject, body)
            return Response({"status": "success", "message": "Email sent successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class WorkshopAdd(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []      # Disable permissions

    def post(self, request):
        try:
            variables = {
                "workshop_name": request.data.get("workshop_name"),
                "workshop_id": request.data.get("workshop_id"),
                "city": request.data.get("city")
            }
            templates = load_templates()
            subject, body = render_template("WorkshopAdd", variables, templates)
            send_email_passkey(request.data.get("receiver_emails"), subject, body)
            return Response({"status": "success", "message": "Email sent successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class WorkshopUpdate(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []      # Disable permissions

    def post(self, request):
        try:
            variables = {
                "workshop_name": request.data.get("workshop_name"),
                "workshop_id": request.data.get("workshop_id"),
                "city": request.data.get("city")
            }
            templates = load_templates()
            subject, body = render_template("WorkshopUpdate", variables, templates)
            send_email_passkey(request.data.get("receiver_emails"), subject, body)
            return Response({"status": "success", "message": "Email sent successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class FreeTrialBookings(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []      # Disable permissions

    def post(self, request):
        try:
            variables = {
                "studio_name": request.data.get("studio_name"),
                "class_name": request.data.get("class_name"),
                "city": request.data.get("city")
            }
            templates = load_templates()
            subject, body = render_template("FreeTrialBooking", variables, templates)
            send_email_passkey(request.data.get("receiver_emails"), subject, body)
            return Response({"status": "success", "message": "Email sent successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class SendEmail(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []      # Disable permissions

    def post(self, request):
        try:
            subject = request.data.get("subject")
            body = request.data.get("body")
            receiver_emails = request.data.get("receiver_emails")
            send_email_passkey(receiver_emails, subject, body)
            return Response({"status": "success", "message": "Email sent successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

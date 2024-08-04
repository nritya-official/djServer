from django.shortcuts import render
from django.http import JsonResponse
from .emailService import load_templates, render_template, send_email_passkey
from django.views.decorators.csrf import csrf_exempt
from djApi.flags import FIREBASE_AUTH
import logging

@csrf_exempt
def studioAdd(request):
    try:
        #decoded_token = FIREBASE_AUTH.verify_id_token("eyJhbGciOiJSUzI1NiIsImtpZCI6ImUyNmQ5MTdiMWZlOGRlMTMzODJhYTdjYzlhMWQ2ZTkzMjYyZjMzZTIiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXpwIjoiODQ3NDIyNzc3NjU0LXMwN2kxb3JsNXY1aWdzb2g4dnRoaWdwdGY1aXN0NjI3LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiYXVkIjoiODQ3NDIyNzc3NjU0LXMwN2kxb3JsNXY1aWdzb2g4dnRoaWdwdGY1aXN0NjI3LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwic3ViIjoiMTAzOTExMjAwOTI3MzY4NDYxNzU2IiwiZW1haWwiOiJheXVzaHJhajc2M0BnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6Im9JY0JHbDRZaWFUWkhSQWhZWXhOQ3ciLCJpYXQiOjE3MjI3OTQ3NzgsImV4cCI6MTcyMjc5ODM3OH0.s0-O-bfsvZzj9-b0lQAI8ikTCzYa2CU6g7clN23LpyIHHa3_h5FZs01NcswZN2mauO2KJ09uy5S0U5woVd98H3gcbXIGfMwxAB_n_YpVH_jnnbMCQplDfGShk8mBu_IizJkNVXzKPR2gHQH1dj1CNR1BYu8cMymHiXoiM9ecZfBYOh7qjEI1NHJomkCpIZa50aT3S2cgoNJTcWrSNQHqSh9sS0FLi6tEkdd7uWos-m243EkwW2JhMM7JMpFyHx8hwXlkWQuFSpeyBC8RSi0pyaz2i7ft5hb9-tzE0S8O80BOZwcAlWiCCD0HKewu6qp4o3MuogbOJGw0oE4518PuWw")
        logging.info(decoded_token)
        variables = {
            "studio_name": request.POST.get("studio_name"),
            "studio_id": request.POST.get("studio_id"),
            "city": request.POST.get("city")
        }
        templates = load_templates()
        subject, body = render_template("StudioAdd", variables, templates)
        send_email_passkey(request.POST.get("receiver_emails"), subject, body)
        return JsonResponse({"status": "success", "message": "Email sent successfully."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

@csrf_exempt
def studioUpdate(request):
    try:
        variables = {
            "studio_name": request.POST.get("studio_name"),
            "studio_id": request.POST.get("studio_id"),
            "city": request.POST.get("city")
        }
        templates = load_templates()
        subject, body = render_template("StudioUpdate", variables, templates)
        send_email_passkey(request.POST.get("receiver_emails"), subject, body)
        return JsonResponse({"status": "success", "message": "Email sent successfully."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


@csrf_exempt
def workshopAdd(request):
    try:
        variables = {
            "workshop_name": request.POST.get("workshop_name"),
            "workshop_id": request.POST.get("workshop_id"),
            "city": request.POST.get("city")
        }
        templates = load_templates()
        subject, body = render_template("WorkshopAdd", variables, templates)
        send_email_passkey(request.POST.get("receiver_emails"), subject, body)
        return JsonResponse({"status": "success", "message": "Email sent successfully."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

@csrf_exempt
def workshopUpdate(request):
    try:
        variables = {
            "workshop_name": request.POST.get("workshop_name"),
            "workshop_id": request.POST.get("workshop_id"),
            "city": request.POST.get("city")
        }
        templates = load_templates()
        subject, body = render_template("WorkshopUpdate", variables, templates)
        send_email_passkey(request.POST.get("receiver_emails"), subject, body)
        return JsonResponse({"status": "success", "message": "Email sent successfully."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

@csrf_exempt
def freeTrialBookings(request):
    try:
        variables = {
            "studio_name": request.POST.get("studio_name"),
            "class_name": request.POST.get("class_name"),
            "city": request.POST.get("city")
        }
        templates = load_templates()
        subject, body = render_template("FreeTrialBooking", variables, templates)
        send_email_passkey(request.POST.get("receiver_emails"), subject, body)
        return JsonResponse({"status": "success", "message": "Email sent successfully."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

@csrf_exempt
def sendEmail(request):
    try:
        subject = request.POST.get("subject")
        body = request.POST.get("body")
        receiver_emails = request.POST.get("receiver_emails")
        send_email_passkey(receiver_emails, subject, body)
        return JsonResponse({"status": "success", "message": "Email sent successfully."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

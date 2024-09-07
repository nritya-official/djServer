from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.shortcuts import render
from djApi.flags import FIREBASE_DB, COLLECTIONS, nSuccessCodes
from google.cloud.firestore_v1.base_query import FieldFilter, Or
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
import logging

# Create your views here.


def studioEntityBookingsReport1(request):
    logging.info("getStudioBookingsReport")
    studio_id = request.GET.get('studio_id')

    if not studio_id:
        return JsonResponse({"error": "Missing studio_id parameter"}, status=400)

    try:
        # Query Firestore for bookings related to the given studio_id
        docs = FIREBASE_DB.collection(COLLECTIONS.BOOKINGS).where(
            'StudioId', '==', studio_id).stream()

        # Initialize the report structure
        report = {
            "StudioId": studio_id,
            "WORKSHOPS": {},
            "OPEN_CLASSES": {},
            "COURSES": {}
        }

        # Process documents
        for doc in docs:
            data = doc.to_dict()
            if 'WorkshopId' in data:
                report["WORKSHOPS"][data['WorkshopId']] = report["WORKSHOPS"].get(data['WorkshopId'], 0) + 1
            elif 'OpenClassId' in data:
                report["OPEN_CLASSES"][data['OpenClassId']] = report["OPEN_CLASSES"].get(data['OpenClassId'], 0) + 1
            elif 'CourseId' in data:
                report["COURSES"][data['CourseId']] = report["COURSES"].get(data['CourseId'], 0) + 1

        logging.info(report)
        return JsonResponse(report, safe=False, status=200)

    except Exception as e:
        logging.error(f"Error generating studio bookings report: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['GET'])
def studioEntityBookingsReport(request):
    logging.info("getStudioBookingsReport")
    studio_id = request.GET.get('studio_id')

    if not studio_id:
        return JsonResponse({"error": "Missing studio_id parameter"}, status=400)

    try:
        # Fetch StudioName from Studio collection
        studio_doc = FIREBASE_DB.collection(COLLECTIONS.STUDIO).document(studio_id).get()
        if not studio_doc.exists:
            return JsonResponse({"error": "Studio not found"}, status=404)
        
        studio_name = studio_doc.to_dict().get('studioName', 'Unknown Studio')

        # Query bookings related to the given studio_id
        docs = FIREBASE_DB.collection(COLLECTIONS.BOOKINGS).where('StudioId', '==', studio_id).stream()

        # Initialize the report structure
        report = {
            "StudioId": studio_id,
            "StudioName": studio_name,
            "WORKSHOPS": [],
            "OPEN_CLASSES": [],
            "COURSES": []
        }

        # Helper function to fetch names for each entity
        def get_entity_name(collection_name, entity_id, field):
            entity_doc = FIREBASE_DB.collection(collection_name).document(entity_id).get()
            if entity_doc.exists:
                return entity_doc.to_dict().get(field, 'Unknown')
            return 'Unknown'

        # Process documents
        workshop_counts = {}
        open_class_counts = {}
        course_counts = {}

        for doc in docs:
            data = doc.to_dict()
            if 'WorkshopId' in data:
                workshop_id = data['WorkshopId']
                workshop_counts[workshop_id] = workshop_counts.get(workshop_id, 0) + 1
            elif 'OpenClassId' in data:
                open_class_id = data['OpenClassId']
                open_class_counts[open_class_id] = open_class_counts.get(open_class_id, 0) + 1
            elif 'CourseId' in data:
                course_id = data['CourseId']
                course_counts[course_id] = course_counts.get(course_id, 0) + 1

        # Add workshop details to report
        for workshop_id, count in workshop_counts.items():
            workshop_name = get_entity_name(COLLECTIONS.WORKSHOPS, workshop_id, 'workshopName')
            report['WORKSHOPS'].append({
                "WorkshopId": workshop_id,
                "WorkshopName": workshop_name,
                "BookingsCount": count
            })

        # Add open class details to report
        for open_class_id, count in open_class_counts.items():
            open_class_name = get_entity_name(COLLECTIONS.OPENCLASSES, open_class_id, 'openClassName')
            report['OPEN_CLASSES'].append({
                "OpenClassId": open_class_id,
                "OpenClassName": open_class_name,
                "BookingsCount": count
            })

        # Add course details to report
        for course_id, count in course_counts.items():
            course_name = get_entity_name(COLLECTIONS.COURSES, course_id, 'workshopName')
            report['COURSES'].append({
                "CourseId": course_id,
                "CourseName": course_name,
                "BookingsCount": count
            })

        logging.info(report)
        return JsonResponse(report, safe=False, status=200)

    except Exception as e:
        logging.error(f"Error generating studio bookings report: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
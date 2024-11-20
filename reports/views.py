from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.shortcuts import render
from utils.flags import FIREBASE_DB
from utils.common_utils import COLLECTIONS, STORAGE_FOLDER, nSuccessCodes
from google.cloud.firestore_v1.base_query import FieldFilter, Or
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
import logging

# Create your views here.

@api_view(['GET'])
def testEndpoint(request):
    logging.info("Hello from report")
    return JsonResponse({'message': 'This is the report endpoint.'})

@api_view(['GET'])
def getAllOwnerStudio(request):
    # Create a mapping of <StudioId>: StudioName
    logging.info("getAllOwnerStudio")
    UserId = request.GET.get('user_id')

    if not UserId:
        return JsonResponse({"error": "Missing UserId parameter"}, status=400)

    try:
        # Fetch documents from Firestore where UserId matches
        docs = FIREBASE_DB.collection(COLLECTIONS.STUDIO).where('UserId', '==', UserId).stream()

        studio_mapping = {}
        for doc in docs:
            logging.info(docs)
            studio_data = doc.to_dict() 
            studio_id = doc.id 
            studio_name = studio_data.get('studioName')  # Extract the StudioName

            # Add to the mapping if StudioName exists
            if studio_name:
                studio_mapping[studio_id] = studio_name

        # Return the mapping as a JSON response
        logging.info(studio_mapping)
        return JsonResponse(studio_mapping, safe=False)

    except Exception as e:
        logging.error(f"Error fetching bookings: {e}")
        return JsonResponse({"error": "An error occurred while fetching the data"}, status=500)

@api_view(['GET'])
def studioEntityBookingsReport1(request):
    studio_id = request.GET.get('studio_id')
    logging.info("getStudioBookingsReport {0}".format(studio_id))

    if not studio_id:
        return JsonResponse({"error": "Missing studio_id parameter"}, status=400)

    try:
        # Fetch StudioName from Studio collection
        studio_doc = FIREBASE_DB.collection(COLLECTIONS.STUDIO).document(studio_id).get()
        if not studio_doc.exists:
            return JsonResponse({"error": "Studio not found"}, status=404)
        
        studio_name = studio_doc.to_dict().get('studioName', 'Unknown Studio')

        
        docs = FIREBASE_DB.collection(COLLECTIONS.BOOKINGS).where(filter=FieldFilter('associated_studio_id', '==', studio_id)).stream()
        for doc in docs:
            logging.info(f"{doc.id} => {doc.to_dict()}")
        '''
        # Initialize the report structure
        report = {
            "StudioId": studio_id,
            "StudioName": studio_name,
            "WORKSHOPS": [],
            "OPEN_CLASSES": [],
            "COURSES": []
        }

        # Helper function to fetch names and other details for each entity
        def get_entity_details(collection_name, entity_id, name_field, capacity_field=None):
            entity_doc = FIREBASE_DB.collection(collection_name).document(entity_id).get()
            if entity_doc.exists:
                entity_data = entity_doc.to_dict()
                name = entity_data.get(name_field, 'Unknown')
                date = entity_data.get('date', None)
                capacity = entity_data.get(capacity_field, 0) if capacity_field else None
                return name, capacity, date
            return 'Unknown', 0

        # Process documents
        workshop_counts = {}
        open_class_counts = {}
        course_counts = {}

        for doc in docs:
            data = doc.to_dict()
            date = data.get('date', 'Unknown')  # Extract the date for all bookings
            
            if 'WorkshopId' in data:
                workshop_id = data['WorkshopId']
                workshop_name, workshop_capacity, date = get_entity_details(
                    COLLECTIONS.WORKSHOPS, workshop_id, 'workshopName', 'capacity'
                )
                workshop_counts[workshop_id] = {
                    "name": workshop_name,
                    "capacity": workshop_capacity,
                    "date": date,
                    "count": workshop_counts.get(workshop_id, {'count': 0})['count'] + 1
                }
            elif 'OpenClassId' in data:
                open_class_id = data['OpenClassId']
                open_class_name, open_class_capacity, date = get_entity_details(
                    COLLECTIONS.OPENCLASSES, open_class_id, 'openClassName', 'capacity'
                )
                open_class_counts[open_class_id] = {
                    "name": open_class_name,
                    "capacity": open_class_capacity,
                    "date": date,
                    "count": open_class_counts.get(open_class_id, {'count': 0})['count'] + 1
                }
            elif 'CourseId' in data:
                course_id = data['CourseId']
                course_name, _, date = get_entity_details(COLLECTIONS.COURSES, course_id, 'courseName')  # Assuming 'courseName' for courses
                course_counts[course_id] = {
                    "name": course_name,
                    "date": date,
                    "count": course_counts.get(course_id, {'count': 0})['count'] + 1
                }

        # Add workshop details to report
        for workshop_id, details in workshop_counts.items():
            report['WORKSHOPS'].append({
                "WorkshopId": workshop_id,
                "WorkshopName": details['name'],
                "Capacity": details['capacity'],
                "Date": details['date'],
                "BookingsCount": details['count']
            })

        # Add open class details to report
        for open_class_id, details in open_class_counts.items():
            report['OPEN_CLASSES'].append({
                "OpenClassId": open_class_id,
                "OpenClassName": details['name'],
                "Capacity": details['capacity'],
                "Date": details['date'],
                "BookingsCount": details['count']
            })

        # Add course details to report
        for course_id, details in course_counts.items():
            report['COURSES'].append({
                "CourseId": course_id,
                "CourseName": details['name'],
                "Date": details['date'],
                "BookingsCount": details['count']
            })

        logging.info(report)
        '''
        return JsonResponse({}, safe=False, status=200)

    except Exception as e:
        logging.error(f"Error generating studio bookings report: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['GET'])
def studioEntityBookingsReport(request):
    studio_id = request.GET.get('studio_id')
    logging.info("getStudioBookingsReport {0}".format(studio_id))

    if not studio_id:
        return JsonResponse({"error": "Missing studio_id parameter"}, status=400)

    try:
        # Fetch StudioName from Studio collection
        studio_doc = FIREBASE_DB.collection(COLLECTIONS.STUDIO).document(studio_id).get()
        if not studio_doc.exists:
            return JsonResponse({"error": "Studio not found"}, status=404)
        
        studio_name = studio_doc.to_dict().get('studioName', 'Unknown Studio')
        
        # Initialize the report structure
        report = {
            "StudioId": studio_id,
            "StudioName": studio_name,
            "WORKSHOPS": [],
            "OPEN_CLASSES": [],
            "COURSES": []
        }

        # Helper function to fetch names and other details for each entity
        def get_entity_details(collection_name, entity_id, name_field, capacity_field=None):
            entity_doc = FIREBASE_DB.collection(collection_name).document(entity_id).get()
            if entity_doc.exists:
                entity_data = entity_doc.to_dict()
                name = entity_data.get(name_field, 'Unknown')
                date = entity_data.get('date', 'Unknown Date')
                capacity = entity_data.get(capacity_field, 0) if capacity_field else None
                return name, capacity, date
            return 'Unknown', 0, 'Unknown Date'

        # Fetch Bookings associated with the Studio
        docs = FIREBASE_DB.collection(COLLECTIONS.BOOKINGS).where(
            filter=FieldFilter('associated_studio_id', '==', studio_id)
        ).stream()

        workshop_counts = {}
        open_class_counts = {}
        course_counts = {}

        # Process each booking document
        for doc in docs:
            data = doc.to_dict()
            logging.info(data)
            increment_count = data.get('persons_allowed', 1)

            if data['entity_type'] == 'Workshops':
                workshop_id = data['entity_id']
                workshop_name, workshop_capacity, date = get_entity_details(
                    COLLECTIONS.WORKSHOPS, workshop_id, 'workshopName', 'capacity'
                )
                workshop_counts[workshop_id] = {
                    "name": workshop_name,
                    "capacity": workshop_capacity,
                    "date": date,
                    "count": workshop_counts.get(workshop_id, {'count': 0})['count'] + increment_count
                }
            elif data['entity_type'] == 'OpenClasses':
                open_class_id = data['entity_id']
                open_class_name, open_class_capacity, date = get_entity_details(
                    COLLECTIONS.OPENCLASSES, open_class_id, 'openClassName', 'capacity'
                )
                open_class_counts[open_class_id] = {
                    "name": open_class_name,
                    "capacity": open_class_capacity,
                    "date": date,
                    "count": open_class_counts.get(open_class_id, {'count': 0})['count'] + increment_count
                }
            elif data['entity_type'] == 'Courses':
                course_id = data['entity_id']
                course_name, _, date = get_entity_details(
                    COLLECTIONS.COURSES, course_id, 'courseName'
                )
                course_counts[course_id] = {
                    "name": course_name,
                    "date": date,
                    "count": course_counts.get(course_id, {'count': 0})['count'] + increment_count
                }

        # Add workshop details to report
        for workshop_id, details in workshop_counts.items():
            report['WORKSHOPS'].append({
                "EntityId": workshop_id,
                "EntityName": details['name'],
                "Capacity": details['capacity'],
                "Date": details['date'],
                "BookingsCount": details['count']
            })

        # Add open class details to report
        for open_class_id, details in open_class_counts.items():
            report['OPEN_CLASSES'].append({
                "EntityId": open_class_id,
                "EntityName": details['name'],
                "Capacity": details['capacity'],
                "Date": details['date'],
                "BookingsCount": details['count']
            })

        # Add course details to report
        for course_id, details in course_counts.items():
            report['COURSES'].append({
                "EntityId": course_id,
                "EntityName": details['name'],
                "Date": details['date'],
                "BookingsCount": details['count']
            })

        logging.info(report)
        return JsonResponse(report, safe=False, status=200)

    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return JsonResponse({"error": "An error occurred while generating the report"}, status=500)

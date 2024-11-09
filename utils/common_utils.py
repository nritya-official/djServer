import time
import jwt
import logging

class COLLECTIONS:
    USER = 'User'
    STUDIO = 'Studio'
    COURSES = 'Courses'
    OPENCLASSES = 'OpenClasses'
    WORKSHOPS = 'Workshops'
    BOOKINGS = 'Bookings'
    RATINGS = 'Ratings'
    USER_KYC = 'UserKyc'
    TRANSACTIONS = 'Transactions'
    FREE_TRIAL_BOOKINGS = 'FreeTrialBookings'
    INSTRUCTORS = 'Instructors'

class STORAGE_FOLDER:
    STUDIO_IMAGES = 'StudioImages'
    STUDIO_ANNOUNCEMENTS = 'StudioAnnouncements'
    STUDIO_ICON = 'StudioIcon'

class NOTIFICATION:
    OP_CREATE = "added"
    OP_UPDATE = "updated"
    OP_DELETE = "deleted"
    OP_SIGN_UP = "Sign Up"
    OP_KYC_APPROVED = "creator approved" 
    OP_KYC_REJECTED = "creator rejected"
    OP_KYC_REVOKED = "creator revoked"
    TYPE_CRUD = "Crud"

class nSuccessCodes:
    # Success Codes
    CREATED = 201  # Resource created successfully
    ACCEPTED = 202  # Request accepted but not yet processed
    NOT_ACCEPTED = 203   
    NO_CONTENT = 204  # Request successful but no content to return
    BOOKING_SUCCESS = 200  # Request successful
    SUCCESS = 200
    ALREADY_BOOKED = 205

    # Client Error Codes
    BAD_REQUEST = 400  # Bad request
    UNAUTHORIZED = 401  # Authentication required
    FORBIDDEN = 403  # Access forbidden
    NOT_FOUND = 404  # Resource not found
    METHOD_NOT_ALLOWED = 405  # Method not allowed
    CONFLICT = 409  # Conflict with the current state of the resource
    FAILURE = 420

    # Server Error Codes
    INTERNAL_SERVER_ERROR = 500  # Generic server error
    NOT_IMPLEMENTED = 501  # Server does not support the requested functionality
    BAD_GATEWAY = 502  # Invalid response from upstream server
    SERVICE_UNAVAILABLE = 503  # Service unavailable

class BOOKINGS_MSG:
    SEATS_FULL = "All seats are booked."
    SEATS_BOOKED = "Seats booked !"
    SEATS_INSUFFICIENT = "Not enough seats left. Decrease number of persons and try again."
    EVENT_PASSED = "Event has already started/finished."
    INVALID_SELECTION = "Invalid selection."
    EVENT_NOT_FOUND = "Event not found"
    PAID_BUT_SEATS_INSUFFICIENT = "Unable to get booking(s), slots booked before payment was completed. Payment refund initiated."
    SIGNATURE_MISMATCH = 'Signature Mismatch!'
    ALREADY_BOOKED = "You have alerady booked."

class BOOKINGS_STATUS:
    SEATS_FULL = 401
    SEATS_BOOKED = 202
    SEATS_INSUFFICIENT = 402
    EVENT_PASSED = 403
    INVALID_SELECTION = 404
    EVENT_NOT_FOUND = 441
    PAID_BUT_SEATS_INSUFFICIENT = 405
    SIGNATURE_MISMATCH = 406
    ALREADY_BOOKED = 407

BOOKINGS_RESPONSE_MAP = {
    BOOKINGS_STATUS.SEATS_FULL: BOOKINGS_MSG.SEATS_FULL,
    BOOKINGS_STATUS.SEATS_BOOKED: BOOKINGS_MSG.SEATS_BOOKED,
    BOOKINGS_STATUS.SEATS_INSUFFICIENT: BOOKINGS_MSG.SEATS_INSUFFICIENT,
    BOOKINGS_STATUS.EVENT_PASSED: BOOKINGS_MSG.EVENT_PASSED,
    BOOKINGS_STATUS.INVALID_SELECTION: BOOKINGS_MSG.INVALID_SELECTION,
    BOOKINGS_STATUS.EVENT_NOT_FOUND: BOOKINGS_MSG.EVENT_NOT_FOUND,
    BOOKINGS_STATUS.PAID_BUT_SEATS_INSUFFICIENT: BOOKINGS_MSG.PAID_BUT_SEATS_INSUFFICIENT,
    BOOKINGS_STATUS.SIGNATURE_MISMATCH : BOOKINGS_MSG.SIGNATURE_MISMATCH,
    BOOKINGS_STATUS.ALREADY_BOOKED : BOOKINGS_MSG.ALREADY_BOOKED
}

# Usage example
def get_booking_response(status_code):
    return BOOKINGS_RESPONSE_MAP.get(status_code, "Unknown error occurred.")


def is_valid_entity_type(entity_type):
    if entity_type in vars(COLLECTIONS).values():
        return True
    else:
        # Log a warning if the entity type is not found
        logging.warning(f"Entity type '{entity_type}' is not found in COLLECTIONS.")
        return False

def times_us():
  """
  Returns the integer Epoch time in microseconds.
  """
  gmt_time = time.gmtime()  # Get GMT time
  return int(time.mktime(gmt_time) * 1e6)

def get_reversed_dictionary(input_dict):
  """
  Reverse a one-to-one mapping dictionary. Eg :
    dict1 = {"A": 1, "B": 2}
    result = {1: "A", 2: "B"}
  :return : reversed dictionary
  :raises TypeError: If the values in the dictionary are not unique.
  """
  reversed_dict = dict((v, k) for k, v in input_dict.items())
  if len(reversed_dict) != len(input_dict):
    raise TypeError("The values in the dictionary are not unique")
  return reversed_dict

def extract_user_id(request):
    """
    Utility function to extract user_id from the Authorization header in the request
    without verifying the token signature.
    
    Args:
        request: The incoming Django request object.
    
    Returns:
        str: The user ID extracted from the JWT token, or an error message as a string.
    """
    # Get the Authorization header
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return 'Authorization header missing'

    # Extract the token from the 'Bearer <token>' format
    if auth_header.startswith('Bearer '):
        auth_token = auth_header.split(' ')[1]
    else:
        return 'Invalid Authorization header format'

    # Decode the JWT without verifying the signature
    try:
        decoded_token = jwt.decode(auth_token, options={"verify_signature": False})
        user_id = decoded_token.get('user_id')  # Assuming 'user_id' is stored in the token
        return user_id
    except jwt.ExpiredSignatureError:
        return 'Token has expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'


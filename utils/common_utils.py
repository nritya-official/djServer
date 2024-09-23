import time

class COLLECTIONS:
    USER = 'User'
    STUDIO = 'Studio'
    OPEN_CLASSES = 'OpenClasses'
    WORKSHOPS = 'Workshops'
    COURSES = 'Courses'
    RATINGS = 'Ratings'
    FREE_TRIAL_BOOKINGS = 'FreeTrialBookings'
    INSTRUCTORS = 'Instructors'
    BOOKINGS = 'Bookings'

class nSuccessCodes:
    # Success Codes
    CREATED = 201  # Resource created successfully
    ACCEPTED = 202  # Request accepted but not yet processed
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

    # Server Error Codes
    INTERNAL_SERVER_ERROR = 500  # Generic server error
    NOT_IMPLEMENTED = 501  # Server does not support the requested functionality
    BAD_GATEWAY = 502  # Invalid response from upstream server
    SERVICE_UNAVAILABLE = 503  # Service unavailable


def is_valid_entity_type(entity_type):
    return entity_type in vars(COLLECTIONS).values()

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

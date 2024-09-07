import time

def times_us():
  """
  Returns the integer Epoch time in microseconds.
  """
  return int(time.time() * 1e6)

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

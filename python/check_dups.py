"""Checking for dups using tuples and dictionary"""

import time

def check_duplicates_with_tuples(string):
    """
    check for duplicates using tuples
    :param s:
    :return:
    """
    seen = ()
    counts = {}
    for char in string:
        if char in seen:
            counts[char] = counts.get(char, 1) + 1
        else:
            counts[char] = 1
            seen += (char,)
    return counts

def check_duplicates_with_dict(string):
    """
    check for duplicates using dict
    :param s:
    :return:
    """
    char_count = {}
    for char in string:
        char_count[char] = char_count.get(char, 0) + 1
    return char_count


# Test with a long string for meaningful timing
VERY_LONG_STRING = "aabcccddde" * 1000

# Timing tuple method
start_time = time.time()
tuple_result = check_duplicates_with_tuples(VERY_LONG_STRING)
end_time = time.time()
tuple_time = end_time - start_time

# Timing dictionary method
start_time = time.time()
dict_result = check_duplicates_with_dict(VERY_LONG_STRING)
end_time = time.time()
dict_time = end_time - start_time
print(f"Tuple Method: Result={tuple_result}, Time={tuple_time:.8f} seconds")
print(f"Dict Method:  Result={dict_result}, Time={dict_time:.8f} seconds")

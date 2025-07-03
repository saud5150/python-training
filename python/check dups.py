import time

def check_duplicates_with_tuples(s):
    seen = ()
    counts = {}
    for char in s:
        if char in seen:
            counts[char] = counts.get(char, 1) + 1
        else:
            counts[char] = 1
            seen += (char,)
    return counts

def check_duplicates_with_dict(s):
    char_count = {}
    for char in s:
        char_count[char] = char_count.get(char, 0) + 1
    return char_count


# Test with a long string for meaningful timing
long_string = "aabcccddde"

# Timing tuple method
start_time = time.time()
tuple_result = check_duplicates_with_tuples(long_string)
end_time = time.time()
tuple_time = end_time - start_time

# Timing dictionary method
start_time = time.time()
dict_result = check_duplicates_with_dict(long_string)
end_time = time.time()
dict_time = end_time - start_time
print(f"Tuple Method: Result={tuple_result}, Time={tuple_time:.8f} seconds")
print(f"Dict Method:  Result={dict_result}, Time={dict_time:.8f} seconds")

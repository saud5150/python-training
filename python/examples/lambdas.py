# # Add two numbers
# add = lambda x, y: x + y
# print(add(3, 5))  # Output: 8

# numbers = [1, 2, 3, 4, 5]
# squared = list(map(lambda x: x**2, numbers))
# print(squared)  # Output: [1, 4, 9, 16, 25]

# numbers = [1, 2, 3, 4, 5, 6]
# evens = list(filter(lambda x: x % 2 == 0, numbers))
# print(evens)  # Output: [2, 4, 6]

people = [('Alice', 30), ('Bob', 25), ('Carol', 35)]
sorted_people = sorted(people, key=lambda person: person[1])
print(sorted_people)  # Output: [('Bob', 25), ('Alice', 30), ('Carol', 35)]

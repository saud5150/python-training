"""Examples made using AI"""


import copy

def shallow_copy_with_slice():
    print("=== Shallow Copy with Slicing ===")
    original = [1, 2, [3, 4]]
    copied = original[:]
    print("Original:", original)
    print("Copied:", copied)
    copied[0] = 100
    print("After modifying copied[0]:", copied)
    print("Original after copied[0] change:", original)
    print()

def shallow_copy_with_list_constructor():
    print("=== Shallow Copy with list() Constructor ===")
    original = [1, 2, [3, 4]]
    copied = list(original)
    copied[1] = 200
    copied[2][1] = 888
    print("Original:", original)
    print("Copied:", copied)
    print()

def shallow_copy_with_copy_method():
    print("=== Shallow Copy with copy() Method ===")
    original = [1, 2, [3, 4]]
    copied = original.copy()
    copied.append(5)
    copied[2][0] = 777
    print("Original:", original)
    print("Copied:", copied)
    print()

def shallow_copy_with_copy_module():
    print("=== Shallow Copy with copy.copy() ===")
    original = [1, 2, [3, 4]]
    copied = copy.copy(original)
    copied[2][1] = 666
    print("Original:", original)
    print("Copied:", copied)
    print()

def show_shallow_copy_behavior():
    print("=== Shallow Copy Behavior with Nested Lists ===")
    original = [[1, 2], [3, 4]]
    copied = copy.copy(original)
    copied[0][0] = 555
    print("Original:", original)
    print("Copied:", copied)
    print("Are original and copied the same object?", original is copied)
    print("Are original[0] and copied[0] the same object?", original[0] is copied[0])
    print()

# Run all demonstrations
shallow_copy_with_slice()
shallow_copy_with_list_constructor()
shallow_copy_with_copy_method()
shallow_copy_with_copy_module()
show_shallow_copy_behavior()

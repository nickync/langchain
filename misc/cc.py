from typing import Any


def f(s):
    # Handle edge cases
    if len(s) == 0:
        return 0
    if len(s) == 1:
        return 1
    
    l = 0
    r = 0
    max_len = 0
    
    while r < len(s):
        subs = s[l:r+1]  # Current window
        #print(f"Window [{l}:{r+1}]: '{subs}'")
        
        # Check if current window has no duplicates
        if len(subs) == len(set(subs)):  # No duplicates
            max_len = max(max_len, len(subs))
            r += 1
        else:
            # Duplicate found, shrink from left
            l += 1
        #print(f"  max_len={max_len}, current_len={r-l}, window='{s[l:r+1]}'")
    
    print(f"  Final: l={l}, r={r}, r-l={r-l}, max_len={max_len}")
    return r-l  # This is wrong! Should return max_len



print(f("tmmzuxt"))  

# Test to demonstrate fixes:

# Test cases to verify:
test_cases = [
    # ("abcabcbb", 3),      # Expected: 3 ("abc")
    # ("bbbbb", 1),         # Expected: 1 ("b")
    # ("pwwkew", 3),        # Expected: 3 ("wke" or "kew")
    # ("", 0),              # Expected: 0 (empty string)
    # ("a", 1),             # Expected: 1 ("a")
    # ("abcdef", 6),        # Expected: 6 ("abcdef")
    # ("dvdf", 3),          # Expected: 3 ("vdf")
    # ("abcdeabcde", 5),    # Expected: 5 ("abcde")
    ("tmmzuxt", 5),       # Expected: 5 ("mzuxt")
    ("abba", 2),          # Expected: 2 ("ab" or "ba")
]

print("\nTest Results:")
print("=" * 60)
# for test_str, expected in test_cases:
#     result = f(test_str)
#     status = "PASS" if result == expected else "FAIL"
#     print(f"{status} Input: '{test_str:12}' | Got: {result} | Expected: {expected}") 

print(type(12) == int)



def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    #print(f"Sorting {arr[:mid]} and {arr[mid:]}")
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    #print(f"Merging {left} and {right}")
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    print(f"Extending {left} and {right}")
    result.extend(left[i:])
    result.extend(right[j:])
    #print(f"Result: {result}")
    return result

print(merge_sort([1, 3, 8, 5, 4]))


def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr)-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                print(f"Swapped {arr[j]} and {arr[j+1]}, i {i} j {j}")
    return arr

print(bubble_sort([9, 1, 8, 3, 2]))

def s(arr):
    i = 0
    m = 10
    cur=0
    while i < len(arr):
        for j in range(i, len(arr)):
            if arr[j] < m:
                m = arr[j]
                cur = j
        arr[i], arr[cur] = arr[cur], arr[i]
        i += 1
        m = 10
    return arr

#print(s([9, 1, 8, 3, 2]))

def iis(arr):
    j = 0
    for i in range(len(arr)-1):
        j = i + 1
        while j > 0:
            if arr[i] > arr[j]:
                arr[i], arr[j] = arr[j], arr[i]
            j -= 1
            i -= 1
    return arr

print(iis([9, 1, 8, 3, 2]))

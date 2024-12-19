def quicksort(list, first, last):
    """Quicksort algorithm to sort a list of wind farm names."""
    if first < last:
        splitpoint = partition(list, first, last)
        quicksort(list, first, splitpoint)
        quicksort(list, splitpoint + 1, last)

def partition(list, first, last):
    """Partitioning step of the quicksort algorithm."""
    pivot = list[first]
    left_pointer = first + 1
    right_pointer = last
    done = False
    while not done:
        while left_pointer <= right_pointer and list[left_pointer] <= pivot:
            left_pointer = left_pointer + 1
        while list[right_pointer] >= pivot and right_pointer >= left_pointer:
            right_pointer = right_pointer - 1
        if right_pointer < left_pointer:
            done = True
        else:
            temp = list[left_pointer]
            list[left_pointer] = list[right_pointer]
            list[right_pointer] = temp
    temp = list[first]
    list[first] = list[right_pointer]
    list[right_pointer] = temp
    return right_pointer
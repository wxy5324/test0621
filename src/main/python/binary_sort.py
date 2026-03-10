"""
二分插入排序 - 与 Java 实现一致
"""


def binary_search(arr, target, left, right):
    """二分法查找插入位置"""
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return left


def binary_insertion_sort(arr):
    """二分插入排序"""
    result = list(arr)
    for i in range(1, len(result)):
        key = result[i]
        pos = binary_search(result, key, 0, i - 1)
        for j in range(i, pos, -1):
            result[j] = result[j - 1]
        result[pos] = key
    return result

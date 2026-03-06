/**
 * 二分插入排序 - 使用二分查找确定插入位置，提高插入排序效率
 */
public class BinaryInsertionSort {

    /**
     * 二分查找插入位置
     * @param arr 已排序部分的数组
     * @param target 待插入的值
     * @param left 左边界
     * @param right 右边界
     * @return 插入位置
     */
    private static int binarySearch(int[] arr, int target, int left, int right) {
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return left;
    }

    /**
     * 二分插入排序
     */
    public static void binaryInsertionSort(int[] arr) {
        for (int i = 1; i < arr.length; i++) {
            int key = arr[i];
            int pos = binarySearch(arr, key, 0, i - 1);
            // 将 pos 到 i-1 的元素后移一位
            for (int j = i; j > pos; j--) {
                arr[j] = arr[j - 1];
            }
            arr[pos] = key;
        }
    }

    public static void main(String[] args) {
        int[] arr = {64, 34, 25, 12, 22, 11, 90, 5};
        
        System.out.println("排序前: ");
        printArray(arr);

        binaryInsertionSort(arr);

        System.out.println("排序后: ");
        printArray(arr);
    }

    private static void printArray(int[] arr) {
        for (int i = 0; i < arr.length; i++) {
            System.out.print(arr[i]);
            if (i < arr.length - 1) {
                System.out.print(", ");
            }
        }
        System.out.println();
    }
}

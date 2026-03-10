import org.junit.AfterClass;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TestWatcher;
import org.junit.runner.Description;
import static org.junit.Assert.*;

/**
 * 二分插入排序 - 单元测试与功能测试
 */
public class BinaryInsertionSortTest {

    private static int testsRun = 0;
    private static int failures = 0;
    private static int errors = 0;
    private static int skipped = 0;

    @Rule
    public TestWatcher watchman = new TestWatcher() {
        @Override
        protected void succeeded(Description description) {
            testsRun++;
            System.out.println("[通过] " + description.getMethodName());
        }
        @Override
        protected void failed(Throwable e, Description description) {
            testsRun++;
            if (e instanceof AssertionError) {
                failures++;
            } else {
                errors++;
            }
            System.out.println("[失败] " + description.getMethodName() + ": " + e.getMessage());
        }
        @Override
        protected void skipped(org.junit.AssumptionViolatedException e, Description description) {
            testsRun++;
            skipped++;
            System.out.println("[跳过] " + description.getMethodName());
        }
    };

    @AfterClass
    public static void printSummary() {
        System.out.println("---------------------------------------");
        System.out.println("Tests run: " + testsRun + ", Failures: " + failures + ", Errors: " + errors + ", Skipped: " + skipped);
        System.out.println("---------------------------------------");
    }

    // ============== 功能测试用例 ==============

    @Test
    public void testSortRandomArray() {
        // 随机乱序数组
        int[] arr = {64, 34, 25, 12, 22, 11, 90, 95, 5};
        int[] expected = {5, 11, 12, 22, 25, 34, 64, 90, 95};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }

    @Test
    public void testSortAlreadySorted() {
        // 已排序数组
        int[] arr = {1, 2, 3, 4, 5};
        int[] expected = {1, 2, 3, 4, 5};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }

    @Test
    public void testSortReverseOrder() {
        // 逆序数组
        int[] arr = {5, 4, 3, 2, 1};
        int[] expected = {1, 2, 3, 4, 5};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }

    @Test
    public void testSortWithDuplicates() {
        // 含重复元素
        int[] arr = {3, 1, 4, 1, 5, 9, 2, 6, 5, 3};
        int[] expected = {1, 1, 2, 3, 3, 4, 5, 5, 6, 9};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }

    @Test
    public void testSortAllSameElements() {
        // 全相同元素
        int[] arr = {7, 7, 7, 7, 7};
        int[] expected = {7, 7, 7, 7, 7};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }

    @Test
    public void testSortNegativeNumbers() {
        // 含负数
        int[] arr = {-5, -1, -9, 3, 0, -2};
        int[] expected = {-9, -5, -2, -1, 0, 3};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }

    @Test
    public void testSortMixedPositiveNegative() {
        // 正负混合
        int[] arr = {10, -3, 0, -10, 5};
        int[] expected = {-10, -3, 0, 5, 10};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }

    // ============== 单元测试 - 边界条件 ==============

    @Test
    public void testSortEmptyArray() {
        // 空数组
        int[] arr = {};
        int[] expected = {};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }

    @Test
    public void testSortSingleElement() {
        // 单元素数组
        int[] arr = {42};
        int[] expected = {42};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }

    @Test
    public void testSortTwoElementsAscending() {
        // 两元素-升序
        int[] arr = {1, 2};
        int[] expected = {1, 2};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }

    @Test
    public void testSortTwoElementsDescending() {
        // 两元素-降序
        int[] arr = {2, 1};
        int[] expected = {1, 2};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }

    @Test
    public void testSortTwoEqualElements() {
        // 两相同元素
        int[] arr = {5, 5};
        int[] expected = {5, 5};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }

    // ============== 功能测试 - In-place 验证 ==============

    @Test
    public void testSortIsInPlace() {
        // 验证排序为原地操作，修改原数组
        int[] arr = {3, 1, 2};
        int[] sameRef = arr;
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertSame("排序应原地修改原数组", sameRef, arr);
        assertArrayEquals(new int[]{1, 2, 3}, arr);
    }

    // ============== 功能测试 - 稳定性与正确性 ==============

    @Test
    public void testSortLargeArray() {
        // 较大数组
        int[] arr = new int[100];
        for (int i = 0; i < 100; i++) {
            arr[i] = 99 - i;
        }
        BinaryInsertionSort.binaryInsertionSort(arr);
        for (int i = 0; i < 100; i++) {
            assertEquals("位置 " + i, i, arr[i]);
        }
    }

    @Test
    public void testSortConsecutiveDuplicates() {
        // 连续重复元素
        int[] arr = {2, 2, 2, 1, 1, 1, 3, 3, 3};
        int[] expected = {1, 1, 1, 2, 2, 2, 3, 3, 3};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }

    @Test
    public void testSortMaxIntValues() {
        // 较大整数值
        int[] arr = {Integer.MAX_VALUE, 0, Integer.MIN_VALUE};
        int[] expected = {Integer.MIN_VALUE, 0, Integer.MAX_VALUE};
        BinaryInsertionSort.binaryInsertionSort(arr);
        assertArrayEquals(expected, arr);
    }
}

public class ArrayTest {
    public int[] array;

    public ArrayTest(int size) {
        array = new int[size];
    }

    public int get(int index) {
        return array[index];
    }
}

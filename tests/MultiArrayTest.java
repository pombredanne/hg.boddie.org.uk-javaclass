public class MultiArrayTest {
    public int[][] multiArray;

    public MultiArrayTest(int[] multiSizes) {
        multiArray = new int[multiSizes[0]][multiSizes[1]];
    }

    public int get(int index1, int index2) {
        return multiArray[index1][index2];
    }
}

public class StringTest {
    private String s;
    private String s2 = new String("abc");
    private static String s3;
    private static String s4 = new String("xyz");

    public StringTest() {
        s = s2;
    }

    public StringTest(String newString) {
        s = newString;
    }

    public StringTest(String firstString, String secondString) {
        s = firstString + secondString;
    }
}

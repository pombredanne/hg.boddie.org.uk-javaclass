public class StringBufferTest {
    StringBuffer sb1;
    StringBuffer sb2;
    String s;
    public StringBufferTest(String a, String b) {
        sb1 = new StringBuffer(a);
        sb2 = new StringBuffer(b);
        s = a + b;
    }
}

public class FieldTest {
    private int a;
    protected int b = 123;
    protected FieldTestClass c;
    protected FieldTestClass d = null;
    public FieldTestClass e = new FieldTestClass(456);
    public static FieldTestClass f;
}

class FieldTestClass {
    public int a;

    public FieldTestClass(int a) {
        this.a = a;
    }
}

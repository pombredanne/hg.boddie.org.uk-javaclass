public class FieldTest {
    private int a;
    protected int b = 123;
    protected FieldTestClass c;
    protected FieldTestClass d = null;
    public FieldTestClass e = new FieldTestClass(456);
    public FieldTestClass f = new FieldTestClass(b + e.a);
    public static FieldTestClass g;
    public static FieldTestClass h = new FieldTestClass(789);

    public static void main(String[] args) {
        if (FieldTest.h != null && FieldTest.h.a == 789) {
            System.out.println("FieldTest.h.a correct: " + FieldTest.h.a);
        } else {
            System.out.println("FieldTest.h.a failed!");
        }
        FieldTest test = new FieldTest();
        if (test.h != null && test.h.a == 789) {
            System.out.println("test.h.a correct: " + test.h.a);
        } else {
            System.out.println("test.h.a failed!");
        }
        if (test.e != null && test.e.a == 456) {
            System.out.println("test.e.a correct: " + test.e.a);
        } else {
            System.out.println("test.e.a failed!");
        }
        if (test.f != null && test.f.a == 579) {
            System.out.println("test.f.a correct: " + test.f.a);
        } else {
            System.out.println("test.f.a failed!");
        }
    }
}

class FieldTestClass {
    public int a;

    public FieldTestClass(int a) {
        this.a = a;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4

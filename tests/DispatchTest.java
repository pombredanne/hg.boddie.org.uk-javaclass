public class DispatchTest {
    public int a;
    public float b;

    public DispatchTest() {
        this.a = 1;
        this.b = 2;
    }

    public DispatchTest(int a) {
        this.a = a;
        this.b = 2;
    }

    public DispatchTest(float b) {
        this.a = 1;
        this.b = b;
    }

    public DispatchTest(int a, float b) {
        this.a = a;
        this.b = b;
    }

    public void set(int a) {
        this.a = a;
    }

    public void set(float b) {
        this.b = b;
    }
}

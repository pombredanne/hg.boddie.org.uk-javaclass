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

    // The ordering of the methods probably should not prevent the most specific
    // method from being chosen, but this happens with a linear search of
    // appropriate methods.

    public int test(DispatchInterface obj) {
        return obj.test();
    }

    public int test(DispatchClass1 obj) {
        return obj.test() + 10;
    }

    public int testTest(DispatchInterface obj) {
        return test(obj);
    }
}

interface DispatchInterface {
    public int test();
}

class DispatchClass1 implements DispatchInterface {
    public int test() {
        return 1;
    }
}

class DispatchClass2 implements DispatchInterface {
    public int test() {
        return 2;
    }
}

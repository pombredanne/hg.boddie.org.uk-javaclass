public class ExceptionTest {

    public int testCatch() {
        try {
            throw new MyException();
        } catch (MyException exc) {
            return 1;
        }
    }

    public int testFinally(int x) {
        try {
            if (x == 0) {
                throw new MyException();
            } else if (x == 1) {
                throw new MyOtherException();
            }
        } catch (MyException exc) {
            x = 3;
        } catch (MyOtherException exc) {
            x = 2;
        } finally {
            x = 1;
        }
        return x;
    }
}

class MyException extends java.lang.Exception {
}

class MyOtherException extends java.lang.Exception {
}

// vim: tabstop=4 expandtab shiftwidth=4

public class ExceptionTest {

    public int testThrow(int x) throws java.lang.Exception {
        if (x == 0) {
            throw new MyException();
        } else if (x == 1) {
            throw new MyOtherException();
        } else {
            return 1;
        }
    }

    public int testCatch(int x) {
        try {
            if (x == 0) {
                throw new MyException();
            } else if (x == 1) {
                throw new MyOtherException();
            } else {
                x = 1;
            }
        } catch (MyException exc) {
            x = 3;
        } catch (MyOtherException exc) {
            x = 2;
        }
        return x;
    }

    public int testIncomingCatch(int x) {
        try {
            return testThrow(x);
        } catch (MyException exc) {
            return 3;
        } catch (MyOtherException exc) {
            return 2;
        } catch (java.lang.Exception exc) {
            return -1; // Should be unreachable, really.
        }
    }

    public int testFinally(int x) throws java.lang.Exception {
        try {
            if (x == 0) {
                x = 3;
                throw new MyException();
            } else if (x == 1) {
                x = 2;
                throw new MyOtherException();
            }
            x = 1;
        } finally {
            x += 10;
        }
        return x;
    }

    public int testCatchFinally(int x) throws MyUncheckedException {
        try {
            if (x == 0) {
                throw new MyException();
            } else if (x == 1) {
                throw new MyOtherException();
            } else if (x == 2) {
                throw new MyUncheckedException();
            }
            x = 1;
        } catch (MyException exc) {
            x = 3;
        } catch (MyOtherException exc) {
            x = 2;
        } finally {
            x += 10;
        }
        return x;
    }

    public int testMultipleCatch(int x, int y) {
        try {
            x = testThrow(x);
        } catch (MyException exc) {
            x = 3;
        } catch (MyOtherException exc) {
            x = 2;
        } catch (java.lang.Exception exc) {
            x = -1; // Should be unreachable, really.
        }

        try {
            x += 10 * testThrow(y);
        } catch (MyException exc) {
            x += 30;
        } catch (MyOtherException exc) {
            x += 20;
        } catch (java.lang.Exception exc) {
            x += -10; // Should be unreachable, really.
        }
        return x;
    }
}

class MyException extends java.lang.Exception {
}

class MyOtherException extends java.lang.Exception {
}

class MyUncheckedException extends java.lang.Exception {
}

// vim: tabstop=4 expandtab shiftwidth=4

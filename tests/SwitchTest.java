public class SwitchTest {

    public int test(int x) {
        switch (x) {
            case 0:

            case 1:
            x = x + 10;
            break;

            case 2:
            x = x + 20;
            break;

            default:
            break;
        }

        return x;
    }
}

public class ValueSubclass extends Value {

    /**
     * Test of subclass initialisation with super usage and foreign object initialisation.
     */
    public ValueSubclass(int x) {
        super(x);
        Value tmp = new Value(42);
    }

    /**
     * Test of overriding.
     */
    public void setValue(int x) {
        this.value = -x;
    }

    /**
     * Test of overriding and super methods.
     */
    public int add(int x) {
        return super.add(-x);
    }

    /**
     * Test of objects as arguments.
     */
    public void setValueObject(Value v) {
        this.value = v.getValue();
    }
}

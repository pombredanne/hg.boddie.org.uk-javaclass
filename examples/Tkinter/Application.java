public class Application extends tkjava.Frame {
    private tkjava.Button quit, hiThere;

    public Application() {
        super();
        this.pack();
        this.createWidgets();
    }

    public void createWidgets() {
        this.quit = new tkjava.Button(this);
        this.quit.pack();
        this.hiThere = new tkjava.Button(this);
        this.hiThere.pack();
    }
}

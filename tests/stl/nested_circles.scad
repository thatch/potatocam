$fn=32;

linear_extrude(height=10) {
  difference() {
    circle(d=60);
    circle(d=50);
  }

  difference() {
    circle(d=40);
    circle(d=30);
  }

  difference() {
    circle(d=20);
    circle(d=10);
  }
}

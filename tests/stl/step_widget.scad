$fn=64;
difference() {
  translate([-15,-15,0]) cube([30,30,10]);
  translate([0,0,8]) cylinder(d=20,h=10);
  translate([0,0,4]) cylinder(d=14,h=10);
  hull() {
    $fn=32;
    translate([0,0,-1]) cylinder(d=6,h=12);
    translate([20,0,-1]) cylinder(d=6,h=12);
  }
}

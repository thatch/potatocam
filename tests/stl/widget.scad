difference() {
  cube([40,40,12]);
  translate([0,0,3]) linear_extrude(height=20) hull() {
    translate([10,10]) circle(r=3,$fn=32);
    translate([10,30]) circle(r=3,$fn=32);
    translate([30,20]) circle(r=6,$fn=32);
  }
  translate([0,0,-1]) linear_extrude(height=20) hull() {
    translate([15,20]) circle(r=3,$fn=32);
    translate([27,20]) circle(r=3,$fn=32);
  }
}

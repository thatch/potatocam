num_holes = 55;

$fs=0.01;
linear_extrude(height=5) difference() {
  square([55,55], center=true);
  ds = rands(0, 6, num_holes, 1);
  xs = rands(-25, 25, num_holes, 4);
  ys = rands(-25, 25, num_holes, 5);
  for(t=[0:num_holes-1]) {
    pt = [xs[t], ys[t]];
    translate(pt) circle(d=ds[t]);
  }
}

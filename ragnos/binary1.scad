difference() {
  union() {
    difference() {
      union() {
        cylinder(h=4, r=60);
        translate([0, 0, 4]) {
          difference() {
            cylinder(h=12, r=50);
            cylinder(h=12, r=45);
          }
        }
      }  
      translate([-60, 0, 0]) cube([120, 60, 16]);
      translate([-60, -60, 0]) cube([60, 120, 16]);
    }

    translate([-20, -60, 0]) cube([20, 60, 4]);
    translate([-20, -50, 0]) cube([20, 5, 16]);

    translate([-20, 0, 0]) cube([80, 20, 4]);
    translate([45, 0, 0]) cube([5, 20, 16]);
  }
  
  translate([10, -10, 0]) cylinder(h=4, r=20);

  translate([-20, -47.5, 16]) rotate([0, 135, 0]) cylinder(h=30, r=2.5);
  translate([47.5, 20, 16]) rotate([135, 0, 0]) cylinder(h=30, r=2.5);

}

//translate([-20, -47.5, 16]) rotate([0, 135, 0]) cylinder(h=30, r=2.5);

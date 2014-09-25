cr = 3.3;
      union() {
        circle(r=cr); 
        translate([-cr / 2, -cr / 2, 0]) square([cr, cr]);
      }


// difference() {
//   rotate_extrude(convexity = 10, $fn=40)
//     translate([70, 0, 0])
//       union() {
//         circle(r=3.3); 
//         cube([33, 33, 33]);
//       }
//   rotate_extrude(convexity = 10, $fn=40)
//     translate([70, 0, 0])
//       circle(r=2.5);
//   translate([-100, -100, -20]) cube([200, 100, 30]);
//   translate([-100, -100, -20]) cube([100, 200, 30]);
// }

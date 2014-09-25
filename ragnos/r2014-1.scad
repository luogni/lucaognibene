module rotate_extrude_90(trx, w, cut90=true, cut45=true) {
    difference() {
	rotate_extrude(convexity = 10, $fn=40) translate([trx, 0, 0]) children();
	if (cut90 == true) {
	    translate([-trx - w, -trx - w, -w * 2]) cube([trx * 2 + w * 2, trx + w, w * 4]);
	    translate([-trx - w, -trx - w, -w * 2]) cube([trx + w, trx * 2 + w * 2, w * 4]);
	}
	if (cut45 == true) {
	    translate([0, 0, -w * 2]) rotate([0, 0, 45]) cube([trx + w, trx + w, w * 4]);
	}
    } 
}

module binary_2014_1(d1, d2, h1=10, rad=70) {
    cr1 = d1 / 2;
    cr2 = d2 / 2;
    rotate_extrude_90(rad, h1 * 2) {
	difference() {
	    union() {
		circle(r=cr1);
		translate([-cr1 / 2, -cr1 - h1, 0]) square([cr1, cr1 + h1]);
	    }
	    circle(r=cr2);
	}
    }
}

module binary_2014_2(d1, d2, h1=10, rad=70, internal_wall=1) {
    cr1 = d1 / 2;
    cr2 = d2 / 2;    
    rotate_extrude_90(rad, h1 * 2) {
	difference() {
	    union() {
		difference() {
		    circle(r=cr1, $fn=50);
		    translate([- d1/2, - (d1 + h1)/2, 0]) square([d1, (d1 + h1)/2]);
		    translate([- d1/2, - (d1 + h1)/2, 0]) square([d1/2, (d1 + h1)/2]);
		}
		translate([-cr1, -cr1 - h1, 0]) square([d1, cr1 + h1]);
	    }
	    union() {
		circle(r=cr2, $fn=50);
		translate([-cr2, -cr2 - h1, 0]) square([cr2*2, h1 + cr2]);
	    }
	}
	translate([-cr2, -cr2 - internal_wall, 0]) square([cr2*2, internal_wall]);
    }
}

module tyre_2014_1(w, h, d, hole) {
    h = h / 2;
    hole_x = h - d/3;
    echo("max tyre_high_external", h * 2);
    echo("max tyre_high_internal", (hole_x - d/2) * 2);
    echo("max hole height", d/2 + (h - hole_x));
    echo("max hole width", d);
    difference() {
	rotate_extrude_90(0, 20, false, false) {
	    difference() {
		square([h, w]);
		translate([hole_x, w/2, 0]) circle(d=d);
		translate([hole_x, (w - d) / 2, 0]) square([d, d]);
	    }    
	}
	translate([0, 0, w/2]) cylinder(h=w, d=hole, $fn=50);
    }
}

module enter_block_2014_1(w, h, d, hole, deg) {
    difference() {
	cube([w, h, d]);
	translate([w, h/2, d]) rotate([0, -deg, 0]) cylinder(h=50, d=hole, $fn=50);
    }
}

module enter_block_2014_2(w, h, d, hole, deg) {
    difference() {
	union() {
	    cube([w, h, d/2]);
	    translate([0, h/2, d/2]) rotate([0, 90, 0]) cylinder(h=w, d=h, $fn=50);
	}
	translate([w, h/2, d]) rotate([0, -deg, 0]) cylinder(h=50, d=hole, $fn=50);
    }
}

screw_hole = 4;
wire_hole = 4;
binary_size = 6;

//tyre_2014_1(10, 22, binary_size + 0.5, screw_hole);
//enter_block_2014_2(20, binary_size, 6, wire_hole + 0.2, 115);
//binary_2014_2(binary_size, wire_hole, 5, 70);

translate([-40, 0, binary_size/2 + 4]) binary_2014_1(binary_size, wire_hole, 4, 70);
translate([-30, 0, binary_size/2 + 4]) binary_2014_1(binary_size, wire_hole, 4, 70);

translate([-20, 0, binary_size/2 + 5]) binary_2014_2(binary_size, wire_hole, 5, 70);
translate([-10, 0, binary_size/2 + 5]) binary_2014_2(binary_size, wire_hole, 5, 70);

translate([0, 0, 0]) enter_block_2014_2(20, binary_size, 6, wire_hole + 0.2, 115);
translate([11, 20, 0]) tyre_2014_1(10, 22, binary_size + 0.5, screw_hole);

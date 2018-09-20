
HEADER_HEIGHT=0.5;
PI_HEIGHT=5.5;
VIEWPORT = [88, 58, 0.2];
SCREEN_PCB = [94.3,61.4, 2.1];
SCREEN_LCD = [94.3, 60.9, 1.3];
SCREEN_PLASTIC = [94.3, 61.1, 2.7];
SCREEN_REGISTER = [6.3, 0.9, 1.3];
SCREEN_HEADER = [33, 5, 12.7];
PI_BOTTOM_CLEAR=3.5;
SUPPORT_H = 16.5;
SUPPORT_D = 2.5;
SUPPORT_BASE_D = 5.5;
CASE_HEIGHT = 24.5;
$fn=50;
module screen() {
    union() {
    cube(SCREEN_PCB);
        translate([0,0,SCREEN_PCB[2]]) {
            cube(SCREEN_PLASTIC);
            translate([0,0,SCREEN_PLASTIC[2]-0.01]) {
                cube(SCREEN_LCD);
            };
            translate([0, -SCREEN_REGISTER[1]+0.01, 0]) {
                cube(SCREEN_REGISTER);
                translate([49, 0, 0]) {
                    cube(SCREEN_REGISTER);
                };
            };
            translate([0, SCREEN_PCB[1]-0.321, 0]) {
                cube(SCREEN_REGISTER);
                translate([49, 0, 0]) {
                    cube(SCREEN_REGISTER);
                };
                translate([83.3, 0, 0]) {
                    cube(SCREEN_REGISTER);
                };
            };
            translate([SCREEN_PCB[0]+(SCREEN_REGISTER[2]/2),0,0]) {
                rotate([0,0,90]) cube(SCREEN_REGISTER);
            };
        };
        translate([15.6, SCREEN_PCB[1]-1-SCREEN_HEADER[1], -SCREEN_HEADER[2]]) {
            cube(SCREEN_HEADER);
        };
    };
}

color([0,0,1.0]) {
import("C:\\Users\\Austen\\Downloads\\rpi\\files\\Raspberry_Pi_3_Light_Version.STL");
};
/*
translate([-7,-3.5,SCREEN_HEADER[2]+HEADER_HEIGHT+PI_HEIGHT]) {
    screen();
};
*/
translate([-10, -7, -5]) {
    difference() {
        color([0,0,1,0.3]) cube([103, 70, 26.7]);
        union() {
            translate([16.5,-2,5]) {
                cube([14,20,10]);
            };
            translate([3,3.5,5+SCREEN_HEADER[2]+HEADER_HEIGHT+PI_HEIGHT]) {
                screen();
            };
            translate([4.75,3.75,3.75]) {
                cube([96.7, 61.3, 23.3]);
            };
        };
    };
    translate([16.25,12.1,3.5]){
        cylinder(d=SUPPORT_BASE_D, h=3);
        translate([0,0,2.99]) cylinder(d=SUPPORT_D, h=2);
    };
    translate([74.25,12.1,3.5]){
        cylinder(d=SUPPORT_BASE_D, h=3);
        translate([0,0,2.99]) cylinder(d=SUPPORT_D, h=2);
    };
    translate([16.25,61.1,3.5]){
        cylinder(d=SUPPORT_BASE_D, h=3);
        translate([0,0,2.99]) cylinder(d=SUPPORT_D, h=2);
    };
    translate([74.25,61.1,3.5]){
        cylinder(d=SUPPORT_BASE_D, h=3);
        translate([0,0,2.99]) cylinder(d=SUPPORT_D, h=2);
    };
};
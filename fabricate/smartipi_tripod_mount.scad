use <gopro_mounts_mooncactus.scad>

BASE_R = 20;
BASE_H = 10;
HEX_D = 8; 
inch = 25.4;

SEPARATION = 156;
separation = (29.63 + 21.28)/2;
MOUNT_W = 20;
TILT = 20;
UP = 18; /// lift flange nut up to mount

module flange_nut(d, D, h, H, UP){
  translate([0, 0, UP]){
    translate([0, 0, -.01])cylinder(h=h + .01, d=D, $fn=50);//flange
    translate([0, 0, h])cylinder(h=1, d1=D, d2=D/2, $fn=50);//flange
    cylinder(h=H+.01, d=d, $fn=6);//nut
  }
  cylinder(d=D, h=UP, $fn=50);
}
    
difference(){
  translate([-(SEPARATION + 20)/2, -(separation + 12)/2, 0])cube([SEPARATION + 20, separation + 12, 25]);
  
  // screw holes
  translate([+SEPARATION/2 + 1.85, +separation / 2, -50])cylinder(d=4, h=100, $fn=50);
  translate([-SEPARATION/2 - 1.85, +separation / 2, -50])cylinder(d=4, h=100, $fn=50);
  translate([+SEPARATION/2 + 1.85, -separation / 2, -50])cylinder(d=4, h=100, $fn=50);
  translate([-SEPARATION/2 - 1.85, -separation / 2, -50])cylinder(d=4, h=100, $fn=50);
  // nut cutouts
  translate([+SEPARATION/2 + 1.85, +separation / 2, 4])cylinder(d=HEX_D, h=100, $fn=6);
  translate([-SEPARATION/2 - 1.85, +separation / 2, 4])cylinder(d=HEX_D, h=100, $fn=6);
  translate([+SEPARATION/2 + 1.85, -separation / 2, 4])cylinder(d=HEX_D, h=100, $fn=6);
  translate([-SEPARATION/2 - 1.85, -separation / 2, 4])cylinder(d=HEX_D, h=100, $fn=6);
  
  rotate([0, 0, 180])
    translate([0, -(separation+16)/2-1, 40])rotate([0, TILT, 0])cube([SEPARATION + 20, separation + 16 + 2, 50]);
  rotate([0, 0, 0])
    translate([0, -(separation+16)/2-1, 40])rotate([0, TILT, 0])cube([SEPARATION + 20, separation + 16 + 2, 50]);

  // oval cutout
  translate([0, -(separation+12+2)/2, -20])scale([1, 1, .45])rotate([0, 90, 90])
    cylinder(d=SEPARATION *1.05, h=separation+12+2, $fn=100);

  // mount nut
  scale([1.08, 1.08, 1])flange_nut(d=7 * inch/16.*1.05, D=19*inch/32*1.05, h=1.5, H=6, UP=UP);

  // mount nut
  cylinder(d=.3*inch, h=100, $fn=50);
}

//translate([0, 0, -UP])flange_nut(d=7 * inch / 16. * 1.05, D=19 * inch / 32, h=1.5, H=6, UP=UP);

if(true){
  translate([-SEPARATION/2, 0, -3])union(){
    translate([-15/2, -36/2, 0])cube([15, 36, 3]);
    translate([0, 0, -11])rotate([90, 0, 90])gopro_connector("triple");
  }
  
  translate([SEPARATION/2, 0, -3])union(){
    translate([-15/2, -36/2, 0])cube([15, 36, 3]);
    translate([0, 0, -11])rotate([90, 0, -90])gopro_connector("triple");
  }
  
 }

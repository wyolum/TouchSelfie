diameter = 6;
length = 12;
screwd = 3;

for (x= [0:diameter+1:diameter+1],y=[0:diameter+1:diameter+1]){
    translate([x,y,0])difference(){
        cylinder(d=diameter,$fn = 6,h=length);
        translate([0,0,-1])cylinder(d=screwd,h=length+2,$fn=99);
    }
}
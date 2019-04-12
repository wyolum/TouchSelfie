inch=25.4;

baselength=3*inch;
basewidth = .5*inch;
baseheight = .3*inch;
standheight = 3.2 * inch;
railsep = 58;

tripod_mount_width = 100;

screw_radius=4/2;
screwsep = 49;
mountdepth=2.5;
mountheight=.5*inch;
mountscrewlength=6 + 6;

module square(w=11.15, screw=6){
  r = w * sqrt(2)/2;
  linear_extrude(h=100){
    polygon(points=[
		    [r * cos(0*90), r * sin(0*90)],
		    [r * cos(1*90), r * sin(1*90)],
		    [r * cos(2*90), r * sin(2*90)],
		    [r * cos(3*90), r * sin(3*90)],
		    ],
	    paths=[[0, 1, 2, 3, 4, 5]]);
	    
  }
  translate([0, 0, -20])cylinder(d=screw, h=20, $fn=30);
}

module quarter_round(radius, length){
  intersection(){
    cylinder(r=radius, h=length);
    cube([radius, radius, length]);
  }
}


module hex(w=.5 * inch, screw=inch/4.){
  r = w * sqrt(3)/4;
  r = w/2.;
  linear_extrude(h=7 * inch / 16.){
    polygon(points=[
		    [r * cos(0*60), r * sin(0*60)],
		    [r * cos(1*60), r * sin(1*60)],
		    [r * cos(2*60), r * sin(2*60)],
		    [r * cos(3*60), r * sin(3*60)],
		    [r * cos(4*60), r * sin(4*60)],
		    [r * cos(5*60), r * sin(5*60)]
		    ],
	    paths=[[0, 1, 2, 3, 4, 5]]);
	    
  }
  translate([0, 0, -10])cylinder(d=screw, h=20, $fn=30);
}

module square(w=11.15, screw=6){
  r = w * sqrt(2)/2;
  linear_extrude(h=100){
    polygon(points=[
		    [r * cos(0*90), r * sin(0*90)],
		    [r * cos(1*90), r * sin(1*90)],
		    [r * cos(2*90), r * sin(2*90)],
		    [r * cos(3*90), r * sin(3*90)],
		    ],
	    paths=[[0, 1, 2, 3]]);
	    
  }
  translate([0, 0, -20])cylinder(d=screw, h=20, $fn=30);
}

//translate([-35.2, 0, 0])cube(.489 * inch); test for bolt size
//rotate(a=90, v=[1, 0, 0])hex();
module mount(screw=true){
  translate([.01, mountdepth + .01, 0])scale([1.01, 1.01, 1])
  rotate(a=180, v=[1, 0, 0])
    union(){
    translate([0, 0, mountheight/3])rotate(v=[0, 0, 1], a=90)translate([0, 0, -0.01])cube([mountdepth, baseheight, mountheight/3+.02]);
    rotate(v=[0,1,0], a=-90)linear_extrude(height=baseheight)
      polygon(points=[
		      [0, 0],
		      [mountheight/3, mountdepth],
		      [mountheight/3, 0],
		      ], paths=[[0, 1, 2]]);
    translate([-baseheight, 0, mountheight])rotate(v=[0,1,0], a=90)linear_extrude(height=baseheight)
      polygon(points=[
		      [0, 0],
		      [mountheight/3, mountdepth],
		      [mountheight/3, 0],
		      ], paths=[[0, 1, 2]]);

    if(screw){
    translate([-baseheight/2, mountscrewlength, mountheight/2])rotate(v=[1, 0, 0], a=90)union(){
      cylinder(h=mountscrewlength, d=3, $fn=20);
    }
    }
  }
}

module rail(){
  translate([-baseheight/2, 5, 20])
  difference(){
    union(){
      translate([baseheight, 10-mountdepth, 20])mount(screw=false);
      translate([baseheight, 10-mountdepth, 20 + screwsep])mount(screw=false);
      translate([0, -5.5, -23])cube([baseheight, 18, 5]); 

      //translate([baseheight, basewidth, standheight - baseheight*1.5])
      //rotate(v=[0, 0, -1], a=90)
      //rotate(v=[1, 0, 0], a=90)
	//quarter_round(radius=basewidth, length=baseheight);
      translate([0, 10, -20])
	cube([baseheight, mountdepth, screwsep + .8*inch + 20]);
      translate([0, -5.5, -3-20])
	difference()
	{
	  intersection(){
	    cube([baseheight, 18, 30]);
	    translate([0, 0, 3.5])
	      rotate(a=30, v=[-1, 0, 0])
	      cube([baseheight, 18, 50]);
	  }
	  translate([0,0, -5])intersection(){
	    cube([baseheight, 18, 30]);
	    translate([0, 0, 3.5])
	      rotate(a=30, v=[-1, 0, 0])
	      cube([baseheight, 18, 50]); 
	  }
	}
    }
    union(){
      translate([baseheight, basewidth-mountdepth, 20])mount();
      translate([baseheight, basewidth-mountdepth, 20 + screwsep])mount();
    }
  }
}
module top(){
  difference(){
    union(){
      translate([-railsep/2, -basewidth/2, 0])rail();
      // translate([railsep/2, -basewidth/2, 0])rail();
    }
    union(){
      rotate(v=[1, 0, 0], a=90)bottom();
      rotate(v=[1, 0, 0], a=-90)bottom();
    }
  }
}

module bottom_attach(){
  translate([baseheight/10 - 2 * baseheight/5, 0, 0])rotate(v=[0, 1, 0], a=90)cylinder(h=baseheight/5, r=basewidth/2);
  translate([baseheight/10 + 0 * baseheight/5, 0, 0])rotate(v=[0, 1, 0], a=90)cylinder(h=baseheight/5, r=basewidth/2);

  translate([baseheight/10 - 2 * baseheight/5, -basewidth/2, -basewidth * .6])cube([baseheight/5, basewidth, basewidth * .6]);
  translate([baseheight/10 + 0 * baseheight/5, -basewidth/2, -basewidth * .6])cube([baseheight/5, basewidth, basewidth * .6]);
}
module handle(){
  extra = 0; // extra width for base
  base_d = railsep + baseheight;
  translate([-baselength * .0 + basewidth*0, 0, -.5 * baseheight])
    scale([1, 1, .4])translate([0, basewidth/2, 0])
    rotate(v=[1, 0, 0], a=90)
    difference(){
    translate([0, 0, -extra])cylinder(r=base_d/2, h=basewidth + 3 * extra);
    translate([0, 0, -1-extra])cylinder(r=base_d/2 - 5 * baseheight/5, h=basewidth + 2+2 * extra);
    translate([-50, 0, -1-extra])cube(100, 100, 10);
  }
}

module bottom(){
  difference(){
    union(){
      translate([-railsep/2, 0, 0])bottom_attach();
      translate([+railsep/2, 0, 0])bottom_attach();
      handle();
    }
    translate([0, 0, -20])square();
  }
}

/*
rotate(v=[1, 0, 0], a=-90)
difference(){
  union(){
    top();
    bottom();
  }
  translate([-50, 0, 0])rotate(v=[0, 1, 0], a=90)cylinder(h=100, r=screw_radius, $fn=100);
}
*/
difference(){
union(){
  rail();
  translate([-railsep, 0, 0]) rail();
  difference(){
    scale([1, 1, 1])
      translate([baseheight/2, basewidth/2-6, -2])
      rotate(v=[0, 1, 0], a=-90)
      cylinder(h=railsep + baseheight, r=basewidth/2);
    translate([-railsep/2, basewidth/2-6, 0])
      // square();
      hex();
    translate([-tripod_mount_width/2 - railsep/2, -10, -13])
      cube([tripod_mount_width, 50, 10]);
  }
}
translate([-52.5,-6,-10])cylinder(d=7,h=20);
}

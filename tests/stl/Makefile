.PHONY: all
all: stl

.PHONY: stl
stl: cube.stl step_cube.stl stone_wheel.stl nested_circles.stl widget.stl widget_hq.stl step_widget.stl circles.stl

%.stl: %.scad
	openscad -o $@ $<

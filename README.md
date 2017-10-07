# PotatoCAM

This project started out of a need to arrive at efficient enough toolpaths for
home milling, where you don't do many toolchanges and want to have a highly
automated (e.g. from a makefile) workflow.

## Goals

* 2.5D CAM
* Configurable tolerance
* STL input
* Works headless
* Makefile-friendly configuration
* GUI to simulate and graph MRR, cut width (radial engagement), cut depth, etc
  (acceleration makes this hard!)

With human input, commercial packages of all costs do a reasonable job at
creating gcode.  My main goal is not to be "better" than them at gcode
generation, but to be more repeatable and easier to run from something like
octoprint.

## A base for experiments

## Special cutting strategy

The bundled strategy is based on spirals and arcs to attempt constant TEA
through material simulation.  In order to generate this, we construct a
heightmap of the cuttable surfaces, a heightmap that represents the stock, and
histogram to determine good stepdowns.

Once thresholded (can the cutter be at a certain depth), we find the voronoi
skeleton, clear largest intersection by spiral, then follow remaining bones by
arcs (using material simulation to determine cutter backoff -- easier than
offsetting polygons).  This is roughing.

For finish, we offset polygon and follow path.

## Notes vs other CAM

* Only does climb or conventional.  Bidirectional roughing is a thing, along
  with clubs, but probably not in the first version.

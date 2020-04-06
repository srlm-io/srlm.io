---
layout: post
title: OpenSCAD Thumbnailer for Gnome
tags: [openscad, gnome, 3d, cad]
---

![OpenSCAD thumbnailer example](/public/images/2015/12/15/openscad_thumbnailer.png)

If you're a heavy user of [OpenSCAD](http://www.openscad.org/) then you'll eventually get to the point where you have folders full of `.scad` files, with no idea what they are. Here's how to make a thumbnailer that will automatically generate a preview image that will display .scad files in Nautilus.

<!--endexcerpt-->

First, create a script that will generate the previews. It will get it's input, output, and size as arguments from the call in the `scad.thumnailer` script below.

Install in `/home/user/bin/scad-thumbnailer.sh` (replace `user` with your username):

```
#!/usr/bin/env sh

/usr/bin/openscad --imgsize=$3,$3 -o $2.png $1
mv $2.png $2
```

Make sure that the file is executable (`chmod +x`).

Next, create the thumbnailer that Gnome will call when it encounters a `.scad` file. Parameters are in the form of string replace, and are moderately well [documented](https://developer.gnome.org/integration-guide/stable/thumbnailer.html.en).

Install in `/usr/share/thumbnailers/scad.thumbnailer` (replace `user` with your username):

```
[Thumbnailer Entry]
Exec=/home/user/bin/scad-thumbnailer.sh %i %o %s
MimeType=application/x-openscad;
```

Make sure that the `.scad` files have the correct MIME type. You can check by right clicking on a `.scad` file in Nautilus and checking that the MIME type is `application/x-openscad`.

Once everything is installed you need to close all your Nautilus windows before the new thumbnailer will be used. You'll end up with nice previews of all your 3D models.

If your files continue to show a generic thumbnail then you may need to clear your thumbnail cache with ` rm -rf ~/.cache/thumbnails/*`, followed by a Nautilus restart.

If you're looking to generate thumbnails of your `.stl` files then take a look at this [package](http://www.thingiverse.com/thing:258653).

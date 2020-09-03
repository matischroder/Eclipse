#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  demo_window.py
#
#  Copyright 2020 John Coppens <john@jcoppens.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from figures import Figure, Rectangle, Ellipse, Curve, ArcoEllipse
from gi.repository import Gdk, Gtk, GooCanvas, GdkPixbuf
import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GooCanvas', '2.0')


def make_rgba(color_string, alpha=1):
    c = Gdk.RGBA()
    c.parse(color_string)
    c.alpha = alpha
    return c


DEFAULT_STROKE_COLOR = make_rgba("black")
DEFAULT_FILL_COLOR = make_rgba("green", 0.5)


class Toolbox(Gtk.Frame):
    def __init__(self, layer):
        super(Toolbox, self).__init__(
            label="Herramientas",
            margin=6)
        self.layer = layer
        self.layer.connect("button-press-event", self.layer_click)
        self.figure = None

        vbox = Gtk.VBox(
            margin=6)
        self.add(vbox)

        lbl = Gtk.Label(label="Ancho trazo:", xalign=0)
        vbox.pack_start(lbl, False, False, 0)
        self.spbtn = Gtk.SpinButton.new_with_range(0, 20, 0.1)
        self.spbtn.set_value(1.0)
        vbox.pack_start(self.spbtn, False, False, 0)

        lbl = Gtk.Label(label="Color trazo:", xalign=0)
        vbox.pack_start(lbl, False, False, 0)
        self.stroke_colbtn = Gtk.ColorButton(
            use_alpha=True,
            rgba=DEFAULT_STROKE_COLOR)
        vbox.pack_start(self.stroke_colbtn, False, False, 0)

        lbl = Gtk.Label(label="Color relleno:", xalign=0)
        vbox.pack_start(lbl, False, False, 0)
        self.fill_colbtn = Gtk.ColorButton(
            use_alpha=True,
            rgba=DEFAULT_FILL_COLOR)
        vbox.pack_start(self.fill_colbtn, False, False, 0)

        lbl = Gtk.Label(label="Figuras:", xalign=0)
        vbox.pack_start(lbl, False, False, 0)

        for file, tooltip, figure in (
            ("rectangle.svg", "Rectángulo",          Rectangle),
            ("ellipse.svg", "Elipse", Ellipse),
            ("line.svg",      "Arco Ellíptico",              ArcoEllipse),
            ("qbezier.svg",   "Curve",   Curve),
        ):
            try:
                pxb = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    file, -1, 32, True)
                img = Gtk.Image.new_from_pixbuf(pxb)
            except:
                img = Gtk.Image.new_from_file("invalid")
            btn = Gtk.Button(
                image=img,
                tooltip_text=tooltip,
                relief=Gtk.ReliefStyle.NONE)
            btn.connect("clicked", self.figure_selected, figure)
            vbox.pack_start(btn, False, False, 0)

    def figure_selected(self, btn, which):
        self.figure = which

    def layer_click(self, src, tgt, event):
        if self.figure is not None:
            # self.figure contiene al objeto a instanciar - lo hacemos aqui.
            self.figure(self, event.x, event.y)


class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect("destroy", self.quit)
        self.set_default_size(600, 600)

        canvas = GooCanvas.Canvas(
            hexpand=True,
            vexpand=True)
        cvroot = canvas.get_root_item()

        scroller = Gtk.ScrolledWindow()
        scroller.add(canvas)

        toolbox = Toolbox(cvroot)

        grid = Gtk.Grid()
        grid.attach(scroller, 0, 0, 1, 1)
        grid.attach(toolbox, 1, 0, 1, 1)

        self.add(grid)

        self.show_all()

    def quit(self, event):
        Gtk.main_quit()

    def run(self):
        Gtk.main()


def main(args):
    mainwdw = MainWindow()
    mainwdw.run()

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

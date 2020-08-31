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

from svg.path import QuadraticBezier
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


DEFAULT_STROKE_COLOR = make_rgba("yellow")
DEFAULT_FILL_COLOR = make_rgba("green", 0.5)


def to_rgba(color):
    """ Conversion de formato Gdk.RGBA (r, g, b y a en valores de 0 a 1.0)
        resultado de get_rgba) a integer para GooCanvas.
    """
    return ((int(color.red * 255) << 24) +
            (int(color.green * 255) << 16) +
            (int(color.blue * 255) << 8) +
            int(color.alpha * 255))


class Marker():
    def __init__(self, layer, x, y, radius=8, color="White", callback=None):
        self.x, self.y = x, y
        self.radius = radius
        self.color = color
        self.position = None
        self.callback = callback

        self.marker = GooCanvas.CanvasEllipse(
            parent=layer,
            center_x=x, center_y=y,
            radius_x=radius, radius_y=radius,
            stroke_color=color,
            fill_color_rgba=0xffffff20,
            line_width=2)

        self.marker.connect("button-press-event", self.button_pressed)
        layer.connect("button-release-event", self.button_released)
        layer.connect("motion-notify-event", self.button_moved)

    def button_pressed(self, src, tgt, event):
        self.position = event.x, event.y
        return True

    def button_released(self, src, tgt, event):
        self.position = None

    def moveto(self, x, y):
        self.marker.set_property("center-x", x)
        self.marker.set_property("center-y", y)

    def button_moved(self, src, tgt, event):
        if self.position is None:
            return

        dx = event.x - self.position[0]
        dy = event.y - self.position[1]

        new_x = self.marker.get_property("center-x") + dx
        new_y = self.marker.get_property("center-y") + dy

        self.moveto(new_x, new_y)

        self.position = new_x, new_y
        if self.callback is not None:
            self.callback(new_x, new_y)


class Figure():
    """
    """

    def __init__(self, tbox):
        """ Tarea comun: Buscar colores, y ancho del trazo actualmente
            seleccionados.
        """
        self.tbox = tbox

        self.stroke_color = to_rgba(self.tbox.stroke_colbtn.get_rgba())
        self.fill_color = to_rgba(self.tbox.fill_colbtn.get_rgba())
        self.line_width = self.tbox.spbtn.get_value()


class Rectangle(Figure):
    def __init__(self, tbox, x, y):
        super(Rectangle, self).__init__(tbox)
        self.origin = x, y
        self.marker1 = Marker(self.tbox.layer, x, y, color="Red",
                              callback=self.moveto)

        self.rect = GooCanvas.CanvasRect(       # TODO
            parent=tbox.layer,
            x=x, y=y,
            width=0, height=0,
            fill_color_rgba=self.fill_color,
            stroke_color_rgba=self.stroke_color,
            line_width=self.line_width)

        self.id_release = tbox.layer.connect("button-release-event",
                                             self.button_released)
        self.id_motion = tbox.layer.connect("motion-notify-event",
                                            self.button_moved)

    def set_x_y(self, x, y):
        self.rect.set_property('x', x)
        self.rect.set_property('y', y)

    def get_x_y(self):
        return (self.rect.get_property('x'),
                self.rect.get_property('y'))

    def set_w_h(self, w, h):
        x, y = self.get_x_y()

        if w < 0:
            x += w
            w = -w
        if h < 0:
            y += h
            h = -h

        self.set_x_y(x, y)
        self.rect.set_property('width', w)
        self.rect.set_property('height', h)

    def button_released(self, src, tgt, event):
        w = event.x - self.origin[0]
        h = event.y - self.origin[1]
        self.set_w_h(w, h)

        self.tbox.layer.disconnect(self.id_release)
        self.tbox.layer.disconnect(self.id_motion)

        self.marker2 = Marker(self.tbox.layer, event.x, event.y,
                              color="Yellow",
                              callback=self.resize)

    def moveto(self, x, y):
        self.set_x_y(x, y)
        w = self.rect.get_property('width')
        h = self.rect.get_property('height')
        self.marker2.moveto(x + w, y + h)

    def resize(self, xnew, ynew):
        x, y = self.get_x_y()
        self.set_w_h(xnew - x, ynew - y)

    def button_moved(self, src, tgt, event):
        w = event.x - self.origin[0]
        h = event.y - self.origin[1]
        self.set_w_h(w, h)


class Qbezier(Figure):
    def __init__(self, tbox, x, y):
        super(Qbezier, self).__init__(tbox)
        self.origin = x, y
        self.marker1 = Marker(self.tbox.layer, x, y, color="Red",
                              callback=self.moveto)

        self.quadratic = GooCanvas.CanvasEllipse(
            parent=tbox.layer,
            x=x, y=y,
            width=0, height=0,
            stroke_color_rgba=self.stroke_color,
            line_width=self.line_width)

        self.id_release = tbox.layer.connect("button-release-event",
                                             self.button_released)
        self.id_motion = tbox.layer.connect("motion-notify-event",
                                            self.button_moved)

    def set_x_y(self, x, y):
        self.quadratic.set_property('x', x)
        self.quadratic.set_property('y', y)

    def get_x_y(self):
        return (self.quadratic.get_property('x'),
                self.quadratic.get_property('y'))

    def set_w_h(self, w, h):
        x, y = self.get_x_y()

        if w < 0:
            x += w
            w = -w
        if h < 0:
            y += h
            h = -h

        self.set_x_y(x, y)
        self.quadratic.set_property('width', w)
        self.quadratic.set_property('height', h)

    def button_released(self, src, tgt, event):
        w = event.x - self.origin[0]
        h = event.y - self.origin[1]
        self.set_w_h(w, h)

        self.tbox.layer.disconnect(self.id_release)
        self.tbox.layer.disconnect(self.id_motion)

        self.marker2 = Marker(self.tbox.layer, event.x, event.y,
                              color="Yellow",
                              callback=self.resize)

    def moveto(self, x, y):
        self.set_x_y(x, y)
        w = self.quadratic.get_property('width')
        h = self.quadratic.get_property('height')
        self.marker2.moveto(x + w, y + h)

    def resize(self, xnew, ynew):
        x, y = self.get_x_y()
        self.set_w_h(xnew - x, ynew - y)

    def button_moved(self, src, tgt, event):
        w = event.x - self.origin[0]
        h = event.y - self.origin[1]
        self.set_w_h(w, h)


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
            ("ellipse.svg",   "Ellipse",             None),
            ("line.svg",      "Líneas",              None),
            ("qbezier.svg",   "Bézier Cuadratico",   Qbezier),
            ("cbezier.svg",   "Bézier Cúbico",       None),
                ("text.svg",      "Texto",               None)):
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

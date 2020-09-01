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
        self.width = w
        self.height = h
        x, y = self.origin[0], self.origin[1]

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


class Ellipse(Figure):
    def __init__(self, tbox, x, y):
        super(Ellipse, self).__init__(tbox)
        self.origin = x, y
        self.marker1 = Marker(self.tbox.layer, x, y, color="Red",
                              callback=self.moveto)

        self.ellipse = GooCanvas.CanvasEllipse(
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
        self.ellipse.set_property('x', x)
        self.ellipse.set_property('y', y)

    def get_x_y(self):
        return (self.ellipse.get_property('x'),
                self.ellipse.get_property('y'))

    def set_w_h(self, w, h):
        self.width = w
        self.height = h
        x, y = self.origin[0], self.origin[1]

        if w < 0:
            x += w
            w = -w
        if h < 0:
            y += h
            h = -h

        self.set_x_y(x, y)
        self.ellipse.set_property('width', w)
        self.ellipse.set_property('height', h)

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
        w = self.ellipse.get_property('width')
        h = self.ellipse.get_property('height')
        self.marker2.moveto(x + w, y + h)

    def resize(self, xnew, ynew):
        x, y = self.origin[0], self.origin[1]
        self.set_w_h(xnew - x, ynew - y)
        print("Equis", xnew, "la i", ynew)

    def button_moved(self, src, tgt, event):
        w = event.x - self.origin[0]
        h = event.y - self.origin[1]
        self.set_w_h(w, h)

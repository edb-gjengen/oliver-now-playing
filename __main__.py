#!/usr/bin/env python
from SpotifyHTTPRequestHandler import SpotifyHTTPRequestHandler

import BaseHTTPServer
import dbus
import json
import shutil
import subprocess
import sys

HandlerClass = SpotifyHTTPRequestHandler
ServerClass = BaseHTTPServer.HTTPServer
Protocol = "HTTP/1.0"
port = 8000
server_address = ("127.0.0.1", port)

player, bridge = (None, None)
def __dbus_init():
    global player, bridge
    if player is not None or bridge is not None:
        return

    bus = dbus.SessionBus()
    spotify = bus.get_object('com.spotify.qt', '/')
    player = dbus.Interface(spotify, 'org.freedesktop.MediaPlayer2')
    bridge = dbus.Interface(spotify, 'org.freedesktop.DBus.Properties')

def __dbus_get_property(property_name):
    if not player or not bridge:
        raise Exception("DBus not initialized! Call '__dbus_init' first.")

    valid_properties = (
            'PlaybackStatus', 'LoopStatus',
            'Rate',           'Shuffle',
            'Metadata',       'Identity',
            'Position',       'MinimumRate',
            'MaximumRate',    'CanGoNext',
            'CanGoPrevious',  'CanPlay',
            'CanPause',       'CanSeek',
            'CanControl',     'CanQuit',
            'CanRaise',       'SupportedUriSchemes',
            'DesktopEntry',   'SupportedMimeTypes',
            'HasTrackList', )
    if property_name in valid_properties:
            return bridge.Get('org.freedesktop.MediaPlayer2', property_name)
    elif property_name == 'Volume':
            return player.Volume()
    else:
            raise Exception("'{}' is not a valid property name".format(property_name))
    return None

def __parse_node(node):
    t = type(node)

    if t == dbus.String:
        return str(node)

    elif t == dbus.Int32:
        return int(node)

    elif t == dbus.Int64:
        return int(node)

    elif t == dbus.Double:
        return float(node)

    elif t == dbus.Array:
        arr = []
        for item in node:
            arr.append(__parse_node(item))
        return arr

    elif t == dbus.Dictionary:
        dictionary = {}
        for k in node.keys():
            key = k.split(':')[-1]
            value = __parse_node(node[k])
            dictionary[key] = value
        return dictionary
    else:
        return str(node)
        

def __parse_dbus_response(response):
    return __parse_node(response)

def __serve(data_function):
    HandlerClass.data_function = data_function
    HandlerClass.protocol_version = Protocol
    httpd = ServerClass(server_address, HandlerClass)
    
    sa = httpd.socket.getsockname()
    httpd.serve_forever()

def __get_data(*args):
    __dbus_init()

    metadata_prop = __dbus_get_property('Metadata')
    metadata = __parse_dbus_response(metadata_prop)

    position_prop = __dbus_get_property('Position')
    position = __parse_dbus_response(position_prop)


    return json.dumps({ 'metadata' : metadata, 'position' : position })

def main():
    __serve(__get_data)

if __name__ == "__main__":
    main()

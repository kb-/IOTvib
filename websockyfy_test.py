# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 18:46:47 2019

@author: Olivier
"""

import os, sys, select, optparse, logging
sys.path.insert(0,os.path.join(os.path.dirname(__file__), ".."))
from websockify.websockifyserver import WebSockifyServer, WebSockifyRequestHandler

class WebSocketEcho(WebSockifyRequestHandler):
    """
    WebSockets server that echos back whatever is received from the
    client.  """
    buffer_size = 8096

    def new_websocket_client(self):
        """
        Echo back whatever is received.
        """

        cqueue = []
        c_pend = 0
        rlist = [self.request]

        while True:
            wlist = []

            if cqueue or c_pend: wlist.append(self.request)
            ins, outs, excepts = select.select(rlist, wlist, [], 1)
            if excepts: raise Exception("Socket exception")

            if self.request in outs:
                # Send queued target data to the client
                c_pend = self.send_frames(cqueue)
                cqueue = []

            if self.request in ins:
                # Receive client data, decode it, and send it back
                frames, closed = self.recv_frames()
                cqueue.extend(frames)

                if closed:
                    break
                
opts.web = "."
server = WebSockifyServer(WebSocketEcho, listen_port="6532", web = ".")
server.start_server()
# -*- coding: utf-8 -*-
"""
Vercel Edge WSGI Gateway Entrypoint
This file satisfies Vercel CLI's Python Runtime requirement
and serves the portal frontend (index.html).
"""
import os

def app(environ, start_response):
    status = '200 OK'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, 'index.html')
    
    if os.path.exists(html_path):
        with open(html_path, 'rb') as f:
            body = f.read()
    else:
        body = b"<!DOCTYPE html><html><body><h1>Peripheral Copilot Portal Ready</h1></body></html>"
    
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(body)))
    ]
    start_response(status, headers)
    return [body]

handler = app
application = app

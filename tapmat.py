#!/usr/bin/python3

from threading import Thread, Lock
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from testData import SinGeneratorThread
from scale import ScaleThread


JSON_SERVER_PORT = 8889

tapData = dict()
tapDataLock = Lock()


def parseRequest(request):
    rqs = request.split('?')
    sets = []
    if len(rqs) > 1:
        sts = rqs[1].split('&')
        for s in sts:
            try:
                sp = s.split('=')
                sets.append((sp[0].strip(), sp[1].strip()))
            except:
                pass
    adr = rqs[0].strip('/')
    return adr, sets

def navigateRequest(path, data):
    if path in ('/', ''):
        return data
    ps = path.split('/')
    try:
        ptr = data
        for p in ps:
            ptr = ptr[p]
        return ptr
    except:
        return data

def guessType(value):
    #try:
    #    return int(value)
    #except:
    #    pass
    #try:
    #    return float(value)
    #except:
    #    pass
    try:
        return json.loads(value)
    except:
        pass
    return value

def setValue(path, value, data):
    ptr = data
    ps = path.split('/')
    try:
        for p in ps[:-1]:
            ptr = ptr[p]
        ptr[ps[-1]] = guessType(value)
    except:
        return False
    return True


class JsonRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        request, sets = parseRequest(self.path)
        headers = self.headers
        print('Request: ', request)
        if len(sets):
            print('Sets:')
            for s in sets:
                print('  {}: {}'.format(s[0], s[1]))
        #print('Headers: ')
        #for key in headers:
        #    print('  {}: {}'.format(key, headers[key]))
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        with tapDataLock:
            change = False
            for s in sets:
                if setValue(s[0], s[1], tapData):
                    change = True
            data = navigateRequest(request, tapData)
            response = bytes(json.dumps(data), 'utf8')
            self.wfile.write(response)


if __name__ == "__main__":

    workers = []
    workers.append(SinGeneratorThread(tapData, tapDataLock))
    workers.append(ScaleThread(tapData, tapDataLock, 'keg1'))

    for w in workers:
        w.start()

    HOST, PORT = "localhost", JSON_SERVER_PORT
    server = HTTPServer((HOST, PORT), JsonRequestHandler)
    server.jsonData = tapData
    server.jsonDataLock = tapDataLock
    ip, port = server.server_address
    print("Json server IP: {}, PORT: {}".format(ip, port))

    try:
        server.serve_forever()
    except:
        pass

    server.server_close()

    for w in workers:
        w.stop()
    for w in workers:
        w.join()


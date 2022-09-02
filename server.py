#!/usr/bin/env python3

import shutil
from datetime import datetime
from importlib.metadata import version
import random
import string
import traceback
from pigeon import *
from description import *
from flask import Flask, request

def log(uid, lat, lng, c0, c1, c2, error=None):
    xml = ""
    for file in shutil.os.listdir("cache/"+uid):
        if file.endswith('.xml'):
            xml = "cache/%s/%s"%(uid,file)
            break
    libraries = ""
    for lib in ["osmnx","crossroads-segmentation","crossroads-description"]:
        libraries += "%s %s\n"%(lib, version(lib))
    logfile = "DATE : %s\nPOSITION : %s %s\nC0 C1 C2 : %s %s %s\nLIBRARIES : \n%s"%(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), lat, lng, c0, c1, c2, libraries)
    if error:
        logfile += "ERROR : \n%s"%error
    if xml:
        with open(xml, 'r') as f:
            content = f.read()
            logfile += "OSMXML CONTENT : \n%s"%content

    fname = ("error_%s%s.log" if error else "%s%s.log")%(''.join(random.choice(string.ascii_letters) for i in range(10)), datetime.now().timestamp())
    with open("log/"+fname, 'w') as f:
        f.write(logfile)


# clear folders
shutil.rmtree("cache", ignore_errors=True), shutil.os.mkdir("cache") , shutil.os.makedirs("log", exist_ok=True)

app = Flask(__name__)

@app.route("/")
def html():
    return app.send_static_file('index.html')

@app.route("/pigeon")
def send_pigeon():

    args = request.args
    selfdescription, lat, lng, c0, c1, c2, uid = args.get("self-description"), args.get("lat"), args.get("lng"), args.get("c0"), args.get("c1"), args.get("c2"), args.get("uid")

    pigeon = PigeonNelson("Crossroads Describer", "Décrire un carrefour proche de sa position", "UTF-8", 0)

    if lat and lng and uid:
        shutil.rmtree("cache/"+uid, ignore_errors=True), shutil.os.mkdir("cache/"+uid)
        error = None
        try:
            generateDescription(pigeon, uid, float(lat), float(lng), int(c0), int(c1), int(c2))
        except Exception as e:
            error = traceback.format_exc()
            pigeon.setMessage("Erreur lors de la génération de la description. Veuillez essayer un autre carrefour.", "fr", 1)
            pigeon.setGeoJson("{}")
        
        log(uid, lat, lng, c0, c1, c2, error)

    return pigeon.getJson()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(shutil.os.environ.get("PORT", 8080)))
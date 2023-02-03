#!/usr/bin/env python3
# ==== CONFIG VARIABLES ====

outputdir = "output"
outputfilebasename = "build"

# Continuously builds a latex document, refreshing it only when it has changed.

# What makes this different from latexmk, is that it just continually builds in
# the background, and refreshes to the latest copy _after each build_. This
# means you get to see the latest copy, even if there are 3 or 4 iterations
# left to go to make it perfect.

# However, it won't just constantly rebuild while there are no changes.

# It does _not_ attempt to do an error parser. rubber-info does that
# spectacularly. However, it will copy the log file, so that its not constantly
# changing, and only update it to the latest.

import subprocess
import shutil
import time
import os
import sys
import hashlib

def get_input_files(base):
    try:
        lines = open(os.path.join(outputdir, base + ".fls"), "r").readlines ()
    except Exception:
        # If the file doesnt exist, it'll be fixed later, when they see an empty list, and run it again.
        debug (".fls file missing")
        return []

    result = set()
    for line in lines:
        (before, _, after) = line.rstrip().partition (" ")
        if before == "INPUT" and after[0] != "/":
            result.add (after)

    return result

def debug (message):
    print(time.strftime("%H:%M:%S") + " - " + message)

os.makedirs(outputdir, exist_ok=True)

filename = sys.argv[1]
base = os.path.splitext (os.path.basename (filename))[0]
final = os.path.join(outputdir, base + ".pdf")
logfile = base + ".log"
auxfile = base + ".aux"

latex = ["pdflatex",
         "-recorder", 
         "-interaction=nonstopmode", 
         "-output-directory", outputdir, 
         filename]

bibtex = ["bibtex", os.path.join(outputdir, base)]

timestamps = {}
md5s = {}

while (True):

    files = get_input_files (base)

    # No .fls file
    if len (files) == 0:
        files = [filename]


    # Keep checking the files until a timestamp changes
    build = False
    time_to_wait = 0.05
    while not build:

        time.sleep (time_to_wait)
        # increase time_to_wait each loop
        # if the user is idle, this saves marginal system resources
        time_to_wait += 0.001

        new_timestamps = []
        changed_files = []
        for f in files:

            # First check the timestamp
            try:
                t = os.path.getmtime(f)
            except Exception:
                debug ("Time stamp error, always build")
                build = True
            else:
                if t > timestamps.get (f, 0):
                    new_timestamps.append (f)
                    timestamps[f] = t

                    # Check if it has actually changed
                    m = hashlib.md5( open( f, "rb" ).read()).hexdigest()
                    if m != md5s.get (f, ""):
                        changed_files.append (f)
                        md5s[f] = m
                        build = True


        if len (changed_files):
            debug("Changed files: " + ", ".join (changed_files))
        elif len (new_timestamps):
            debug("Touched files: " + ", ".join (new_timestamps))


        # If the .pdf if missing, build it
        if not os.path.exists(final):
            debug("PDF missing")
            build = True



    # Now build it


    # We dont care about outputs or exit code
    debug("Beginning build")
    # running bibtex on every aux file
    for filename in os.listdir(outputdir):
        if ".aux" in filename:
            auxfile_basename = os.path.splitext(filename)[0]
            bibtex_target    = os.path.join(outputdir, auxfile_basename)
            subprocess.call (["bibtex", bibtex_target],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    p = subprocess.Popen (latex, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # This can hang. Don't wait longer than 20 seconds (when it takes longer,
    # its generally building something incredibly broken, possibly because it
    # saved just after an open brace was added, and it can't make sense of the
    # thing.
    start = time.time ()
    while True:
        retcode = p.poll()

        if retcode != None:
            break;

        # It might timeout
        finish = time.time ()
        if finish > start + 30:
            try:
                p.kill()
            except Exception:
                pass

            debug ("Timeout (" + str(finish - start) + ") running: " + " ".join (latex))
            break

        time.sleep (0.2)

    debug("Built");

    build_path = os.path.join(outputdir, f'{outputfilebasename}.pdf')

    if os.path.exists(final):
        debug ("copying pdf")

        # Delete before copying for okular
        if os.path.exists(build_path):
            os.remove (build_path)
        shutil.copy (final, build_path)

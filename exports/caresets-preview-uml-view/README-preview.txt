CareSets site - preview build (branch uml-view, 2026-09-30)

This is the static site, built with an empty base URL, so it must be served
from the root of a web server rather than opened from the file system
(the pages use absolute paths like /assets/...).

Quickest way, with Python installed:

    cd <the unzipped folder>
    python -m http.server 8000

then open  http://localhost:8000/  in a browser.

What to look at: Logical Data Models > Model Viewer, pick a model, and try
the three tabs under "Element Structure": Tree, UML and Concept.

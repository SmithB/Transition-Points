"""
This module was used simply for testing purposes for debugging generated kml files.
Prints out geometries in kml format that can put in a kml file to view on Google Earth.
Author: Pranesh Velmurugan praneshsvels@gmail.com
Date: 8/5/24
"""
from fastkml import kml
from pygeoif.geometry import LineString


def create_file(line_given):
    """
    Prints out LineString in kml format
    :param line_given: LineString object
    """
    k = kml.KML()
    ns = "{http://www.opengis.net/kml/2.2}"

    # Create a KML Document and add it to the KML root object
    d = kml.Document(ns=ns, id="docid", name="doc name", description="doc description")
    k.append(d)

    # Create a KML Folders
    f = kml.Folder(ns=ns, id="fid", name="f name", description="description")
    d.append(f)
    nf = kml.Folder(
         ns=ns, id="nested-fid", name="nested f name", description="nested description")
    f.append(nf)
    f2 = kml.Folder(ns=ns, id="id2", name="name2", description="description2")
    d.append(f2)

    line = LineString(line_given)
    p = kml.Placemark(
        ns=ns, id="id", name="name", description="description")
    p.geometry = line
    f2.append(p)
    print(k.to_string(prettyprint=True))


def create_file_multipolygon(multi_polygon):
    """
    Prints out Multi Polygon in kml format
    :param multi_polygon: MultiPolygon object
    """
    k = kml.KML()
    ns = "{http://www.opengis.net/kml/2.2}"

    # Create a KML Document and add it to the KML root object
    d = kml.Document(ns=ns, id="docid", name="doc name", description="doc description")
    k.append(d)

    # Create a KML Folder and add it to the Document
    f = kml.Folder(ns=ns, id="fid", name="f name", description="f description")
    d.append(f)

    # Create a KML Folder and nest it in the first Folder
    nf = kml.Folder(
        ns=ns, id="nested-fid", name="nested f name", description="nested f description")
    f.append(nf)
    # Create a second KML Folder within the Document
    f2 = kml.Folder(ns=ns, id="id2", name="name2", description="description2")
    d.append(f2)

    p = kml.Placemark(
        ns=ns, id="id", name="name", description="description")
    p.geometry = multi_polygon
    f2.append(p)
    print(k.to_string(prettyprint=True))


def create_file_multiline(multi_line_string):
    """
    Prints out MutliLineString in kml format
    :param multi_line_string: MultiLineString object
    """
    k = kml.KML()
    ns = "{http://www.opengis.net/kml/2.2}"

    # Create a KML Document and add it to the KML root object
    d = kml.Document(ns=ns, id="docid", name="doc name", description="doc description")
    k.append(d)

    # Create a KML Folders
    f = kml.Folder(ns=ns, id="fid", name="f name", description="description")
    d.append(f)

    nf = kml.Folder(
        ns=ns, id="nested-fid", name="nested f name", description="nested description")
    f.append(nf)
    f2 = kml.Folder(ns=ns, id="id2", name="name2", description="description2")
    d.append(f2)

    p = kml.Placemark(
        ns=ns, id="id", name="name", description="description")
    p.geometry = multi_line_string
    f2.append(p)
    print(k.to_string(prettyprint=True))

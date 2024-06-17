import Conversions
import KmlReader as Kr
from fastkml import kml
from pygeoif.geometry import Polygon, LineString, MultiPolygon
import Intersections

# Create the root KML object


def create_file(line_given):
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

    line = LineString(line_given)
    # print(polygon)
    p = kml.Placemark(
        ns=ns, id="id", name="name", description="description")
    p.geometry = line
    f2.append(p)
    print("FIND ME: ")
    print(k.to_string(prettyprint=True))


def create_file_multipolygon(multi_polygon):
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

    # line = LineString(line_given)
    # print(polygon)
    p = kml.Placemark(
        ns=ns, id="id", name="name", description="description")
    p.geometry = multi_polygon
    f2.append(p)
    print("FIND ME: ")
    print(k.to_string(prettyprint=True))

# Create a Placemark with a simple polygon geometry and add it to the
# second folder of the Document
# polygon = Polygon(Kr.parse_mask('/Users/pvelmuru/Desktop/snow_depth_mask.kml')[1])
# print(polygon)
# p = kml.Placemark(
#     ns=ns, id="id", name="name", description="description")
# p.geometry = polygon
# f2.append(p)
# print(k.to_string(prettyprint=True))
# coordinates = Kr.parse_mask('/Users/pvelmuru/Desktop/snow_depth_mask.kml')


# line = LineString(Intersections.test_get())
# # print(polygon)
# p = kml.Placemark(
#     ns=ns, id="id", name="name", description="description")
# p.geometry = line
# f2.append(p)
# print(k.to_string(prettyprint=True))

# line = LineString(Kr.get_coordinates_from_kml('/Users/pvelmuru/Desktop/IS2_RGT_0001_cycle12_23-Jun-2021.kml'))
# # print(polygon)
# p = kml.Placemark(
#     ns=ns, id="id", name="name", description="description")
# p.geometry = line
# f2.append(p)
# print(k.to_string(prettyprint=True))
#
# # Conversion Test -- Looks right
# cart_list = Conversions.gcs_list_to_cartesian(line.coords)
# gcs_list = Conversions.cartesian_list_to_gcs(cart_list)
# print("OK: ", gcs_list)

import glob
from xml.dom import minidom
import os
import shutil
import cv2
import numpy as np

def xml2array(file):
    xmldoc = minidom.parse(file)
    itemlist = xmldoc.getElementsByTagName('object')
    bboxes = np.array([0.0, 0.0, 0.0, 0.0])
    for item in itemlist:
        # get bbox coordinates
        xmin = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmin')[0]).firstChild.data
        ymin = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymin')[0]).firstChild.data
        xmax = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmax')[0]).firstChild.data
        ymax = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymax')[0]).firstChild.data
        bboxes = np.vstack((bboxes, np.array([float(xmin), float(ymin), float(xmax), float(ymax)])))
    bboxes = bboxes[1:]
    return bboxes

def array2xml(file, bboxes):
    xmldoc = minidom.parse(file)
    itemlist = xmldoc.getElementsByTagName('object')
    i = 0
    for item in itemlist:
        # update bbox cordinates
        ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmin')[0]).firstChild.nodeValue = int(bboxes[i][0])
        ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymin')[0]).firstChild.nodeValue = int(bboxes[i][1])
        ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmax')[0]).firstChild.nodeValue = int(bboxes[i][2])
        ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymax')[0]).firstChild.nodeValue = int(bboxes[i][3])
        i += 1
    with open(file, 'w') as f:
        f.write(xmldoc.toxml())
        f.close()

def apply_aug(path, output, augment):
    # Reading Image file paths
    formats = ['jpg', 'JPG', 'jpeg', 'JPEG', 'png', 'PNG']
    image_file_list = []
    for format in formats:
        image_file_list.extend(glob.glob(f'{path}/*.{format}'))
    for file in image_file_list:
        name_ext = os.path.splitext(file)
        img = cv2.imread(file)
        xml_file = name_ext[0]+'.xml'
        bboxes = xml2array(xml_file)
        img, bboxes = augment(img, bboxes)
        cv2.imwrite(output+'/augmented_'+os.path.split(file)[1], img)
        output_xml_file = output+'/augmented_'+os.path.split(xml_file)[1]
        shutil.copyfile(xml_file, output_xml_file)
        array2xml(output_xml_file, bboxes)

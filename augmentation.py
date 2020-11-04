import glob
from xml.dom import minidom
import os
import shutil
import cv2
import numpy as np

def xml2array(file, lut):
    try:
       xmldoc = minidom.parse(file)
    except:
        return None
    itemlist = xmldoc.getElementsByTagName('object')
    bboxes = np.array([0.0, 0.0, 0.0, 0.0, -1.0])
    if len(itemlist):
        return None
    for item in itemlist:
        classid =  (item.getElementsByTagName('name')[0]).firstChild.data
        if classid in lut:
            label = float(lut[classid])
        else:
            label = -1.0
            print ("warning: label '%s' not in look-up table for file '%s'" % classid, file )
        # get bbox coordinates
        xmin = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmin')[0]).firstChild.data
        ymin = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymin')[0]).firstChild.data
        xmax = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmax')[0]).firstChild.data
        ymax = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymax')[0]).firstChild.data
        bboxes = np.vstack((bboxes, np.array([float(xmin), float(ymin), float(xmax), float(ymax), label])))
    bboxes = bboxes[1:]
    return bboxes

def array2xml(file, bboxes, lut):
    xmldoc = minidom.parse(file)
    itemlist = xmldoc.getElementsByTagName('object')
    i = 0
    m = bboxes.shape[0]
    dic = dict([(value, key) for key, value in lut.items()]) 
    for item in itemlist:
        if i < m:
            # update class label
            (item.getElementsByTagName('name')[0]).firstChild.nodeValue = dic[int(bboxes[i][4])]
            # update bbox cordinates
            ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmin')[0]).firstChild.nodeValue = int(bboxes[i][0])
            ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymin')[0]).firstChild.nodeValue = int(bboxes[i][1])
            ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmax')[0]).firstChild.nodeValue = int(bboxes[i][2])
            ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymax')[0]).firstChild.nodeValue = int(bboxes[i][3])
            i += 1
        else:
            parent = item.parentNode
            parent.removeChild(item)
    with open(file, 'w') as f:
        f.write(xmldoc.toxml())
        f.close()

def apply_aug(image_list, output, augment, lut):
    for file in image_list:
        name_ext = os.path.splitext(file)
        xml_file = name_ext[0]+'.xml'
        bboxes = xml2array(xml_file, lut)
        if bboxes == None:
            continue
        img = cv2.imread(file)
        img, bboxes, name = augment(img, bboxes)
        output_xml_file = output+'/'+name+os.path.split(xml_file)[1]
        if len(bboxes):
            cv2.imwrite(output+'/'+name+os.path.split(file)[1], img)
            shutil.copyfile(xml_file, output_xml_file)
            array2xml(output_xml_file, bboxes, lut)

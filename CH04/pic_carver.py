#!/usr/bin/env python
'''mail sniffer'''

import re
import zlib
import cv2

from scapy.all import *
import os
import threading
import signal

import sys
import argparse

pictures_dir = '~/pic_carver/pictures'
faces_dir = '~/pic_carver/faces'

PAYLOAD_SPLITTER = '\r\n\r\n'
CONTENT_TYPE = 'Content-Type'
CONTENT_ENCODING = 'Content-Encoding'
IMAGE = 'image'
def getargs():
    '''parse the command line arguments'''
    # process the command line
    parser = argparse.ArgumentParser(description='BHP Pic Carver')
    parser.add_argument('pictures_dir', default=pictures_dir, help='Directory to store pictures')
    parser.add_argument('faces_dir', default=faces_dir,
                        help='Directory to store images containing faces')
    parser.add_argument('-f', '--pcap_file', default='./arper.pcap', help='pcap source file')

    result = parser.parse_args()
    #print result
    return result

def get_http_headers(http_payload):
    '''get_http_headers'''
    try:
        # split the headers off if it is HTTP traffic
        #print 'Getting raw headers...',
        headers_raw = http_payload[:http_payload.index(PAYLOAD_SPLITTER)+2]
        #print 'Done.'
        # break out the headers
        headers = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", headers_raw))
    except Exception as err:
        #print str(err)
        return None
    if CONTENT_TYPE not in headers:
        return None
    return headers
def extract_image(headers, http_payload):
    '''extract_image'''
    image = None
    image_type = None
    try:
        if IMAGE in headers[CONTENT_TYPE]:
            # grab the iimage type and image body
            image_type = headers[CONTENT_TYPE].split('/')[1]
            image = http_payload[http_payload.index(PAYLOAD_SPLITTER) + 4:]
            # if we detect copression, decompress the image
            try:
                if CONTENT_ENCODING in headers.keys():
                    if headers[CONTENT_ENCODING] == 'gzip':
                        image = zlib.decompress(image, 16+zlib.MAX_WBITS)
                    elif headers[CONTENT_ENCODING] == 'deflate':
                        image = zlib.decompress(image)
            except:
                pass
    except:
        return None, None
    return image, image_type
def face_detect(target_img, output_file_name, highlight_color=(127, 255, 0)):
    '''detect if target contains a face
    if so, save as output_file_name
    '''
    img = cv2.imread(target_img)
    cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
    rects = cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20, 20))

    if len(rects) == 0:
        return False

    rects[:, 2:] += rects[:, :2]

    # highlight the faces in the IMAGE

    for (x1, y1, x2, y2) in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), highlight_color, 2)

    cv2.imwrite(output_file_name, img)
    return True

def http_assembler(ns):
    '''http_assembler'''
    pictures_dir = ns.pictures_dir
    faces_dir = ns.faces_dir
    pcap_file = ns.pcap_file

    carved_images = 0
    faces_detected = 0

    a = rdpcap(pcap_file)
    #a.summary()
    sessions = a.sessions()
    for session in sessions:

        http_payload = ''
        
        for packet in sessions[session]:
            
            try:
                if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                    # reassemble the stream
                    print 'Reassembling...',
                    #print str(packet[TCP])
                    http_payload += str(packet[TCP].payload)
                    print 'Done.'
            except:
                pass
        headers = get_http_headers(http_payload)
        if headers is None:
            continue
        print 'Extracting image...',
        image, image_type = extract_image(headers, http_payload)
        print 'Done.'
        if image is not None and image_type is not None:
            # store the image
            file_name = '%s-pic_carver_%d.%s' % (pcap_file, carved_images, image_type)
            fd = open('%s/%s' % (pictures_dir, file_name), 'wb')
            fd.write(image)
            fd.close()

            carved_images += 1

            # now attempt face detection
            try:
                if face_detect('%s/%s' % (pictures_dir, file_name),
                               '%s/%s-%s' % (faces_dir, pcap_file, file_name)):
                    faces_detected += 1
            except:
                pass
    return carved_images, faces_detected

def main():
    '''main'''
    carved_images, faces_detected = http_assembler(getargs())
    print 'Extracted %d images' % carved_images
    print 'Extracted %d faces' % faces_detected


main()

#!/usr/bin/python
#
# Adapted from http://svn.debian.org/wsvn/libhid/trunk/swig/test_libhid.py
#
#
'''
https://web.archive.org/web/20120116134204/http://pastebin.com:80/rpMEjHN5
''' 

from hid import false
import sys
import time
 
# allow it to run right out of the build dir
from hid import true
import os
libsdir = os.getcwd() + '/.libs'
if os.path.isdir(libsdir) and os.path.isfile(libsdir + '/_hid.so'):
  sys.path.insert(0, libsdir)
 
from hid import *
 
 
packet_len = 64
 
# Packing a request. Please see HexWax documentation for the list of all commands
# Packets are 64 bytes long, most of the commands are 4 bytes long. So up to 18
# can be batched into a packet. For example command with bytes [0x94, 0x0, 0x0, 0x0]
# is getting firmware id
def pack_request(*arguments):
    packet = [0x0] * packet_len
    i = 0
    for arg in arguments:
        packet[i] = arg
        i += 1
    #packet[0:4] = [0x94, 0x0, 0x0, 0x0] #get firmware id
    return ''.join([chr(c) for c in packet])
 
# Logs error to the error output
def log_error(functionName, ret):
    sys.stderr.write(functionName + (" failed with return code %d\n" % ret))
 
# Logs result onto standard output. Result is 64 bytes as decimal numbers
# Response is 64 bytes long
def show_result(bytes):
    sys.stdout.write("Result:")
    sys.stdout.write(''.join(['%d ' % ord(abyte) for abyte in bytes]))
 
# Turns LED on the bord on or off depending on input parameter on. 0 is turning
# the led on 1 is turning it off. The command is 0x9F set port bit (set output
# pin value), port is 0x03 (port C), 0x06 is bit index (so this is 7th bit),
# and the last bit is 0 for clear, 1 for set
def set_led(on, hid):
    if on:
        param = 0x00
    else:
        param = 0x01
 
    raw = pack_request(0x9F, 0x03, 0x06, param) #set port bit - 0 to turn it on 1 to turn it off
 
    ret = hid_interrupt_write(hid, 1, raw, packet_len)
    if ret != HID_RET_SUCCESS:
        log_error("hid_set_output_report", ret)
 
    ret, bytes = hid_interrupt_read(hid, 0x81, packet_len, 100)
    if ret != HID_RET_SUCCESS:
        log_error("hid_get_input_report", ret)
 
    show_result(bytes)
 
 
 
def main():
    #initialising debuging
    hid_set_debug(HID_DEBUG_ALL)
    hid_set_debug_stream(sys.stderr)
    hid_set_usb_debug(0)
 
    #init hid
    ret = hid_init()
    if ret != HID_RET_SUCCESS:
        log_error("hid_init", ret)
 
    #find our device
    hid = hid_new_HIDInterface()
    matcher = HIDInterfaceMatcher()
    matcher.vendor_id = 0x0b40
    matcher.product_id = 0x0132
 
    #removed following lines if you're running this from command line
    #my netbeans didn't want to show standard output so I had to redirect it to
    #a file
    fsock = open('out.log', 'w')
    sys.stdout = fsock
    fsock2 = open('out.err', 'w')
    sys.stderr = fsock2
 
    #open our device
    ret = hid_force_open(hid, 0, matcher, 3)
    if ret != HID_RET_SUCCESS:
        log_error("hid_force_open", ret)
 
    #write details about the device like handle, location, manufacturer etc.
    ret = hid_write_identification(sys.stdout, hid)
    if ret != HID_RET_SUCCESS:
        log_error("hid_write_identification", ret)
 
    #prepare our own command - this is get firmware id, only the first byte is
    #significant
    raw = pack_request(0x94)
 
    #send the packet
    ret = hid_interrupt_write(hid, 1, raw, packet_len)
    if ret != HID_RET_SUCCESS:
        log_error("hid_set_output_report", ret)
 
    #then read the result
    ret, bytes = hid_interrupt_read(hid, 0x81, packet_len, 100)
    if ret != HID_RET_SUCCESS:
        log_error("hid_get_input_report", ret)
 
    show_result(bytes)
 
    #prepare another request
    #set register TRISC bit 6 - port C bit 6 to be output
    #mind though 0x9B command can be used to write any register, so check the
    #microcontroller's datasheet
    raw = pack_request(0x9B, 0x94, 0x06, 0x00)
 
    ret = hid_interrupt_write(hid, 1, raw, packet_len)
    if ret != HID_RET_SUCCESS:
        log_error("hid_set_output_report", ret)
 
    ret, bytes = hid_interrupt_read(hid, 0x81, packet_len, 100)
    if ret != HID_RET_SUCCESS:
        log_error("hid_get_input_report", ret)
 
    show_result(bytes)
 
 
    #once we have our bit set as output we can control it. Here, LED is turned
    #on and then turned off after a second and it's done 10 times
    for i in range(10):
        set_led(true, hid)
        time.sleep(1)
        set_led(false, hid)
        time.sleep(1)
   
    #close and cleanup when we're done
    ret = hid_close(hid)
    if ret != HID_RET_SUCCESS:
        log_error("hid_close", ret)
 
    hid_cleanup()
 
if __name__ == '__main__':
  main()

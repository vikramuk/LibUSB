#/usr/bin/python
#
import usb # 1.0 not 0.4
def getStringDescriptor(device, index):
    """
    """
    response = device.ctrl_transfer(usb.util.ENDPOINT_IN,
                                    usb.legacy.REQ_GET_DESCRIPTOR,
                                    (usb.util.DESC_TYPE_STRING << 8) | index,
                                    0, # language id
                                    255) # length

    # TODO: Refer to 'libusb_get_string_descriptor_ascii' for error handling
    return response[2:].tostring().decode('utf-16')

if __name__ == "__main__":
    for d in usb.core.find(find_all=True):
        print "0x%04x 0x%04x" % (d.idVendor, d.idProduct),

        # TODO: Work out why 'usbtool' from V-USB can read more strings
        #       than we can. Is it because they're using 0.4.2?

        try: 
            print getStringDescriptor(d, d.iProduct),
        except usb.core.USBError:
            pass

        try: 
            print "(%s)" % (getStringDescriptor(d, d.iManufacturer),),
        except usb.core.USBError:
            pass

        print

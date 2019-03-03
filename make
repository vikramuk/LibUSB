executable: Lsusb.cpp /path/to/library/include/libusb.h
    g++ -o executable Lsusb.cpp -L /path/to/library/object/ -lusb-1.0

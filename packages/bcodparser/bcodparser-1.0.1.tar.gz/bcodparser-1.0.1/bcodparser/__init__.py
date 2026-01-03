# Made by V / Lou du Poitou (c) 2025, http://loudupoitou.dns-dynamic.net
# LICENSE MIT (c) 2025, V / Lou du Poitou

# URL's
# GitHub : https://github.com/Lou-du-Poitou/bcodparser/
# PyPi : https://pypi.org/project/bcodparser/

# Bluetooth devices class
# View this at part [2.8]
# https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Assigned_Numbers/out/en/Assigned_Numbers.pdf

# The Class of Device is a bitfiled composed of four fields.
# - Fixed Value [0b00] (bits 0 to 1)
# - Minor Device Class (bits 2 to 7)
# - Major Device Class (bits 8 to 12)
# - Major Services Classes (bits 13 to 23)

# By convention, the codepoints of the classes below will be their value in the corresponding bitfield(s).
# For example: the key (3, 8): "1% to 17% usage" is composed of:
# - The value of the major class: 8
# - The value of the minor class: 1 << 3 = 8

# This program allows you to decode the Bluetooth Class of Device (CoD) field and interpret major, minor, and service classes.

# Unknown device class
UNKNOWN_DEVICE_CLASS = "Unknown"

# Major Device Class (bits 8 to 12)
MAJOR_DEVICE_CLASS = {
    0: "Miscellaneous",
    1: "Computer",
    2: "Phone",
    3: "LAN/Network Access Point",
    4: "Audio/Video",
    5: "Peripheral",
    6: "Imaging",
    7: "Wearable",
    8: "Toy",
    9: "Health",
    31: "Uncategorized"
}

# Minor Device Class (bits 2 to 7)
MINOR_DEVICE_CLASS = {
    # Computer Major Class
    (1, 0): "Uncategorized",
    (1, 1): "DesktopWorkstation",
    (1, 2): "Server-class Computer",
    (1, 3): "Laptop",
    (1, 4): "HandheldPC/PDA",
    (1, 5): "Palm-sizePC/PDA",
    (1, 6): "WearableComputer",
    (1, 7): "Tablet",
    
    # Phone Major Class 
    (2, 0): "Uncategorized",
    (2, 1): "Cellular",
    (2, 2): "Cordless",
    (2, 3): "Smartphone",
    (2, 4): "Wired Modem or Voice Gateway",
    (2, 5): "Common ISDN Access",
    
    # LAN/Network Access Point Major Class
    (3, 0): "Fully available",
    (3, 8): "1% to 17% utilized",
    (3, 16): "17% to 33% utilized",
    (3, 24): "33% to 50% utilized",
    (3, 32): "50% to 67% utilized",
    (3, 40): "67% to 83% utilized",
    (3, 48): "83% to 99% utilized",
    (3, 56): "No service available",
    
    # Audio/Video Major Class
    (4, 0): "Uncategorized",
    (4, 1): "Wearable Headset Device",
    (4, 2): "Hands-free Device",
    (4, 3): "Reserved for Future Use",
    (4, 4): "Microphone",
    (4, 5): "Loudspeaker",
    (4, 6): "Headphones",
    (4, 7): "Portable Audio",
    (4, 8): "Car Audio",
    (4, 9): "Set-top box",
    (4, 10): "HiFi Audio Device",
    (4, 11): "VCR",
    (4, 12): "Video Camera",
    (4, 13): "Camcorder",
    (4, 14): "Video Monitor",
    (4, 15): "Video Display and Loudspeaker",
    (4, 16): "Video Conferencing",
    (4, 17): "Reserved for Future Use",
    (4, 18): "Gaming/Toy",
    (4, 19): "Hearing Aid",
    (4, 20): "Glasses",
    
    # Peripheral Major Class
    (5, 0): "Uncategorized",
    
    # Input type
    (5, 16): "Keyboard",
    (5, 32): "Pointing Device",
    (5, 48): "Combo Keyboard/Pointing Device",
    
    # Peripheral type
    (5, 1): "Joystick",
    (5, 2): "Gamepad",
    (5, 3): "Remote Control",
    (5, 4): "Sensing Device",
    (5, 5): "Digitizer Tablet",
    (5, 6): "Card Reader",
    (5, 7): "Digital Pen",
    (5, 8): "Handheld Scanner",
    (5, 9): "Handheld Gestural Input Device",
    
    # Imaging Major Class
    (6, 4): "Display",
    (6, 8): "Camera",
    (6, 16): "Scanner",
    (6, 32): "Printer",
    
    # Wearable Major Class
    (7, 1): "Wristwatch",
    (7, 2): "Pager",
    (7, 3): "Jacket",
    (7, 4): "Helmet",
    (7, 5): "Glasses",
    (7, 6): "Pin",
    
    # Toy Major Class
    (8, 1): "Robot",
    (8, 2): "Vehicle",
    (8, 3): "Doll/Action Figure",
    (8, 4): "Controller",
    (8, 5): "Game",
    
    # Health Major Class
    (9, 0): "Undefined",
    (9, 1): "Blood Pressure Monitor",
    (9, 2): "Thermometer",
    (9, 3): "Weighing Scale",
    (9, 4): "Glucose Meter",
    (9, 5): "Pulse Oximeter",
    (9, 6): "Heart/Pulse Rate Monitor",
    (9, 7): "Health Data Display",
    (9, 8): "Step Counter",
    (9, 9): "Body Composition Analyser",
    (9, 10): "Peak Flow Monitor",
    (9, 11): "Medication Monitor",
    (9, 12): "Knee Prothesis",
    (9, 13): "Ankle Prothesis",
    (9, 14): "Generic Health Manager",
    (9, 15): "Personal Mobility Device"
}

# Major Service Classes (bits 13 to 23)
SERVICE_DEVICE_CLASS = {
    1: "Limited Discoverable Mode",
    2: "LE audio",
    4: "Reserved for Future Use",
    8: "Positioning",
    16: "Networking",
    32: "Rendering",
    64: "Capturing",
    128: "Object Transfert",
    256: "Audio",
    512: "Telephony",
    1024: "Information"
}

# Function to decode the Bluetooth CoD
def decode(device_class: int) -> dict:
    """
    Decode the bluetooth Class of Device (CoD) format.
    The Class of Device is a bitfiled composed of four fields.
    
    Returns (dict):
    - minorClass (list[str])
        Minor Device Class (bits 2 to 7)
    - majorClass (str)
        Major Device Class (bits 8 to 12)
    - serviceClass (list[str])
        Major Services Classes (bits 13 to 23)
        
    Note: Unknown minor/service classes are filtered out
    """
    
    # Check the type of device_class
    if not isinstance(device_class, int) or device_class < 0:
        raise ValueError("Invalid Parameter : [device_class] must be a positive integer")
    
    # We don't check the fixed value (bits 0 to 1), it's not necessary for this function
    
    # Decoding result (minor class, major class, services)
    result = {
        "minorClass": [],
        "majorClass": "",
        "serviceClass": []
    }
    
    # Get the major class field (bits 8 to 12)
    major = (device_class >> 8) & ((1 << 5) - 1)
    result["majorClass"] = MAJOR_DEVICE_CLASS.get(major, UNKNOWN_DEVICE_CLASS)
    
    # Get the minor class field (bits 2 to 7)
    minor = (device_class >> 2) & ((1 << 6) - 1)
    
    # Get the service class field (bits 13 to 23)
    service = device_class >> 13

    if major == 3: # LAN/Network
        load_factor = minor >> 3 # (bits 5 to 7 of device_class)
        minor_key = load_factor << 3 # By convention
        minor_class = MINOR_DEVICE_CLASS.get((major, minor_key))
        if minor_class:
            result["minorClass"].append(minor_class)
        
    elif major == 5: # Peripheral type
        input_type = minor >> 4 # (bits 6 to 7 of device_class)
        peripheral_type = minor & ((1 << 4) - 1) # (bits 2 to 5 of device_class)
        
        for minor_key in [input_type << 4, peripheral_type]:
            minor_class = MINOR_DEVICE_CLASS.get((major, minor_key))
            if minor_class:
                result["minorClass"].append(minor_class)
                        
    elif major == 6: # Imaging
        for i in range(2, 6): # Iterates from 2 because the bitset is in the range 4 to 7 of device_class
            if minor & (1 << i): # Check the bitset value at position i
                minor_key = 1 << i
                minor_class = MINOR_DEVICE_CLASS.get((major, minor_key))
                if minor_class:
                    result["minorClass"].append(minor_class)

    else: # Others
        minor_class = MINOR_DEVICE_CLASS.get((major, minor))
        if minor_class:
            result["minorClass"].append(minor_class)
    
    # Get the service classes
    for i in range(0, 11):
        if service & (1 << i): # Check the bitset value at position i
            service_key = 1 << i
            service_class = SERVICE_DEVICE_CLASS.get(service_key)
            if service_class:
                result["serviceClass"].append(service_class)
    
    return result

# Made by V / Lou du Poitou (c) 2025, http://loudupoitou.dns-dynamic.net
# LICENSE MIT (c) 2025, V / Lou du Poitou
# You can contact me at v.loudupoitou@gmail.com
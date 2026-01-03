# bcodparser
Allows you to decode the Bluetooth Class of Device (CoD) field and interpret major, minor, and service classes.

# ⚙️ Installation
```
pip install bcodparser
```

# 🖊️ Example
> *Here is an example of use with [pybluez](https://github.com/pybluez/pybluez)*

**Code**
```python
from bcodparser import decode
import bluetooth # pybluez

# Scan Bluetooth
print("Scanning bluetooth...")

nearby_devices = bluetooth.discover_devices(
    lookup_names=True,
    lookup_class=True
)

print(f"Found {len(nearby_devices)} devices\n")

# List the Bluetooth devices with informations
for address, name, classe in nearby_devices:
    decoded = decode(classe)
    
    print(f"Name: {name}")
    print(f"Adress: {address}")
    
    print("Major Device Class: ", decoded["majorClass"])
    print("Minor Device Class: ", ", ".join(decoded["minorClass"]))
    print("Service Device Classes: ", ", ".join(decoded["serviceClass"]))
    
    print("\n")
```

**Output**
```
Scanning bluetooth...
Found 3 devices

Name: My Headphone
Adress: 11:22:33:44:55:66
Major Device Class:  Audio/Video
Minor Device Class:  Wearable Headset Device
Service Device Classes:  Rendering, Audio


Name: My Phone
Adress: 77:88:99:AA:BB:CC
Major Device Class:  Phone
Minor Device Class:  Smartphone
Service Device Classes:  Networking, Capturing, Object Transfert, Telephony


Name: My Computer
Adress: DD:EE:FF:11:22:33
Major Device Class:  Computer
Minor Device Class:  Laptop
Service Device Classes:  Networking, Capturing, Audio
```

View PyPi : https://pypi.org/project/bcodparser/
View GitHub : https://github.com/Lou-du-Poitou/bcodparser/
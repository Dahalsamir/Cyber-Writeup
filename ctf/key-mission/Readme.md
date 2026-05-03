## KEY MISSION CTF Decoding Mixed Case USB Keystrokes from PCAP

**Introduction**

During a recent assessment, I came across USB keystroke data while analyzing a packet capture. Initially, I spent time exploring it in Wireshark but realized it wasn't required for that task. However, the curiosity remained, and I later encountered a CTF challenge where I had to extract a flag from USB traffic.

This write-up documents the process of analyzing USB HID data and reconstructing typed keystrokes from a .pcap file.

**Challenge Overview**
1) Input: USB packet capture (.pcap)
2) Goal: Extract the typed keystrokes and recover the flag
3) Tooling:
4) Wireshark
5) Python + Scapy

---

**Analyze PCAP in Wireshark**

1) Open the .pcap file in Wireshark.

2) Focus on USB keyboard traffic:
```
usb.transfer_type == 0x01
```
3) This isolates URB_INTERRUPT in packets, which contain keyboard input.
```
From the packet details:

Look at HID Data
Example:
0200000000000000
```
---

**Understand USB HID Format**

Each USB keyboard packet contains 8 bytes:
```
[modifier][reserved][key1][key2][key3][key4][key5][key6]
```
Byte Position	Meaning
```
1st byte	Modifier (Shift, Ctrl, etc.)
3rd byte	Key pressed (Usage ID)
```
Important Observations
- Modifier Key
```
0x02 → Left Shift
0x20 → Right Shift
```
- If Shift is pressed → uppercase / special character

- Keycode (Usage ID)
```
Example:
0x04 → a
0x1E → 1
```
- These are NOT ASCII values, they are HID keycodes
  
---

Solving Python Script

```python
#!/usr/bin/python3

from scapy.all import *

usb_code = {
4: ["a", "A"], 5: ["b", "B"], 6: ["c", "C"], 7: ["d", "D"],
8: ["e", "E"], 9: ["f", "F"], 10: ["g", "G"], 11: ["h", "H"],
12: ["i", "I"], 13: ["j", "J"], 14: ["k", "K"], 15: ["l", "L"],
16: ["m", "M"], 17: ["n", "N"], 18: ["o", "O"], 19: ["p", "P"],
20: ["q", "Q"], 21: ["r", "R"], 22: ["s", "S"], 23: ["t", "T"],
24: ["u", "U"], 25: ["v", "V"], 26: ["w", "W"], 27: ["x", "X"],
28: ["y", "Y"], 29: ["z", "Z"], 30: ["1", "!"], 31: ["2", "@"],
32: ["3", "#"], 33: ["4", "$"], 34: ["5", "%"], 35: ["6", "^"],
36: ["7", "&"], 37: ["8", "*"], 38: ["9", "("], 39: ["0", ")"],
40: ["\n"], 42: ["BACKSPACE","BACKSPACE"], 43: ["\t","\t"],
44: [" "," "], 45: ["-", "_"], 46: ["=", "+"], 47: ["[", "{"],
48: ["]", "}"], 49: ["\"", "|"], 51: [";", ":"], 52: ["'", "'"],
53: ["`", "~"], 54: [",", "<"], 55: [".", ">"], 56: ["/", "?"]
}

flag = ""

packets = rdpcap("./key_mission.pcap")

for packet in packets:
    if len(packet) == 72:
        layer1 = packet[0]
        shift = layer1.load[-8]

        if shift in [2, 32]:
            case = 1
        else:
            case = 0
        
        keypressed = layer1.load[-6]
        if keypressed == 0:
            continue

        char = usb_code[keypressed][case]

        if char == "BACKSPACE":
            flag = flag[:-1]
        else:
            flag += char

print(flag)
```
---

# Offical Documnet for understand HID keycodes https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf

**How the Script Works**
- load[-8] → modifier (Shift detection)
- load[-6] → key pressed
- Maps keycode → character
- Handles:
- Shift (uppercase)
- Backspace (removes last char)

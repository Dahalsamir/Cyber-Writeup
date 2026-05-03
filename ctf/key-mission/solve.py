#!/usr/bin/python3

from scapy.all import *

usb_code = {
4: ["a", "A"],
5: ["b", "B"],
6: ["c", "C"],
7: ["d", "D"],
8: ["e", "E"],
9: ["f", "F"],
10: ["g", "G"],
11: ["h", "H"],
12: ["i", "I"],
13: ["j", "J"],
14: ["k", "K"],
15: ["l", "L"],
16: ["m", "M"],
17: ["n", "N"],
18: ["o", "O"],
19: ["p", "P"],
20: ["q", "Q"],
21: ["r", "R"],
22: ["s", "S"],
23: ["t", "T"],
24: ["u", "U"],
25: ["v", "V"],
26: ["w", "W"],
27: ["x", "X"],
28: ["y", "Y"],
29: ["z", "Z"],
30: ["1", "!"],
31: ["2", "@"],
32: ["3", "#"],
33: ["4", "$"],
34: ["5", "%"],
35: ["6", "^"],
36: ["7", "&"],
37: ["8", "*"],
38: ["9", "("],
39: ["0", ")"],
40: ["\n"],
42: ["BACKSPACE","BACKSPACE"],#it is DELETE match iin python default keyword so remain it
43: ["\t","\t"],
44: [" "," "],
45: ["-", "_"],
46: ["=", "+"],
47: ["[", "{"],
48: ["]", "}"],
49: ["\"", "|"],
51: [";", ":"],
52: ["'", "'"],
53: ["`", "~"],
54: [",", "<"],
55: [".", ">"],
56: ["/", "?"]
}

falg = ""

packets = rdpcap("./key_mission.pcap")

for packet in packets:
    if len(packet) == 72:
        layer1 = packet[0]
        shift = layer1.load[-8]

        if shift in [2,32]: #hex 0x20 is equal to 32 
            case = 1 #uppper case
        else:
            case = 0  #lowercase 
        
        keypressed = layer1.load[-6]
        if keypressed==0:
            continue
        char = usb_code[keypressed][case]
        if char == "BACKSPACE":
            falg = falg[:-1]
        else:
            falg += char
print(falg)
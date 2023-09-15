import serial
import serial.tools.list_ports
import time
import string

ports = serial.tools.list_ports.comports()

selected_port = 0
for port, desc, hwid in sorted(ports):
    if "CH340" in desc:
        selected_port = port

if selected_port == 0:
    print("--- PORT LISTESI - BIR PORT SECINIZ ---")
    for port, desc, hwid in sorted(ports):
        print(f"Port: {port}")
        print(f"Description: {desc}")
        print(f"Hardware ID: {hwid}")
    port_digit = input("\nPORT NUMARASINI GİRİNİZ (COM):")
else:
    for port, desc, hwid in sorted(ports):
        print("Otomatik port bulundu: \n")
        if port == selected_port:
            print(f"Port: {port}")
            print(f"Description: {desc}")
            print(f"Hardware ID: {hwid}")

ser = serial.Serial(
    port=selected_port,
    baudrate=9600,
    timeout=1
)

def sendTX(message):
    try:
        # Open the serial port
        if not ser.is_open:
            ser.open()
            print(f"PORT {ser.portstr} AÇILDI.\n")

        ser.write(message.encode())

        print(f"    [TX] >>> {message}")
        
        # RX
        received_data = ser.readline().decode().strip()

        if received_data:
            print(f"<<< [RX]     {received_data}")

    except Exception as e:
        print(f"Error: {e}")
        ser.close()
       
    return received_data
    
XORvar = 1111

while(input("Devam etmek için enter, çıkmak için exit yazınız: ") != "exit"):
    sendTX("<C00000001:0000>")
    recieve1 = sendTX("<C00000001?>")
    sendTX("<C00000001:"+str(hex(int("0x"+recieve1.split(":")[1][:-1], 16) ^ XORvar)).upper()[2:]+">")
    first = "0400"
    first = sendTX(f"<C00000000:{first}>").split("R")[1][:4]
    slave = "01"
    sendTX(f"<C{first}0004:{slave}>")
    slave = sendTX(f"<C{first}{slave}04:{slave}>").split(":")[1][:2]
    #roleleri ac
    sendTX(f"<C{first}{slave}10:1112>")
    sendTX(f"<C{first}{slave}10:1110>")
    sendTX(f"<C{first}{slave}10:1109>")
    #role fonksiyonlar
    sendTX(f"<C{first}{slave}12:01>")
    sendTX(f"<C{first}{slave}12:02>")
    sendTX(f"<C{first}{slave}12:03>")
    #full test
    sendTX(f"<C{first}{slave}10:9999>")

# Close the serial port if it's open
if ser.is_open:
    ser.close()
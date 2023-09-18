import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import serial
import serial.tools.list_ports

root = tk.Tk()
root.title("Sensor tester")

def start_button_click ():
    start_loop("0400","01")
    
def stop_button_click ():
    stop_loop()

def port_button_click():
    port_set()
    root.after(300, stop_loop)
    
def refresh_ports():
    refresh_loop()

# Create a list to hold the led widgets
leds = []

# Create a frame for the led grid
circle_frame = tk.Frame(root)
circle_frame.grid(row=0, column=1, padx=10, pady=10)

# Create 16 leds with numbers at the bottom
for i in range(16):
    frame = tk.Frame(circle_frame, width=60, height=60, bg="gray")
    frame.grid(row=i // 4, column=i % 4, padx=5, pady=5)

    led = tk.Canvas(frame, width=80, height=60, bg="white", highlightthickness=0)
    led.pack(pady=0)

    text = tk.Label(frame, text=str(i + 1), font=("Arial", 16))
    text.pack()

    leds.append(led)

button_frame = tk.Frame(root)
button_frame.grid(row=0, column=2)
 
# TEST START BUTTON
test_button = tk.Button(button_frame, text="START TEST", command=start_button_click,  width=10, height=4, font=("Arial", 16))
test_button.grid(row=0, column=0, padx=10, pady=10)

# STOP BUTTON
stop_button = tk.Button(button_frame, text="STOP TEST", command=stop_button_click,  width=10, height=4, font=("Arial", 16))
stop_button.grid(row=1, column=0, padx=10, pady=10)

# PORT FRAME
port_frame = tk.Frame(root)
port_frame.grid(row=0, column=0, padx=10, pady=10)

# PORT TEXT BOX
port_output = tk.Label(port_frame, text="", width=60, height=30, relief=tk.SUNKEN, anchor="nw", justify="left")
port_output.grid(row=0, column=0, columnspan=2, padx=5, sticky="w")

# PORT INPUT BOX
port_input = ttk.Combobox(port_frame, state="readonly", width=40)
port_input.grid(row=1, column=0, padx=5, pady=20)

# PORT ENTER BUTTON
port_button = tk.Button(port_frame, text="ENTER PORT", command=port_button_click, width=20, height=1, justify="right")
port_button.grid(row=1, column=1, padx=20, pady=20)

# STATUS LABER
status_label = tk.Label(button_frame, text="TEST HAZIR")
status_label.grid(row=2, column=0, padx=10, pady=10)
    
#END GUI

def port_set():
    global ser
    ports = serial.tools.list_ports.comports()

    selected_port = 0
    port_output_message = ""
    if ports != None:
        for port, desc, hwid in sorted(ports):
            if port_input.get().split(" - ")[0] == port:
                selected_port = port
                print(selected_port)
                port_output_message += "Port Seçildi\n\n"
                port_output_message += f"Port: {port}\n"
                port_output_message += f"Description: {desc}\n"
                port_output_message += f"Hardware ID: {hwid}\n\n"
     
    ser = serial.Serial(
        port=selected_port,
        baudrate=9600,
        timeout=0.1
        )
    port_output.config(text=port_output_message)

def port_init():
    ports = serial.tools.list_ports.comports()

    selected_port = 0
    port_output_message = ""
    try:
        if ports != None:
            for port, desc, hwid in sorted(ports):
                if "CH340" in desc:
                    selected_port = port

            if selected_port == 0:
                port_output_message += "PORT LISTESI - BIR PORT SECINIZ "
                for port, desc, hwid in sorted(ports):
                    port_output_message += f"Port: {port}\n"
                    port_output_message += f"Description: {desc}\n"
                    port_output_message += f"Hardware ID: {hwid}\n"
                    refresh_ports()
            elif ports:
                for port, desc, hwid in sorted(ports):
                    port_output_message += f"Port bulundu: {port}\n"
                    if port == selected_port:
                        port_output_message += f"PORT OTOMATİK SEÇİLDİ {port}\n\n"
                        port_output_message += f"Port: {port}\n"
                        port_output_message += f"Description: {desc}\n"
                        port_output_message += f"Hardware ID: {hwid}\n\n"
            else:
                port_output_message += "PORT BULUNAMADI - HATA\n\n"

            global ser 
            ser = serial.Serial(
                port=selected_port,
                baudrate=9600,
                timeout=0.1
                )
        else:
            port_output_message += "PORT BULUNAMADI - HATA\n\n"
    except Exception as e:
        port_output_message = f"PORT BULUNAMADI - HATA \n {e}\n\n"
    port_output.config(text=port_output_message)

def sendTX(message):
    try:
        ser.write(message.encode())
        print(f"    [TX] >>> {message}")

        # RX
        received_data = ser.readline().decode().strip()

        if received_data:
            print(f"<<< [RX]     {received_data}")
            return received_data

    except Exception as e:
        print(f"Error: {e}")

port_init()
XORvar = 1111

loop_running = False

def start_loop(first, slave):
    global loop_running

    try:# Open the serial port
        if not ser.is_open:
            ser.open()
            print(f"PORT {ser.portstr} AÇILDI.\n")
    except Exception as e:
        print(f"Error: {e}")
        
    loop_running = True
    status_label.config(text="TEST BAŞLATILIYOR", foreground="orange")
    
    #unlock
    sendTX("<S00000001:0000>")
    #set test
    temp_key = sendTX("<S00000001?>")
    #enter key
    keyXOR = "<S00000001:"+str(hex(int("0x"+temp_key.split(":")[1][:-1], 16) ^ XORvar)).upper()[2:]+">"
    sendTX(keyXOR)
    #set first
    first = sendTX(f"<S00000000:{first}>").split("R")[1][:4]
    #set slave
    slave = sendTX(f"<S{first}{slave}04:{slave}>").split(":")[1][:2]
    root.after(100, run_loop)
    root.mainloop()

def stop_loop():
    global loop_running
    loop_running = False
    status_label.config(text="TEST DURDURULMUŞ", foreground="red")
    for i in range(0,16):
        leds[i].config(bg="white")
    if ser.is_open:
        try:
            ser.close()
        except:
            None

def run_loop():
    first = "0400"
    slave = "01"
    if loop_running:
        status_label.config(text="TEST ÇALIŞIYOR", foreground="green")
        #SENSOR
        sensorReturn = sendTX(f"<S{first}{slave}10?>")
        sensorData = sensorReturn.split(":")[1][:-1]
        for i in range(0,len(sensorData)):
            if sensorData[i] == "1":
                leds[i].config(bg="#30db00")
        for i in range(0,16):
            if i >= len(sensorData):
                leds[i].config(bg="gray")
        root.after(100, run_loop)
        root.mainloop()
        
def refresh_loop():
    port_input['values'] = ()
    ports = serial.tools.list_ports.comports()
    available_ports = []
    if ports != None:
        for port, desc, hwid in sorted(ports):
            available_ports.append(f"{port} - {desc}")
    port_input['values'] = available_ports
    root.after(1000, refresh_loop)

root.after(1000, refresh_loop)
root.after(300, stop_loop)
root.after(300, run_loop)
root.mainloop()

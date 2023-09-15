import tkinter as tk
from tkinter import scrolledtext
import serial
import serial.tools.list_ports

ser = serial.Serial()

def main():
    # Function for Button 1
    def button1_click():
        full_test("0400", "01")

    # Function for Button 2
    def button2_click():
        role_test("0400", "01")

    # Function for small button
    def small_button_click():
        port_init()
        text = input_text.get()

    # Create the main application window
    root = tk.Tk()
    root.title("CHANNEL MONITORING V1.1 TESTER")


    # Create a frame to hold the small button, text input, and small text
    input_frame = tk.Frame(root)
    input_frame.pack(side=tk.LEFT, padx=10)  # Place the frame on the left side with some padding

    # Create a small text box at the top
    port_output = tk.Label(input_frame, text="", width=60, height=30, relief=tk.SUNKEN, anchor="nw", justify="left")
    port_output.grid(row=0, column=0, columnspan=2, padx=5, sticky="w")

    # Create a text input box
    input_text = tk.Entry(input_frame, width=40, justify="left")
    input_text.grid(row=1, column=0, padx=5, pady=20)

    # Create a small button with a larger size
    small_button = tk.Button(input_frame, text="ENTER PORT", command=small_button_click, width=20, height=1, justify="right")
    small_button.grid(row=1, column=1, padx=20, pady=20)


    # Create a frame to hold Button 1 and Button 2
    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.RIGHT, padx=10)  # Place the frame on the right side with some padding

    # Create Button 1 with a larger size
    button1 = tk.Button(button_frame, text="FULL TEST", command=button1_click, width=10, height=4, font=("Arial", 16))
    button1.pack()

    # Create Button 2 with a larger size
    button2 = tk.Button(button_frame, text="ROLE TEST", command=button2_click, width=10, height=4, font=("Arial", 16))
    button2.pack()

    # Create a large, copyable text box
    output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=30)
    output_text.config(state=tk.DISABLED)
    output_text.pack()


    # END OF GUI

    def port_init():
        ports = serial.tools.list_ports.comports()

        selected_port = 0
        for port, desc, hwid in sorted(ports):
            if "CH340" in desc:
                selected_port = port

        port_output_message = ""
        
        if input_text.get():
            selected_port = input_text.get()

        if selected_port == 0:
            port_output_message += "PORT LISTESI - BIR PORT SECINIZ "
            for port, desc, hwid in sorted(ports):
                port_output_message += f"Port: {port}\n"
                port_output_message += f"Description: {desc}\n"
                port_output_message += f"Hardware ID: {hwid}\n"
                input_text.insert(0, port)
        elif ports:
            for port, desc, hwid in sorted(ports):
                port_output_message += "Otomatik port bulundu:\n\n"
                if port == selected_port:
                    port_output_message += f"Port: {port}\n"
                    port_output_message += f"Description: {desc}\n"
                    port_output_message += f"Hardware ID: {hwid}\n\n"
        else:
            port_output_message += "PORT BULUNAMADI - HATA\n\n"

        global ser 
        ser = serial.Serial(
            port=selected_port,
            baudrate=9600,
            timeout=0.2
            )
            
        port_output.config(text=port_output_message)
            
    port_init()
    XORvar = 1111
            
    def role_test(first, slave):
        try:# Open the serial port
            if not ser.is_open:
                ser.open()
                print(f"PORT {ser.portstr} AÇILDI.\n")
        except Exception as e:
            print(f"Error: {e}")
                
        text = f"RÖLE FONKSİYON TESTİ - PORT {ser.portstr}\n"
        #Röle aç
        text += "  [TX]  "+f"<C{first}{slave}10:1112>\n"
        text += "  [RX]  "+sendTX(f"<C{first}{slave}10:1112>")+"\n"
        #Röle aç
        text += "  [TX]  "+f"<C{first}{slave}10:1111>\n"
        text += "  [RX]  "+sendTX(f"<C{first}{slave}10:1111>")+"\n"
        #Röle aç
        text += "  [TX]  "+f"<C{first}{slave}10:1109>\n"
        text += "  [RX]  "+sendTX(f"<C{first}{slave}10:1109>")+"\n"
        #Röle fonksiyon kapat
        text += "  [TX]  "+f"<C{first}{slave}12:01>\n"
        text += "  [RX]  "+sendTX(f"<C{first}{slave}12:01>")+"\n"
        #Röle fonksiyon aç
        text += "  [TX]  "+f"<C{first}{slave}12:02>\n"
        text += "  [RX]  "+sendTX(f"<C{first}{slave}12:02>")+"\n"
        #Röle fonksiyon sil
        text += "  [TX]  "+f"<C{first}{slave}12:03>\n"
        text += "  [RX]  "+sendTX(f"<C{first}{slave}12:03>")+"\n"

        output_text.config(state=tk.NORMAL)
        output_text.insert(tk.END, text)
        output_text.config(state=tk.DISABLED)
        
        if ser.is_open:
            try:
                ser.close()
            except:
                None
    
    
    def full_test(first, slave):
        try:# Open the serial port
            if not ser.is_open:
                ser.open()
                print(f"PORT {ser.portstr} AÇILDI.\n")
        except Exception as e:
            print(f"Error: {e}")
                
        text = f"GENEL TEST - PORT {ser.portstr}\n"
        
        #unlock
        text += "  [TX]  <C00000001:0000>\n"
        text += "  [RX]  "+sendTX("<C00000001:0000>")+"\n"
        #set test
        text  += "  [TX]  <C00000001?>\n"
        temp_key = sendTX("<C00000001?>")
        text += f"  [RX]  {temp_key}\n"
        #enter key
        keyXOR = "<C00000001:"+str(hex(int("0x"+temp_key.split(":")[1][:-1], 16) ^ XORvar)).upper()[2:]+">"
        text  += f"  [TX]  {keyXOR}\n"
        sendTX(keyXOR)
        #set first
        text  += f"  [TX]  <C00000000:{first}>\n"
        first = sendTX(f"<C00000000:{first}>").split("R")[1][:4]
        #set slave
        text += f"  [TX]  <C{first}{slave}04:{slave}>\n"
        slave = sendTX(f"<C{first}{slave}04:{slave}>").split(":")[1][:2]
        #full role testi
        text += f"  [TX]  <C{first}{slave}10:9999>\n"
        sendTX(f"<C{first}{slave}10:9999>")
        
        output_text.config(state=tk.NORMAL)
        output_text.insert(tk.END, text)
        output_text.config(state=tk.DISABLED)

        if ser.is_open:
            try:
                ser.close()
            except:
                None
        
    
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
            
    
    if role_test_iteration != 0:
        role_test()
        
    root.mainloop()


role_test_iteration = 0
main()
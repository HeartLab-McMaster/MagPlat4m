import os
import time
from lakeshore import Teslameter

class TeslameterInterface:
    def __init__(self):
        try:
        # Connect to the Teslameter
            self.teslameter = Teslameter()
            self.teslameter.command('SENSE:MODE DC')
            serial_no = self.teslameter.query('PROBE:SNUMBER?')
            print(f"Connected to probe: {serial_no}")

            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, "new.csv")
        #Open the file & log
            self.file = open(file_path, 'w')
            #     self.teslameter.log_buffered_data_to_file(145, 100, file)  #duration (seconds), 10 ms timestep
            #     #CHANGE THE TIME ABOVE FOR DIFFERENT BOX SIZES
    
            # # Wait for Arduino to complete movement
            #     while True:
            #         if self.ser.in_waiting:
            #             line = self.ser.readline().decode().strip()
            #             print("Arduino:", line)
            #             if line == "Completed!" or line == "Scan Stopped!":
            #                 break
            #         time.sleep(0.1)
                    
            # plot_thread = threading.Thread(target=self.plot_field, args=(file_path,), daemon = True)
            # plot_thread.start()
            # self.plot_field(file_path)
        except Exception as e:
            print(f"Scan/logging error: {e}")
        
    def scan_to_file(self, x_pos, y_pos):
        xyz = self.teslameter.get_dc_field_xyz()
        print(len(xyz), xyz)
        self.file.write(f"{x_pos},{y_pos},{xyz[0]},{xyz[1]},{xyz[2]},{xyz[3]}\n")
        
    def __del__(self):
        self.close()

    def close(self):
        if self.file:
            self.file.close()
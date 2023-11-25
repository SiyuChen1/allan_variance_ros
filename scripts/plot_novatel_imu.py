import argparse
import matplotlib.pyplot as plt
import numpy as np


start_time = 3000
current_time = start_time
idx = 0

# https://docs.novatel.com/OEM7/Content/PDFs/OEM7_Commands_Logs_Manual.pdf
# table 278 on page 1199 for cpt7 imu
gyroscope_factor = 1 / 2 ** 33
accelerometer_factor = 1 / 2 ** 29

# https://docs.novatel.com/OEM7/Content/PDFs/OEM7_Commands_Logs_Manual.pdf
# on page 1201 and on page 1167
# for cpt 7 imu, 100 Hz
freq = 100

parser = argparse.ArgumentParser(description="Plot raw IMU data")
parser.add_argument("--input-raw-imu", type=str, default=None)

# Parse the arguments
args = parser.parse_args()

raw_imu_path = args.input_raw_imu
# Create a new bag file (replace 'test.bag' with your desired file)

imu_ts_array = []

with open(raw_imu_path, 'r') as file:
    for line in file:
        if line.strip():
            # This log is output in the IMU Body frame. on page 1167
            idx = idx + 1
            # Splitting the line by spaces and converting the parts to floats
            parts = line.split(';')
            data = parts[1].rstrip().split(',')
            if int(data[0]):
                current_time = current_time + 1 / freq
            else:
                current_time = float(data[1])
            imu_ts = []
            imu_ts.append(current_time)
            imu_ts.append(accelerometer_factor * float(data[3]) * freq)
            imu_ts.append(-accelerometer_factor * float(data[4]) * freq)
            imu_ts.append(accelerometer_factor * float(data[5]) * freq)
            imu_ts.append(gyroscope_factor * float(data[6]) * freq)
            imu_ts.append(-gyroscope_factor * float(data[7]) * freq)
            imu_ts.append(gyroscope_factor * float(data[8].split('*')[0]) * freq)

            imu_ts_array.append(imu_ts)

            if idx % 20000 == 0:
                print(f"{idx} raw imu data have been processed")

imu_ts_array_np = np.array(imu_ts_array)

# Extracting individual columns
time_stamps = imu_ts_array_np[:, 0]
acc_x = imu_ts_array_np[:, 1]
acc_y = imu_ts_array_np[:, 2]
acc_z = imu_ts_array_np[:, 3]
ang_vel_x = imu_ts_array_np[:, 4]
ang_vel_y = imu_ts_array_np[:, 5]
ang_vel_z = imu_ts_array_np[:, 6]

# Creating the figure
plt.figure(figsize=(15, 10))

# First Row: Acceleration Plots
plt.subplot(2, 3, 1)  # 2 rows, 3 columns, 1st subplot
plt.plot(time_stamps, acc_x, color='r')
plt.title('Acceleration in X')
plt.xlabel('Time (s)')
plt.ylabel('Acc X')

plt.subplot(2, 3, 2)  # 2 rows, 3 columns, 2nd subplot
plt.plot(time_stamps, acc_y, color='g')
plt.title('Acceleration in Y')
plt.xlabel('Time (s)')
plt.ylabel('Acc Y')

plt.subplot(2, 3, 3)  # 2 rows, 3 columns, 3rd subplot
plt.plot(time_stamps, acc_z, color='b')
plt.title('Acceleration in Z')
plt.xlabel('Time (s)')
plt.ylabel('Acc Z')

# Second Row: Angular Velocity Plot
plt.subplot(2, 1, 2)  # 2 rows, 1 column, 2nd subplot
plt.plot(time_stamps, ang_vel_x, label='Ang Vel X', color='r')
plt.plot(time_stamps, ang_vel_y, label='Ang Vel Y', color='g')
plt.plot(time_stamps, ang_vel_z, label='Ang Vel Z', color='b')
plt.title('IMU Angular Velocity Data')
plt.xlabel('Time (s)')
plt.ylabel('Angular Velocity')
plt.legend()

# Display the plots
plt.tight_layout()
plt.show()

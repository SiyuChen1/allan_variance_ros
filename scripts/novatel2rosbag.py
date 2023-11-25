import argparse
import rosbag
from sensor_msgs.msg import Imu


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


parser = argparse.ArgumentParser("Convert raw IMU log file into rosbag")

parser.add_argument("--input-raw-imu", type=str, default=None)
parser.add_argument("--output-bag", type=str, default=None)

args = parser.parse_args()

# raw_imu_path = '/home/siyuchen/imu_calibration/rawimu_2023-11-24_09-28-32.log'
raw_imu_path = args.input_raw_imu
# Create a new bag file (replace 'test.bag' with your desired file)
bag = rosbag.Bag(args.output_bag, 'w')

with open(raw_imu_path, 'r') as file:
    for line in file:
        if line.strip():
            # This log is output in the IMU Body frame. on page 1167
            idx = idx + 1
            # Splitting the line by spaces and converting the parts to floats
            parts = line.split(';')
            data = parts[1].rstrip().split(',')
            msg = Imu()
            if int(data[0]):
                current_time = current_time + 1 / freq
            else:
                current_time = float(data[1])
            msg.header.stamp.from_sec(float_secs=current_time)
            msg.header.seq = idx
            msg.linear_acceleration.z = accelerometer_factor * float(data[3]) * freq
            msg.linear_acceleration.y = -accelerometer_factor * float(data[4]) * freq
            msg.linear_acceleration.x = accelerometer_factor * float(data[5]) * freq
            msg.angular_velocity.z = gyroscope_factor * float(data[6]) * freq
            msg.angular_velocity.y = -gyroscope_factor * float(data[7]) * freq
            msg.angular_velocity.x = gyroscope_factor * float(data[8].split('*')[0]) * freq

            bag.write('/imu', msg)

            if idx % 20000 == 0:
                print(f"{idx} raw imu data have been processed")

bag.close()
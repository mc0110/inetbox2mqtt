#
# Copyright (c) 2022  Sönke Krebber
#
# For leveling of an RV-car a MPU6050 IMU is used to publish pitch and roll angles.
#
#
# version 0.2 
#
# change_log:
# 0.1 Initial release
# 0.2 cleand up some code

from imu import MPU6050
from Kalman import KalmanAngle
import time
import math

# Auto-discovery-function of home-assistant (HA)
HA_MODEL  = 'inetbox'
HA_SWV    = 'V02'
HA_STOPIC = 'service/spiritlevel/status/'
#HA_CTOPIC = 'service/spiritlevel/set/'

radToDeg = 57.2957786
RestrictPitch = True

class spirit_level:

    HA_SL_CONFIG = {
        "spirit_level_pitch":     ['homeassistant/sensor/spirit_level_pitch/config', '{"name": "spirit_level_pitch", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "None", "unit_of_measurement": "°", "state_topic": "' + HA_STOPIC + 'spirit_level_pitch"}'],
        "spirit_level_roll":      ['homeassistant/sensor/spirit_level_roll/config', '{"name": "spirit_level_roll", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "None", "unit_of_measurement": "°", "state_topic": "' + HA_STOPIC + 'spirit_level_roll"}'],
        #"spirit_level_set_speed": ['homeassistant/switch/spirit_level_set_speed/config', '{"name": "spirit_level_set_speed", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'spirit_level_set_speed"}'],
        }
    

    # build up status 
    def __init__(self, i2c):
        self.i2c = i2c
        self.imu = MPU6050(self.i2c)
        
        self.kalmanX = KalmanAngle()
        self.kalmanY = KalmanAngle()
        self.kalAngleX = 0
        self.kalAngleY = 0
        
        #Read Accelerometer raw value
        accX = self.imu.accel.x
        accY = self.imu.accel.y
        accZ = self.imu.accel.z

        if (RestrictPitch):
            roll = math.atan2(accY, accZ) * radToDeg
            if (math.sqrt((accY ** 2) + (accZ ** 2)) > 0):
                pitch = math.atan(-accX / math.sqrt((accY ** 2) + (accZ ** 2))) * radToDeg
            else:
                pitch = 0
        else:
            if (math.sqrt((accX ** 2) + (accZ ** 2)) > 0):
                roll = math.atan(accY / math.sqrt((accX ** 2) + (accZ ** 2))) * radToDeg
            else:
                roll = 0
            pitch = math.atan2(-accX, accZ) * radToDeg

        self.kalmanX.setAngle(roll)
        self.kalmanY.setAngle(pitch)

        self.timer = time.time()


    def loop(self):
        try:
            #Read Accelerometer raw value
            accX = self.imu.accel.x
            accY = self.imu.accel.y
            accZ = self.imu.accel.z

            #Read Gyroscope raw value
            gyroX = self.imu.gyro.x
            gyroY = self.imu.gyro.y
            gyroZ = self.imu.gyro.z

            dt = time.time() - self.timer
            self.timer = time.time()

            if (RestrictPitch):
                roll = math.atan2(accY,accZ) * radToDeg
                pitch = math.atan(-accX/math.sqrt((accY**2)+(accZ**2))) * radToDeg
            else:
                roll = math.atan(accY/math.sqrt((accX**2)+(accZ**2))) * radToDeg
                pitch = math.atan2(-accX,accZ) * radToDeg

            gyroXRate = gyroX/131
            gyroYRate = gyroY/131

            if (RestrictPitch):
                if((roll < -90 and self.kalAngleX >90) or (roll > 90 and self.kalAngleX < -90)):
                    self.kalmanX.setAngle(roll)
                else:
                    self.kalAngleX = self.kalmanX.getAngle(roll,gyroXRate,dt)                    
                if(abs(self.kalAngleY)>90 or True):
                    gyroYRate  = -gyroYRate
                    self.kalAngleY  = self.kalmanY.getAngle(pitch,gyroYRate,dt)
            else:

                if((pitch < -90 and self.kalAngleY >90) or (pitch > 90 and self.kalAngleY < -90)):
                    self.kalmanY.setAngle(pitch)
                else:
                    self.kalAngleY = self.kalmanY.getAngle(pitch,gyroYRate,dt)
                if(abs(kalAngleX)>90):
                    gyroXRate  = -gyroXRate
                    self.kalAngleX = self.kalmanX.getAngle(roll,gyroXRate,dt)

            #print("Angle X: " + str(self.kalAngleX)+"   " +"Angle Y: " + str(self.kalAngleY))

        except Exception as exc:
            print(exc)


    # get Angles
    def get_pitch(self):
        return self.kalAngleY
    
    def get_roll(self):
        return self.kalAngleX

    def get_angles(self):
        return {self.kalAngleX, self.kalAngleY}

    def get_all(self):
        return {"spirit_level_pitch": self.kalAngleY,
                "spirit_level_roll": self.kalAngleX }
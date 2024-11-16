import numpy as np
roi = np.zeros([4, 168, 192])
roi[0, 109:157, 0:48] = 1
np.save("../data/epixUHR_asic0_sensor_fullRoi.npy", roi)
roi = np.zeros([4, 168, 192])
roi[3, 112:160, 10:58] = 1
np.save("../data/epixUHR_asic3_sensor_fullRoi.npy", roi)
roi = np.zeros([4, 168, 192])
for r in range(109, 157):
    for c in range(48):
        if r%12 == 11 and c%6 == 0:
            roi[0, r, c] = 1
np.save("../data/epixUHR_asic0_sensor_pietroPixelRoi.npy", roi)
for r in range(111, 160):
    for c in range(10, 58):
        if r%12 == 11 and c%6 == 0:
            roi[3, r, c] = 1
np.save("../data/epixUHR_asic3_sensor_pietroPixelRoi.npy", roi)
roi = np.zeros([4, 168, 192])
roi[3, 58:107, 70:119] = 1
np.save("../data/epixUHR_asic3_offSensor_fullRoi.npy", roi)
roi = np.zeros([4, 168, 192])
roi[0, 11:59, 60:109] = 1
np.save("../data/epixUHR_asic0_offSensor_fullRoi.npy", roi)

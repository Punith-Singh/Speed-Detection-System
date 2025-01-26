import cv2
import math
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style

plt.rcParams.update({'font.size': 10})
limit = 150

file = open("E://SDS//TrafficRecord//SpeedRecord.txt", "w")
file.write("------------------------------\n")
file.write(" REPORT \n")
file.write("------------------------------\n")
file.write("ID | SPEED\n------------------------------\n")
file.close()

class EuclideanDistTracker:
    def __init__(self):
        self.center_points = {}
        self.id_count = 0
        self.s1 = np.zeros((1, 1000))
        self.s2 = np.zeros((1, 1000))
        self.s = np.zeros((1, 1000))
        self.f = np.zeros(1000)
        self.capf = np.zeros(1000)
        self.count = 0
        self.exceeded = 0
        self.ids_DATA = []
        self.spd_DATA = []

    def update(self, objects_rect):
        objects_bbs_ids = []
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])
                if dist < 70:
                    self.center_points[id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                    if 410 <= y <= 430:
                        self.s1[0, id] = time.time()
                    if 235 <= y <= 255:
                        self.s2[0, id] = time.time()
                        self.s[0, id] = self.s2[0, id] - self.s1[0, id]
                    if y < 235:
                        self.f[id] = 1
            if not same_object_detected:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.s[0, self.id_count] = 0
                self.s1[0, self.id_count] = 0
                self.s2[0, self.id_count] = 0
                self.id_count += 1

        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center
        self.center_points = new_center_points.copy()
        return objects_bbs_ids

    def getsp(self, id):
        if self.s[0, id] != 0:
            return int(200 / self.s[0, id])
        return 0

    def capture(self, img, x, y, h, w, sp, id):
        if self.capf[id] == 0:
            self.capf[id] = 1
            self.f[id] = 0
            crop_img = img[y - 5:y + h + 5, x - 5:x + w + 5]
            n = "_id_" + str(id) + "_speed_" + str(sp)
            file_path = 'E://SDS//TrafficRecord//' + n + '.jpg'
            cv2.imwrite(file_path, crop_img)
            self.count += 1
            fileTR = open("E://SDS//TrafficRecord//SpeedRecord.txt", "a")
            if sp > limit:
                fileEX = 'E://SDS//TrafficRecord//exceeded//' + n + '.jpg'
                cv2.imwrite(fileEX, crop_img)
                fileTR.write(str(id) + " \t " + str(sp) + " <-- exceeded\n")
                self.exceeded += 1
            else:
                fileTR.write(str(id) + " \t " + str(sp) + "\n")
            fileTR.close()
            self.ids_DATA.append(id)
            self.spd_DATA.append(sp)

    def dataset(self):
        return self.ids_DATA, self.spd_DATA

    def datavis(self, id_lst, spd_lst):
        x = id_lst
        y = spd_lst
        valx = [str(i) for i in x]
        plt.figure(figsize=(20, 5))
        style.use('dark_background')
        plt.axhline(y=limit, color='r', linestyle='-', linewidth=5)
        plt.bar(x, y, width=0.5, linewidth=3, edgecolor='yellow', color='blue', align='center')
        plt.xlabel('ID')
        plt.ylabel('SPEED')
        plt.xticks(x, valx)
        plt.legend(["speed limit"])
        plt.title('SPEED OF VEHICLES CROSSING ROAD\n')
        plt.savefig("E://SDS//TrafficRecord//datavis.png", bbox_inches='tight', pad_inches=1, edgecolo

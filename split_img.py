# coding:utf-8
import cv2
import numpy as np
import matplotlib.pyplot as plt

class SplitImg():
    def __init__(self):
        self.width = 0
        self.height = 0
        self.img_position = []
        self.img_matrix = []

    def dimension_reduction(self, img_path):
        '''
        对图片进行垂直和水平映射
        :param img_path: 图片存储路径
        :return:
        '''
        img = cv2.imread(img_path, 0)
        _, self.img_matrix = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
        horizontal_sum = np.sum(self.img_matrix, axis=1)

        # plt.plot(horizontal_sum,range(horizontal_sum.shape[0]))
        # plt.gca().invert_yaxis()
        # plt.show()

        bin = self.img_matrix.T
        vertical_sum = np.sum(bin, axis=1)
        # plt.plot(range(vertical_sum.shape[0]),vertical_sum)
        # plt.gca().invert_yaxis()
        # plt.show()
        self.height = horizontal_sum.shape[0]
        self.width = vertical_sum.shape[0]
        self.img_position = [[0, 0], [self.width, 0], [self.width, self.height], [0, self.height]]

    def extra_space(self, dirc, apex_position, img_matrix, width_space):
        if dirc == '-':
            mapping_sum = np.sum(img_matrix, axis=1)
        else:
            mapping_sum = np.sum(img_matrix.T, axis=1)
            # plt.plot(range(mapping_sum.shape[0]), mapping_sum)
            # plt.gca().invert_yaxis()
            # plt.show()
        mapping_size = mapping_sum.shape[0]
        mapping_space = []
        split_result = {}
        start_index = 0
        pre_num = mapping_sum[0]
        stat_num = 0
        for i in range(1, mapping_size):
            if pre_num+1000 > mapping_sum[i] > pre_num-1000:
                stat_num += 1
            else:
                if stat_num > self.width * width_space and start_index != 0:
                # if stat_num > self.width * 0.1 and start_index != 0:
                    mapping_space.append((start_index+i-1)//2)
                stat_num = 0
                start_index = i
                pre_num = mapping_sum[i]
        if dirc == '-':
            x0_y1 = apex_position[0]
            x1_y1 = apex_position[1]
            for i in range(len(mapping_space)):
                x0_y0 = x0_y1
                x1_y0 = x1_y1
                x1_y1 = [apex_position[1][0], apex_position[1][1]+mapping_space[i]]
                x0_y1 = [apex_position[0][0], apex_position[0][1]+mapping_space[i]]
                split_result[str(i+1)] = [x0_y0, x1_y0, x1_y1, x0_y1]
            split_result[str(i+2)] = [x0_y1, x1_y1, apex_position[2], apex_position[3]]
        else:
            x1_y0 = apex_position[0]
            x1_y1 = apex_position[3]
            for i in range(len(mapping_space)):
                x0_y0 = x1_y0
                x0_y1 = x1_y1
                x1_y0 = [apex_position[0][0]+mapping_space[i], apex_position[1][1]]
                x1_y1 = [apex_position[0][0]+mapping_space[i], apex_position[2][1]]
                split_result[str(i+1)] = [x0_y0, x1_y0, x1_y1, x0_y1]
            split_result[str(i+2)] = [x1_y0, apex_position[1], apex_position[2], x1_y1]
        # print(dirc)
        # print(mapping_space)
        # print(split_result)
        return split_result

    def split_img(self, width_space):
        dirc = '-'
        hori_blocks = self.extra_space(dirc, self.img_position, self.img_matrix, width_space)
        dirc = '|'
        split_result = {}
        for k, v in hori_blocks.items():
            current_matrix = np.asarray(self.img_matrix)[v[0][1]:v[2][1],v[0][0]:v[1][0]]
            vert_blocks = self.extra_space(dirc, v, current_matrix, width_space)
            for k1, v1 in vert_blocks.items():
                split_result['.'.join([k, k1])] = v1
        # print(split_result)
        return split_result

    def run(self, img_path, width_space=0.1):
        self.dimension_reduction(img_path)
        return self.split_img(width_space)

# coding:utf-8

import sys
import os
import re
import datetime
import base64
import requests
import shutil
import zipfile
import json
from tqdm import tqdm
from config import *
# from script.split_img import *
# from script.sentence_connect import *
from jsonpath import jsonpath
from pprint import pprint
from sentence_connect import *
from split_img import *


class Cimg2md2:
    def ocr_predict(self, img_path, model_type):
        """
        获取ocr识别图片文字的结果信息和位置信息

        :param img_path: 待识别图片储存路径
        :return: 图片文字信息，文字位置信息
        """
        with open(img_path, 'rb') as f:
            cnt = f.read()
            x = base64.b64encode(cnt)
            image_jpeg_base64 = x.decode('ascii').replace('\n', '')
        data = {}
        data['image'] = image_jpeg_base64
        data['scene'] = model_type
        data['edge_size'] = 0
        data['do_recognition'] = 'True'
        data['row_range_flag'] = 'True'
        data['vis_flag'] = 'False'

        rst = requests.post(PREDICT_URL, data=data).json()
        return rst

    def table_predict(self, image_path, scene):
        """
        获取ocr识别图片中表格的相关信息

        :param image_path: 待识别图片储存路径
        :param scene: 固定值"table_print"
        :return: 图片中表格的文字信息，位置信息
        """
        with open(image_path, 'rb') as f:
            cnt = f.read()
            x = base64.b64encode(cnt)
            image_jpeg_base64 = x.decode('ascii').replace('\n', '')
        data = {}
        data['image'] = image_jpeg_base64
        data['scene'] = scene
        res = requests.post(OCR_TABLE_URL, data=data).json()
        return res

    def table2txt_pro(self, table, predict):
        """
        根据ocr识别的图片表格信息，将表格保存成md格式

        :param table: ocr返回的全部表格信息
        :return: 表格md格式
        """
        element_infos = table['data']['json']['raw_result']
        # pprint(element_infos)
        element_infos = sorted(element_infos, key=lambda x: x['cell_infos'][0]['box'][0][1])
        result = {'position': []}
        i = 1
        for element_info in element_infos:
            bboxes = predict['data']['json']['general_ocr_res']['bboxes'][0]['position']  ##bboxes 每一行的position
            texts = predict['data']['json']['general_ocr_res']['texts'][0]  ##所有文本信息
            excel_column_info = predict['data']['json']['general_ocr_res']['bboxes'][0]['excel_column_info']  # 列信息
            excel_row_info = predict['data']['json']['general_ocr_res']['bboxes'][0]['excel_row_info']  # 列信息

            rows = element_info['rows']
            cols = element_info['cols']
            if rows == 1 and cols == 1:
                raise ValueError
            tabel_col_0 = []  # 取出某一列信息
            for boxs in element_info['cell_infos']:
                for num in range(rows):
                    if boxs['col'] == 0 and boxs['row'] == num:
                        tabel_col_0.append(boxs)

            y_length = [(boxs['box'][1][1], boxs['box'][2][1]) for boxs in tabel_col_0]  # 获取每一行的y轴区间
            # print(y_length)

            new_cols = 0
            for idx, va in enumerate(bboxes):
                if y_length[0][0] <= va[0][1] and va[1][1] <= y_length[0][1]:  # 获取新的table的列数
                    for item in excel_column_info.items():
                        if idx in item[1] and new_cols <= int(item[0]):
                            new_cols = int(item[0])

            text_cell = [[[] for y in range(new_cols + 1)] for x in range(rows)]

            for col_indx, collength in enumerate(y_length):  # 填充信息
                for idx, va in enumerate(bboxes):
                    row = -1
                    col = -1
                    if collength[0] <= va[0][1] and va[1][1] <= collength[1]:  # 判断在一个y轴区间内的行信息
                        row = col_indx
                        col = [int(clo_item[0]) for clo_item in excel_column_info.items() if idx in clo_item[1]][0]
                    if row >= 0 and col >= 0:
                        if len(text_cell[row][col]) == 0:
                            text_cell[row][col].append({'text': [texts[idx]], 'position': [va]})  # 按行按列进行填充信息
                            result['position'].append(va)
                        else:
                            text_cell[row][col][0]['text'].append(texts[idx])
                            text_cell[row][col][0]['position'].append(va)
                            result['position'].append(va)

            table_text = ''
            for j in range(rows):
                tmp = []
                for k in range(new_cols + 1):
                    try:
                        if len(''.join(text_cell[j][k][0]['text']).strip()) != 0:
                            cell = {}
                            for num in range(len(text_cell[j][k][0]['text'])):
                                x_y = text_cell[j][k][0]['position'][num][0][1]
                                cell[x_y] = text_cell[j][k][0]['text'][num]
                            cell = sorted(cell.items(), key=lambda x: x[0])
                            tmp.append('  '.join(cell[1] for cell in cell))
                        else:
                            tmp.append('  ')
                    except:
                        tmp.append(' ')
                table_text += '|' + '|'.join(tmp) + '|\n'
                if j == 0:
                    table_text += '|' + '|'.join(['----' for i in range(new_cols + 1)]) + '|\n'
            for col in range(new_cols + 1):
                if len(text_cell[0][col]) != 0 and len(text_cell[0][col][0]['position']) != 0:
                    result['t{}'.format(i)] = {'start': text_cell[0][col][0]['position'][0],
                                               'text': '\n' + table_text + '\n'}
                    i += 1
                    break

        return result

    def table2txt(self, table):
        """
        根据ocr识别的图片表格信息，将文字保存成md格式

        :param table: ocr返回的全部表格信息
        :return: 表格md格式
        """
        element_infos = table['data']['json']['raw_result']
        element_infos = sorted(element_infos, key=lambda x: x['cell_infos'][0]['box'][0][1])
        result = {'position': []}
        i = 1
        for element_info in element_infos:
            cols = element_info['cols']
            rows = element_info['rows']
            text_cell = [['' for j in range(cols)] for i in range(rows)]
            cell_infos = element_info['cell_infos']
            for cell_info in cell_infos:
                text_cell[cell_info['row']][cell_info['col']] = {'text': cell_info['text'],
                                                                 'position': cell_info['text_box']}
                result['position'] += cell_info['text_box']
            table_text = ''
            # pprint(text_cell)
            for j in range(rows):
                tmp = []
                for k in range(cols):
                    try:
                        if len(''.join(text_cell[j][k]['text']).strip()) != 0:
                            # cell = {}
                            # for num in range(len(text_cell[j][k]['text'])):
                            #     x_y = text_cell[j][k]['position'][num][0][1]
                            #     cell[x_y] = text_cell[j][k]['text'][num]
                            # cell = sorted(cell.items(), key=lambda x: x[0])
                            # tmp.append(''.join(cell[1] for cell in cell))
                            cell = {}
                            cell_sorted = {}
                            for num in range(len(text_cell[j][k]['text'])):
                                x_y = text_cell[j][k]['position'][num][0][1]
                                cell[x_y] = [[text_cell[j][k]['text'][num], text_cell[j][k]['position'][num]]]
                            cell = list(sorted(cell.items(), key=lambda x: [x[0], x[1][0][1][0][0]]))
                            for c in range(len(cell)):
                                cell_sorted[c] = cell[c][1]
                            cell = {'1.1': cell_sorted}
                            # pprint(cell)
                            text_list = SentenceConnect().processBlocksEasyMode(cell)
                            text_list = [text[0] for text in text_list if len(text) > 0]
                            # pprint(text_list)
                            tmp.append('\t'.join(text_list))
                        else:
                            tmp.append('  ')
                    except:
                        tmp.append(' ')
                table_text += '|' + '|'.join(tmp) + '|\n'
                if j == 0:
                    table_text += '|' + '|'.join(['----' for i in range(cols)]) + '|\n'
            for col in range(cols):
                if len(text_cell[0][col]['position']) != 0:
                    result['t{}'.format(i)] = {'start': text_cell[0][col]['position'][0],
                                               'text': '\n' + table_text + '\n'}
                    i += 1
                    break

        return result

    def text_block(self, predict, split_img):
        text_blocks = {b: {} for b in split_img.keys()}
        pprint(predict)
        row_info = jsonpath(predict, '$..excel_row_info')[0]
        position = jsonpath(predict, '$..position')[0]
        text_info = jsonpath(predict, '$..texts')[0][0]
        for line in range(len(row_info)):
            for line_index in row_info[str(line)]:
                text_00 = position[line_index][0]
                text_11 = position[line_index][2]
                line_info = [text_info[line_index], position[line_index]]
                for b, block in split_img.items():
                    block_00 = block[0]
                    block_11 = block[2]
                    if text_00[0] >= block_00[0] and \
                            text_00[1] >= block_00[1] and \
                            text_00[0] <= block_11[0] and \
                            text_00[1] <= block_11[1]:

                        if line not in text_blocks[b]:
                            text_blocks[b][line] = [line_info]
                        else:
                            text_blocks[b][line].append(line_info)

        return text_blocks

    def block2txt(self, text_blocks):
        txt = ''
        for block in text_blocks.values():
            for line in block.values():
                tmp = '\t'.join([t[0] for t in line])
                if len(tmp.strip()) == 0:
                    continue
                txt += tmp + '\n'
            txt += '\n'
        return txt

    def extract_table(self, table_info, text_block):
        table_position = table_info.pop('position')
        table_start = [v['start'] for v in table_info.values()]
        table_start = list(sorted(table_start, key=lambda x: x[0][1]))
        result_text_block = {}
        for k, v in text_block.items():
            result_text_block[k] = {}
            for block, block_v in v.items():
                for b in block_v:
                    if b[1] not in table_position:
                        if block not in result_text_block[k]:
                            result_text_block[k][block] = []
                        result_text_block[k][block].append(b)
                    if b[1] in table_start:
                        index = table_start.index(b[1])
                        result_text_block[k][block] = [
                            [table_info['t{}'.format(index + 1)]['text'], table_info['t{}'.format(index + 1)]['start']]]

        return result_text_block

    def single2txt(self, img_path):
        """
        单个图片转txt，为image2txt函数提供支持。

        """
        # table = self.table_predict(img_path, 'table_print')
        # table_info = self.table2txt(table) if table['data'] != None else {'position':[]}
        split_img = SplitImg().run(img_path)
        predict = self.ocr_predict(img_path)
        text_block = self.text_block(predict, split_img)
        text_list = SentenceConnect().processBlocks(text_block)
        text_list = [text[0] if len(text) > 0 else '' for text in text_list]
        return '\n'.join(text_list)

    def single2txtEasyMode(self, img_path, width_space, model_type):
        """
        单个图片转txt，为image2txt函数提供支持。

        """
        predict = self.ocr_predict(img_path, model_type)
        table = self.table_predict(img_path, 'table_print')
        # if table['data'] != None:
        #     try:
        #         table_info = self.table2txt_pro(table, predict)
        #     except:
        #         table_info = self.table2txt(table)
        # else:
        table_info = {'position': []}
        split_img = SplitImg().run(img_path, width_space)
        text_block = self.text_block(predict, split_img)
        text_block = self.extract_table(table_info, text_block)
        # pprint(text_block)
        # TODO

        text_list = SentenceConnect().processBlocksEasyMode(text_block)
        text_list = [text[0] if len(text) > 0 else '' for text in text_list]
        return '\n'.join(text_list)

    def img2txt(self, img_zip_path):
        """
        全部图片转txt，并拼接存放在同一个txt中。

        """
        img_name = img_zip_path.replace(UPLOAD_IMG2MD_PATH, '')
        img_folder_path = img_zip_path.replace('.zip', '')
        txt_name = img_name.replace('.zip', '.txt')
        txt_path = RESULT_IMG2MD_TEMP_PATH + txt_name
        zip_file = zipfile.ZipFile(img_zip_path, 'r')
        zip_file.extractall(img_folder_path)

        output = []
        if os.path.isdir(os.path.join(img_folder_path, '__MACOSX')):
            shutil.rmtree(os.path.join(img_folder_path, '__MACOSX'))

        for root, dirs, files in os.walk(img_folder_path):
            for file in files:
                if file == '.DS_Store':
                    continue
                image_path = os.path.join(root, file)
                output.append(self.single2txt(image_path))

        txt = '\n\n'.join(output)
        with open(txt_path, 'w', encoding='utf8') as f:
            f.write(txt)
        return txt_path

    def txt2md(self, txt_path, temp_path=RESULT_IMG2MD_TEMP_PATH, result_path=RESULT_IMG2MD_PATH):
        """
        txt文件转md，规则实现断行拼接。
        此处没有使用断行拼接api，因为效果不好。

        """
        txt_name = txt_path.replace(temp_path, '')
        output_name = txt_name.replace('.txt', '.md')
        output_path = result_path + output_name

        line_length_dict = {}
        output_list = []
        temp_path = ''.join(txt_path.replace(txt_path, output_path).split('.txt')) + '_temp.txt'
        shutil.copy(txt_path, output_path)
        return output_name

    def img2md_multi(self, img_path):
        """
        处理多张图片的情况

        :param img_path: 多张图片压缩后的zip文件
        :return: 多张图片按顺序拼接后的txt
        """
        txt_path = self.img2txt(img_path)
        return self.txt2md(txt_path)

    def img2md_single(self, img_path):
        """
        处理单张图片的情况

        :param img_path: 待识别图片储存的路径
        :return: 识别后的txt文件
        """
        img_name = img_path.replace(UPLOAD_IMG2MD_PATH, '')
        txt_name = ''.join(img_name.split('.')[:-1]) + '.txt'
        txt_path = RESULT_IMG2MD_TEMP_PATH + txt_name
        txt = self.single2txt(img_path)
        with open(txt_path, 'w', encoding='utf8') as f:
            f.write(txt)
        return self.txt2md(txt_path)

    def img2md_single_easymode(self, img_path, txt_path):
        """
        处理单张图片的情况
        :param img_path: 待识别图片储存的路径
        :return: 识别后的txt文件
        """
        # img_name = img_path.replace(UPLOAD_IMG2MD_PATH, '')
        # txt_name = ''.join(img_name.split('.')[:-1]) + '.txt'
        # txt_path = RESULT_IMG2MD_TEMP_PATH + txt_name
        txt = self.single2txtEasyMode(img_path, 0.05, 'print')
        print(txt)
        with open(txt_path, 'a', encoding='utf8') as f:
            f.write(txt)
        return txt

    def run(self, img_path, txt_path, mode=None):
        suffix = img_path.split('.')[-1]
        if suffix == 'zip':
            output_name = self.img2md_multi(img_path)
            type = 'zip'
        elif suffix != 'zip':
            if mode == 'easy mode':
                output_name = self.img2md_single_easymode(img_path, txt_path)
            else:
                output_name = self.img2md_single(img_path)
            type = 'not zip'
        else:
            type = ''
            output_name = ''
        return output_name


if __name__ == '__main__':
    pro_img = Cimg2md2()
    img_path = "内容提取模型需求/仲裁申请书/jpg(100)/4957/32077028067044.jpg"
    pro_img.run(img_path, "1C.txt", 'easy mode')
    # path = "内容提取模型需求"
    # dir_list = os.listdir(path)
    # for dir in dir_list:
    #     if os.path.isfile(os.path.join(path, dir)):
    #         continue
    #     for dir2 in os.listdir(os.path.join(path, dir)):
    #         for dir3 in tqdm(os.listdir(os.path.join(path, dir, dir2))):
    #             # if this path contains directory
    #             if os.path.isdir(os.path.join(path, dir, dir2, dir3)):
    #                 for dir4 in sorted(os.listdir(os.path.join(path, dir, dir2, dir3))):
    #                     img_path = os.path.join(path, dir, dir2, dir3, dir4)
    #                     # 文件保存路径
    #                     txt_path = os.path.join("text", dir, dir2, dir3 + ".txt")
    #                     # create the dir if it doesn't exist
    #                     if not os.path.exists(os.path.join("text", dir, dir2)):
    #                         os.makedirs(os.path.join("text", dir, dir2))
    #                     try:
    #                         pro_img.run(img_path, txt_path, 'easy mode')
    #                     except:
    #                         print(os.path.join(dir, dir2, dir3))
    #             # word file
    #             else:
    #                 img_path = os.path.join(path, dir, dir2, dir3)
    #                 txt_path = os.path.join("text", dir, dir2, dir3.replace(".docx", ".txt"))
    #
    #                 if not os.path.exists(os.path.join("text", dir, dir2)):
    #                     os.makedirs(os.path.join("text", dir, dir2))
    #                 try:
    #                     pro_img.run(img_path, txt_path, 'easy mode')
    #                 except:
    #                     print(os.path.join(dir, dir2, dir3))

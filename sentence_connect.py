# coding:utf-8
from jsonpath import jsonpath
import numpy as np

class MatrixLine:
    def __init__(self, position):
        self.left_up_corner = [(position[0][0] + position[3][0]) / 2, (position[0][1] + position[1][1]) / 2]
        self.right_down_corner = [(position[1][0] + position[2][0]) / 2, (position[2][1] + position[3][1]) / 2]
        self.height = self.right_down_corner[1] - self.left_up_corner[1]
        self.width = self.right_down_corner[0] - self.left_up_corner[0]
        self.error = [0, 0]


class MatrixText(object):
    def __init__(self, position, text):
        self.left_up_corner = [(position[0][0] + position[3][0]) / 2, (position[0][1] + position[1][1]) / 2]
        self.right_down_corner = [(position[1][0] + position[2][0]) / 2, (position[2][1] + position[3][1]) / 2]
        self.height = self.right_down_corner[1] - self.left_up_corner[1]
        self.width = self.right_down_corner[0] - self.left_up_corner[0]
        self.text = text

    def compare(self, matrixText):
        return - self.left_up_corner[1] + matrixText.left_up_corner[1] >= 0

    def getLineSpacing(self, matrixText):
        line_space = self.left_up_corner[1] - matrixText.left_up_corner[1]
        return line_space

    # 左对齐，左对齐的精度要求比较高
    def left_align(self, matrixText):
        return abs(self.left_up_corner[0] - matrixText.left_up_corner[0]) < (self.height + matrixText.height) * 0.15


class MatrixBlock(object):
    def __init__(self):
        self.matrix_text_list = []

    def appendMatrixText(self, matrixText):
        self.matrix_text_list.append(matrixText)
        # if isinstance(matrixText,list):

    def getHeight(self):
        return np.mean([x.height for x in self.matrix_text_list])

    def calculateBorder(self, groups, mode):
        max_len = max([len(x) for x in groups])
        # 如何找到正文的左边界
        max_group_index = 0

        if mode==0:
            # 左边界为分组中数量最多的那个
            while len(groups[max_group_index]) != max_len:
                max_group_index = max_group_index + 1
            return max_group_index
        elif mode==1:
            # 左边界 如果最左边界分组中只有一个，那么默认其为标题, 最左边界为第二组
            if  len(groups[max_group_index])==1:
                return 0
            elif len(groups[max_group_index])>1 and len(groups[0]==1):
                return 1
            else:
                return 0
        else:
            return max_group_index;


    def divide_by_left_easymode(self):
        # 找到左边界的方法
        list_left = [[self.matrix_text_list[index].left_up_corner[0], index] for index in
                     range(len(self.matrix_text_list))]

        list_left.sort()

        groups = []
        for m_tuple in list_left:
            if len(groups) == 0:
                groups.append([m_tuple])
                # groups[len(groups)-1].append(m_tuple)
            else:
                # 这里的20应该是一个可以变化的值
                if abs(m_tuple[0] - groups[-1][0][0]) < self.getHeight()*1:
                    groups[-1].append(m_tuple)
                else:
                    groups.append([m_tuple])
        return groups

    def get_right_border(self, groups, left_group_index):
        right_list = [self.matrix_text_list[x[1]].right_down_corner[0] for x in groups[left_group_index]]
        # 有边界中位数
        # media = right_list[int(len(right_list)/2)]
        right_x = max(right_list)
        return right_x

    def divide_text(self, left_index, right_media, error_offset):
        texts = []
        index_last = -1
        for index in range(len(self.matrix_text_list)):
            if index not in left_index:
                texts.append([self.matrix_text_list[index].text])
                ++index_last
            else:
                if index == 0:
                    texts.append([self.matrix_text_list[index].text])
                    ++index_last
                else:
                    right_x = self.matrix_text_list[index - 1].right_down_corner[0]
                    if right_x > right_media - error_offset and self.matrix_text_list[index - 1].text[-1]\
                            not in ['。', '？', '!', '!'] \
                            and self.matrix_text_list[index].left_up_corner[1] - self.matrix_text_list[index-1].left_up_corner[1] < self.matrix_text_list[index-1].height*2.5   \
                            and '\t' not in self.matrix_text_list[index].text:
                        texts[index_last].append(self.matrix_text_list[index].text)
                    else:
                        texts.append([self.matrix_text_list[index].text])
                        ++index_last

        return texts


#
# 往下匹配：找到横坐标重叠，且行高一致，最近的一行

class SentenceConnect():
    def __init__(self):
        self.groups = []
        self.group_ranges = []

    def similarEqual(self, int_val_1, int_val_2, offset):
        if int_val_1 + offset >= int_val_2 and int_val_1 - offset <= int_val_2:
            return True
        return False

    # 查看该行是否已经被分组，
    # 若未分组，则为其创建新分组，若已分组，则需要匹配下一行(视觉上的)是否在该分组中
    def match(self, index, positions, texts, group_index):
        # 如果当前行没有被之前的行匹配进组，则创建新的分组
        m_position = positions[index]
        m_matrixLine = MatrixLine(positions[index])

        if texts[index] == '1.':
            print('catch u!')

        if group_index[index] == -1:
            m_group = {}
            m_group['height'] = (m_position[3][1] - m_position[0][1] + m_position[2][1] - m_position[1][1]) / 2
            m_group['space'] = 0  # 组中只有一行时无法判断行距
            m_group['left'] = (m_position[0][0] + m_position[3][0]) / 2  # 只会考虑左对齐
            m_group['right'] = (m_position[1][0] + m_position[2][0]) / 2
            m_group['size'] = 1
            m_group['left_up_corner'] = m_matrixLine.left_up_corner
            m_group['right_down_corner'] = m_matrixLine.right_down_corner
            self.groups.append(m_group)
            group_index[index] = len(self.groups) - 1
        else:
            # 已经被分组，则不用创建
            m_group = self.groups[group_index[index]]
        if m_matrixLine.width > 2 * m_group['height']:
            # 匹配下一行是否在该组中
            # 寻找下一行依据的策略：行的横坐标重叠
            nextMatrixLine = None
            for i in range(index + 1, len(positions)):
                #    next_position = positions[i]
                nextMatrixLine = MatrixLine(positions[i])
                if nextMatrixLine.left_up_corner[0] <= m_matrixLine.right_down_corner[0] and \
                        nextMatrixLine.left_up_corner[
                            0] >= m_matrixLine.left_up_corner[0] - 1.5 * m_group['height'] and \
                        nextMatrixLine.left_up_corner[1] > \
                        m_matrixLine.right_down_corner[1] - m_group['height'] * 0.5:
                    # 找到了最近的一行
                    # 特殊情况，这一行特别的小，则忽略
                    if nextMatrixLine.height < 3:
                        continue
                    else:
                        break
                else:
                    nextMatrixLine = None

            if nextMatrixLine != None:
                # 左侧匹配
                # 关于误差 需要考虑开头空行2个字符的情况，此处暂时不考虑
                # 行高需要考虑以下情况：
                # 如果该行是组里第一行，匹配的下一行左侧和高度都一致，但是实际上他可能是下一组的第一行
                #
                # if similarEqual(m_matrixLine.left_up_corner[0], nextMatrixLine.left_up_corner[0], m_group['height']) and similarEqual(m_matrixLine.height, nextMatrixLine.height, m_matrixLine.height*0.15):
                if self.similarEqual(m_matrixLine.height, nextMatrixLine.height, m_matrixLine.height * 0.15):
                    # 行高匹配
                    if m_group['space'] != 0:
                        if self.similarEqual(m_group['space'],
                                             nextMatrixLine.left_up_corner[1] - m_matrixLine.left_up_corner[1],
                                             m_group['space'] * 0.15):
                            # 在将新的一行加入组的过程中，需要不断调整组的左右边界
                            group_index[i] = group_index[index]
                            m_group['left'] = (m_group['left'] * m_group['size'] + nextMatrixLine.left_up_corner[0]) / (
                                    m_group['left'] + 1)
                            m_group['size'] = m_group['size'] + 1
                            # groups[group_index[index]] = m_group #将group更新的数据传到global var
                    else:
                        # m_group['space']==0 说明这是组内第一行
                        # 需要再匹配下一行，对比行距
                        next2edMatrixLine = None
                        for j in range(i + 1, len(positions)):
                            next2edMatrixLine = MatrixLine(positions[j])
                            if next2edMatrixLine.left_up_corner[0] <= m_matrixLine.right_down_corner[0] and \
                                    next2edMatrixLine.left_up_corner[0] >= m_matrixLine.left_up_corner[0]:
                                # 找到了最近的一行
                                # 特殊情况，这一行特别的小，则忽略
                                if next2edMatrixLine.height < 3:
                                    continue
                                else:
                                    break

                            else:
                                next2edMatrixLine = None
                        inGroup = False
                        if next2edMatrixLine != None:
                            if self.similarEqual(next2edMatrixLine.left_up_corner[0], nextMatrixLine.left_up_corner[0],
                                                 m_group['height']) and self.similarEqual(m_matrixLine.height,
                                                                                          nextMatrixLine.height,
                                                                                          nextMatrixLine.height * 0.15):
                                # 三行 a， b， c，前提是这三行左侧对齐且行号近似相等
                                # 如果a与b，b与c行距近似，则b可以加入a的组中
                                # 如果a与b > b与c，则b不应该加入a组
                                # 如果a与b < b与c，则b应该加入a组
                                if self.similarEqual(
                                        (next2edMatrixLine.left_up_corner[1] - nextMatrixLine.left_up_corner[1]),
                                        m_group['space'], m_group['space'] * 0.15):
                                    inGroup = True
                                elif (next2edMatrixLine.left_up_corner[1] - nextMatrixLine.left_up_corner[1]) < m_group[
                                    'space']:
                                    inGroup = False
                                else:
                                    inGroup = True
                        else:
                            inGroup = True
                        if inGroup:
                            group_index[i] = group_index[index]
                            m_group['left'] = (m_group['left'] * m_group['size'] + nextMatrixLine.left_up_corner[0]) / (
                                    m_group['left'] + 1)
                            m_group['space'] = nextMatrixLine.left_up_corner[1] - m_matrixLine.left_up_corner[1]
                            m_group['size'] = m_group['size'] + 1
                            m_group['right_down_corner'][1] = nextMatrixLine.right_down_corner[1]
                            if m_group['right_down_corner'][0] < nextMatrixLine.right_down_corner[0]:
                                m_group['right_down_corner'][0] = nextMatrixLine.right_down_corner[0]
            else:
                pass

    def parsePredict(self, predict):
        positions = jsonpath(predict, '$..position')[0]
        texts = jsonpath(predict, '$..texts')[0][0]
        return positions, texts

    def divideIntoGroup(self, positions, texts):
        """
        根据位置信息将文本分组

        :param positions: ocr接口返回的位置信息
        :param texts: ocr接口返回的文本信息
        :return:
            groups: groups[i]表示第i个分组的信息，行高，左对齐坐标，行距等
            group_index: group_index[i]对应positions[i]这个文本归属的group，对应groups的下标
            list_text: 按group来拼接的文本结果
        """
        group_index = [-1 for i in range(len(positions))]
        for index in range(len(positions)):
            self.match(index, positions, texts, group_index)
        # print(group_index)
        groupIdMax = 0
        for id in group_index:
            if groupIdMax < id:
                groupIdMax = id

        list_groupId_text = [[] for i in range(groupIdMax + 1)]
        for index in range(len(group_index)):
            list_groupId_text[group_index[index]].append(index)

        list_text = []
        for m_list in list_groupId_text:
            m_text = []
            for m_text_id in m_list:
                m_text.append(texts[m_text_id])
            list_text.append(m_text)
        # pd.DataFrame(list_text).to_csv('divided_group.txt', encoding="utf-8")
        return self.groups, group_index, list_text

    # positions, texts = parsePredict(loadPreidicts())
    # divideIntoGroup(positions, texts)

    def processOneBlock(self, m_block):
        texts_all = []
        if len(m_block.keys()) == 0:
            return texts_all
        # divideIntoGroup()
        list_positions_group_by_length = []
        m_len_pre = 0
        for (k, v) in m_block.items():
            if len(v) != 0:
                if len(v) != m_len_pre:
                    list_positions_group_by_length.append([])
                    m_len_pre = len(v)
                list_positions_group_by_length[len(list_positions_group_by_length) - 1].append(v)

        for m_positions_group_by_length in list_positions_group_by_length:
            # len_group = len(m_positions_group_by_length[0])
            len_group = 0
            for item in m_positions_group_by_length:
                len_group = max(len_group, len(item))
            # m_positions=[x[1] for x in m_positions_group_by_length[0]]
            # m_texts=[x[0] for x in m_positions_group_by_length[0]]
            m_positions = []
            m_texts = []
            for item in m_positions_group_by_length:
                # for m_item in item:
                for m_item in item:
                    m_positions.append(m_item[1])
                    m_texts.append(m_item[0])

            if len_group == 1:
                # 单列匹配，即每行只有1列，只需要区分出段落
                groups, group_index, list_text = self.divideIntoGroup(m_positions, m_texts)
                texts_all.append(list_text)
            elif len_group == 2 and len(m_positions) >= 3:
                # 双列匹配，可能是两块文字，也可能是两列的表格，需要加以区分
                # list_right_partion_left_boundry = [i[1] for i in [x[1] for x in [m for m in m_positions_group_by_length]]]
                # list_right_partion_text = [i[0] for i in [x[1] for x in [m for m in m_positions_group_by_length]]]
                # 判断每一行长度是否整齐，如果整齐的话断定其为一个表格
                isNeat = True
                for index in range(len(m_positions_group_by_length)):
                    if index != 0 and len(m_positions[index]) != len(m_positions[index - 1]):
                        isNeat = False
                        break
                if isNeat:
                    for item in m_positions_group_by_length:
                        # for m_item in item:
                        table_row = ""
                        for m_item in item:
                            table_row = table_row + m_item[0]
                            table_row = table_row + ('    ')
                        texts_all.append([table_row])
                else:
                    groups, group_index, list_text = self.divideIntoGroup(m_positions, m_texts)
                    texts_all.append(list_text)
            else:
                # 多行匹配，定义为表格，按行输出就完了
                # texts_all.append([m_texts])
                for item in m_positions_group_by_length:
                    # for m_item in item:
                    table_row = ""
                    for m_item in item:
                        table_row = table_row + m_item[0]
                        table_row = table_row + ('    ')
                    texts_all.append([table_row])

        return texts_all

    def processOneBlockEasyMode(self, m_block):

        matrixBlock = MatrixBlock()

        for key, value in m_block.items():

            text = ''
            m_position = [[],[],[],[]]

            if len(value)>1 and  value[0][1][0][1] - value[1][1][0][1]>0 and  value[0][1][0][1] - value[1][1][0][1] > (value[0][1][3][1] - value[0][1][0][1]) * 0.5:
                value = sorted(value, key=lambda x:x[1][0][1])
                for m in value:
                    m_mt = MatrixText(m[1], m[0])
                    matrixBlock.appendMatrixText(m_mt)

            else:
                for item in value:
                    text+= item[0] + '\t'
                text = text.strip('\t')

                m_position[0] = value[0][1][0]
                m_position[1] = value[-1][1][1]
                m_position[2] = value[-1][1][2]
                m_position[3] = value[0][1][3]

                mt = MatrixText(m_position, text)
                matrixBlock.appendMatrixText(mt)


        # pprint.pprint(matrixBlock)
        # list_left [[x, index, group_index]]
        groups = matrixBlock.divide_by_left_easymode()
        # if len(groups[0]) != max([len(x) for x in groups]):
        #     # 第一组应该是正文的左边界顶格吧
        #     raise Exception
        max_group_index = matrixBlock.calculateBorder(groups, -1)

        media = matrixBlock.get_right_border(groups, max_group_index)
        left_index = [x[1] for x in groups[max_group_index]]
        height = matrixBlock.getHeight()
        texts = matrixBlock.divide_text(left_index, media, height * 2)
        # pprint.pprint(texts)

        return texts

    # 整理 text_sum 格式，按整合为按行输出的格式
    def textSumStdOutput(self, text_sum):
        list_text = []

        for item in text_sum:
            for m_item in item:
                for m_m_item in m_item:
                    if len(m_m_item) > 1:
                        list_text.append([''.join(m_m_item)])
                    elif m_m_item:
                        list_text.append(m_m_item)
            list_text.append([])
        return list_text

    def textSumStdOutputEasyMode(self, text_sum):
        list_text = []

        for item in text_sum:
            for m_m_item in item:
                if len(m_m_item) > 1:
                    list_text.append([''.join(m_m_item)])
                elif m_m_item:
                    list_text.append(m_m_item)
        list_text.append([])
        return list_text

    def processBlocks(self, blocks):
        """
        处理blocks对象，最后按分块输出

        :param blocks: 上游返回的blocks对象
        :return:
            list_text: 二维数组，第一维为行数，第二维为列数，实际上第二维只有1列，为了转化成dataframe输出
        """
        text_sum = []
        for (key, value) in blocks.items():
            a = self.processOneBlock(value)
            text_sum.append(a)
        list_text = self.textSumStdOutput(text_sum)
        return list_text

    def processBlocksEasyMode(self, blocks):
        """
        处理blocks对象，最后按分块输出

        :param blocks: 上游返回的blocks对象
        :return:
            list_text: 二维数组，第一维为行数，第二维为列数，实际上第二维只有1列，为了转化成dataframe输出
        """
        text_sum = []
        for (key, value) in blocks.items():
            if len(value.items()) != 0:
                a = self.processOneBlockEasyMode(value)
                text_sum.append(a)
        list_text = self.textSumStdOutputEasyMode(text_sum)
        return list_text
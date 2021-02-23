from extractors import *
import os
import pandas as pd
from tqdm import tqdm


def extractor(df1, df2, path, name):
    filePath = os.path.join(path, name)
    nameInfo = {"文件名": name}
    otherInfo = {"文件名": name}
    subjectInfo = {}  # 原告
    objectInfo = {}  # 被告
    with open(filePath, encoding='utf-8', errors='ignore') as f:
        # 文章排序
        lines = lines_sort(f.readlines())
        count = 0
        # 抽取原告信息
        for i, line in enumerate(lines):
            # 至此可开始提取被告信息
            if ("被申请单位" in line or "被申请人" in line or "被告" in line or "被申请方" in line) and "原审被告" not in line:
                count = i
                break

            # 原告姓名
            subjectInfo = name_extractor1(0, subjectInfo, line)

            # 原告职位
            subjectInfo = position(subjectInfo, line)

            # 原告民族
            subjectInfo = nation_extractor(subjectInfo, line)

            # 原告性别
            subjectInfo = gender_extractor(subjectInfo, line)

            # 原告地址
            subjectInfo = address_extractor(subjectInfo, line)

            # 法人
            subjectInfo = legalRepresentative_extractor(subjectInfo, line)

            # 社会信代号
            subjectInfo = creditCode_extractor(subjectInfo, line)

            # 原告生日
            subjectInfo = birthday_extractor(subjectInfo, line)

            # 原告身份证号
            subjectInfo = id_extractor(subjectInfo, line)

            # 原告手机号
            subjectInfo = num_extractor(subjectInfo, line)

        # 抽取被告信息
        for line in lines[count: count + 7]:
            # 被告姓名
            objectInfo = name_extractor1(1, objectInfo, line)

            # 被告职位
            objectInfo = position(objectInfo, line)

            # 被告民族
            objectInfo = nation_extractor(objectInfo, line)

            # 被告性别
            objectInfo = gender_extractor(objectInfo, line)

            # 被告地址
            objectInfo = address_extractor(objectInfo, line)

            # 法人
            objectInfo = legalRepresentative_extractor(objectInfo, line)

            # 社会信代号
            objectInfo = creditCode_extractor(objectInfo, line)

            # 被告生日
            objectInfo = birthday_extractor(objectInfo, line)

            # 被告身份证号
            objectInfo = id_extractor(objectInfo, line)

            # 被告手机号
            objectInfo = num_extractor(objectInfo, line)

        # 事实及理由
        otherInfo = reason_extractor(otherInfo, lines)

        # 申请事项
        for line in lines[count: count + 15]:
            otherInfo = event_extractor(otherInfo, line, lines[count:])

        # 仲裁机构
        otherInfo = institute_extractor(otherInfo, lines[::-1])

        # 申请日期
        otherInfo = apply_date(otherInfo, lines[::-1])

        # 有无签名
        otherInfo = signature(otherInfo, lines[::-1])

        lst1 = [nameInfo, subjectInfo, objectInfo]
        lst2 = [otherInfo]
        df1 = df1.append(lst1)
        df2 = df2.append(lst2)

        return df1, df2


def extractor2(df1, df2, path, name):
    filePath = os.path.join(path, name)
    nameInfo = {"文件名": name}
    otherInfo = {"文件名": name}
    subjectInfo = {"身份": "申请人"}  # 原告
    objectInfo1 = {"身份": "被申请人"}  # 被告1
    objectInfo2 = {}  # 被告2

    with open(filePath, encoding='utf-8', errors='ignore') as f:
        # 文章排序
        lines = lines_sort(f.readlines())
        # 1. 抽取姓名信息
        subjectInfo, objectInfo1, objectInfo2, part = name_extractor2(subjectInfo, objectInfo1, objectInfo2, lines)

        # 2. 抽取原告其它信息
        for i, line in enumerate(lines[part[0][0]: part[0][1] + 1]):
            # 原告职位
            subjectInfo = position(subjectInfo, line)

            # 原告民族
            subjectInfo = nation_extractor(subjectInfo, line)

            # 原告性别
            subjectInfo = gender_extractor(subjectInfo, line)

            # 原告地址
            subjectInfo = address_extractor(subjectInfo, line)

            # 法人
            subjectInfo = legalRepresentative_extractor(subjectInfo, line)

            # 社会信代号
            subjectInfo = creditCode_extractor(subjectInfo, line)

            # 原告生日
            subjectInfo = birthday_extractor(subjectInfo, line)

            # 原告身份证号
            subjectInfo = id_extractor(subjectInfo, line)

            # 原告手机号
            subjectInfo = num_extractor(subjectInfo, line)

        # 3. 抽取被告信息
        flag = False
        if "委托申请人" not in subjectInfo:
            start, end = part[1][0], part[1][1] + 1
            if len(part) == 3:
                flag = True
        else:
            start, end = part[2][0], part[2][1] + 1
            if len(part) == 4:
                flag = True
        for line in lines[start: end]:
            # 被告姓名
            objectInfo1 = name_extractor1(1, objectInfo1, line)

            # 被告职位
            objectInfo1 = position(objectInfo1, line)

            # 被告民族
            objectInfo1 = nation_extractor(objectInfo1, line)

            # 被告性别
            objectInfo1 = gender_extractor(objectInfo1, line)

            # 被告地址
            objectInfo1 = address_extractor(objectInfo1, line)

            # 法人
            # objectInfo1 = legalRepresentative_extractor(objectInfo1, line)

            # 社会信代号
            objectInfo1 = creditCode_extractor(objectInfo1, line)

            # 被告生日
            objectInfo1 = birthday_extractor(objectInfo1, line)

            # 被告身份证号
            objectInfo1 = id_extractor(objectInfo1, line)

            # 被告手机号
            objectInfo1 = num_extractor(objectInfo1, line)

        # 4. 若有两个被申请人
        if flag:
            start, end = part[-1][0], part[-1][1] + 1
            for line in lines[start: end]:
                objectInfo1["身份"] = "被申请人一"
                objectInfo2["身份"] = "被申请人二"
                # 被告姓名
                objectInfo2 = name_extractor1(1, objectInfo2, line)

                # 被告职位
                objectInfo2 = position(objectInfo2, line)

                # 被告民族
                objectInfo2 = nation_extractor(objectInfo2, line)

                # 被告性别
                objectInfo2 = gender_extractor(objectInfo2, line)

                # 被告地址
                objectInfo2 = address_extractor(objectInfo2, line)

                # 法人
                # objectInfo1 = legalRepresentative_extractor(objectInfo1, line)

                # 社会信代号
                objectInfo2 = creditCode_extractor(objectInfo2, line)

                # 被告生日
                objectInfo2 = birthday_extractor(objectInfo2, line)

                # 被告身份证号
                objectInfo2 = id_extractor(objectInfo2, line)

                # 被告手机号
                objectInfo2 = num_extractor(objectInfo2, line)

        # 事实及理由
        otherInfo = reason_extractor(otherInfo, lines)

        # 申请事项
        for line in lines[part[-1][1] + 1: part[-1][1] + 1 + 10]:
            otherInfo = event_extractor(otherInfo, line, lines[part[-1][1] + 1:])

        # 仲裁机构
        otherInfo = institute_extractor(otherInfo, lines[::-1])

        # 申请日期
        otherInfo = apply_date(otherInfo, lines[::-1])

        # 有无签名
        otherInfo = signature(otherInfo, lines[::-1])

        if not objectInfo2:
            lst1 = [nameInfo, subjectInfo, objectInfo1]
        else:
            lst1 = [nameInfo, subjectInfo, objectInfo1, objectInfo2]
        lst2 = [otherInfo]
        df1 = df1.append(lst1)
        df2 = df2.append(lst2)

        return df1, df2


def test(df1, path, name):
    filePath = os.path.join(path, name)
    with open(filePath, encoding='utf-8', errors='ignore') as f:
        # 文章排序
        lines = lines_sort(f.readlines())
        sub, obj1, obj2, part = name_extractor2({}, {}, {}, lines)
        if obj2:
            lst = [{"文件名": name}, sub, obj1, obj2]
        else:
            lst = [{"文件名": name}, sub, obj1]
        df1 = df1.append(lst)
    return df1


if __name__ == "__main__":
    path = "text/仲裁申请书/jpg(100)"
    file_dir = os.listdir(path)
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    for name in tqdm(sorted(file_dir)):
        # df1, df2 = extractor(df1, df2, path, name)
        try:
            df1, df2 = extractor2(df1, df2, path, name)
            columns = list(df1)
            columns.insert(0, columns.pop(columns.index("文件名")))
            columns.insert(1, columns.pop(columns.index("身份")))
            columns.insert(2, columns.pop(columns.index("姓名")))
            columns.insert(3, columns.pop(columns.index("性别")))
            columns.insert(4, columns.pop(columns.index("民族")))
            columns.insert(5, columns.pop(columns.index("地址")))
            # columns.insert(6, columns.pop(columns.index("委托申请人")))
            df1 = df1.loc[:, columns]
        except Exception as e:
            print(name, e)

    print("Finished! ! !")
    df1.to_csv("results/result1.csv", encoding="utf_8_sig")
    df2.to_csv("results/result2.csv", encoding="utf_8_sig")
    # df1.to_csv("results/test.csv", encoding="utf_8_sig")

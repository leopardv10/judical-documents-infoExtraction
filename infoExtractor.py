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


if __name__ == "__main__":
    path = "text/仲裁申请书/jpg(100)"
    file_dir = os.listdir(path)
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    for name in tqdm(sorted(file_dir)):
        # df1, df2 = extractor(df1, df2, path, name)
        try:
            df1, df2 = extractor(df1, df2, path, name)
        except:
            print(name, "error")
            # break
    print("Finished! ! !")
    df1.to_csv("results/result1.csv", encoding="utf_8_sig")
    df2.to_csv("results/result2.csv", encoding="utf_8_sig")

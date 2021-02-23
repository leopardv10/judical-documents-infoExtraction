import re
from nation import *
import requests
from config import *
import json
from pprint import pprint
import fool


# 规则抽取
def name_extractor1(flag, dic, line):
    def helper(start, line):
        end = line.find(",", start) if line.find(",", start) != -1 else line.find("。", start)
        if end == -1:
            end = len(line)
        name = line[start: end].strip().strip(":").strip().split()
        if not name:
            return None
        return name[0] if ":" not in name[0] else name[0].split(":")[1]

    # 0是原告，1是被告
    if flag == 0:
        char = ""
    elif flag == 1:
        char = "被"
    else:
        print("flag的取值必须为0或1")
        return

    if char + "上诉人" in line and "姓名" not in dic.keys():
        start = line.index(char + "上诉人") + 4
        # print(name)
        dic["姓名"] = helper(start, line)
    elif (char + "申请人" in line or char + "申请方" in line or char + "申请单位" in line) and "姓名" not in dic.keys():
        start = line.index(char + "申请") + 4
        # print(name)
        dic["姓名"] = helper(start, line)
    elif flag == 0 and "原告" in line and "姓名" not in dic.keys():
        start = line.find("原告") + 3
        # print(name)
        dic["姓名"] = helper(start, line)
    elif flag == 1 and "被告" in line and "姓名" not in dic.keys():
        start = line.index("被告") + 3
        dic["姓名"] = helper(start, line)
    return dic


# 用NER模型辅助抽取
def name_extractor2(sub: dict, obj1: dict, obj2: dict, lines: list):
    # eg:[[1, 4], [5, 6], [7, 10]]
    role = ["申请人"]
    part = [[1]]
    # 文本分段
    for i, line in enumerate(lines):
        if "申请事项" in line or "诉讼请求" in line or "仲裁请求" in line or "诉讼申请" in line \
                or "申请请求" in line or "申请要求" in line or "申请仲裁事项" in line or "请求事项" in line or "仲裁要求" in line:
            part[-1].append(i - 1)
            break
        elif "委托申请人" in line:
            role.append("委托申请人")
            part[-1].append(i - 1)
            part.append([i])
        elif "被申请人" in line or "被申请方" in line or "被申请单位" in line:
            # 可能出现line = 被申请人: 这种情况
            if "被申请人:" == line.strip() or "被申请方:" == line.strip() or "被申请单位:" == line.strip():
                continue
            if "被申请人一" not in role:
                role.append("被申请人一")
            else:
                role.append("被申请人二")
            part[-1].append(i - 1)
            part.append([i])
    # print(part)
    name_list = []
    # 每一段提取姓名信息
    for para in part:
        def sort_function(d):
            return d[0]
        # 模型抽取
        names = []
        txt = "".join(lines[para[0]: para[1] + 1])
        textmode = {"sentence": txt}
        r = json.loads(requests.post(NER_API, data=textmode).text)
        # pprint(r)
        entity_list = r["data"]["entity_list"]
        for dic in entity_list:
            if dic["entity_type"] == "人名" and dic["entity"] not in entity_list:
                # [人名位置, 人名]
                names.append([dic["entity_index"]["begin"], dic["entity"]])

        # 如果，NER模型没抽出来，用foolnltk辅助抽取
        if not names:
            # [(3, 4, "person", "张三")]
            res = fool.analysis(txt)[1][0]
            for t in res:
                if "person" in t:
                    names.append([t[0], t[3].strip()])

        # 按姓名的start index排序, names = [[2, 张三], [4, 王五]]
        names.sort(key=sort_function)
        use = []
        for name in names:
            use.append(name[1])
        name_list.append(use)

    # res -> {'委托申请人': ['朱荣贵'], '申请人': ['冯明显'], '被申请人一': ['孙辉']}
    res = {}
    for r, n in zip(role, name_list):
        res[r] = n
    # pprint(res)

    # 将res中的结果保存到csv中
    for key in res.keys():
        if key == "申请人":
            sub["姓名"] = res[key][0] if res[key] else None
        elif key == "委托申请人":
            sub["委托申请人"] = res[key][0] if res[key] else None
        # 被申请人都是公司，这里人名都是法人和其他相关人士
        elif key == "被申请人一":
            for i, name in enumerate(res[key]):
                if i == 0:
                    obj1["法人姓名"] = name
                else:
                    obj1["单位联系人"] = name
        elif key == "被申请人二":
            for i, name in enumerate(res[key]):
                if i == 0:
                    obj2["法人姓名"] = name
                else:
                    obj2["单位联系人"] = name

    return sub, obj1, obj2, part


def creditCode_extractor(dic, line):
    if "信用代码" in line:
        start = line.find("信用代码") + 5
        end = line.find(",", start) if line.find(",", start) != -1 else line.find("。", start)
        if end == -1: end = len(line)
        code = line[start: end].strip("\t").strip("\n").split("法定代表人")[0]
        if len(code) > 10:
            code = code.split("联系电话")[0].split()
            dic["统一社会信用代码"] = code[1] if len(code) > 1 else code[0]
    return dic


def id_extractor(dic, line):
    id = re.findall("\d{17}[\d|x|X]", line)
    if id and "身份证号" not in dic.keys():
        dic["身份证号"] = id[0]
    return dic


def legalRepresentative_extractor(dic, line):
    if "法定代表人" in line:
        start = line.find("法定代表人") + 6
        end = line.find(",", start) if line.find(",", start) != -1 else line.find("。", start)
        if end == -1: end = len(line)
        legalPerson = line[start: end].strip("\t").strip("\n").strip(":")
        if len(legalPerson) > 4:
            textmod = {"sentence": legalPerson}
            r = json.loads(requests.post(NER_API, data=textmod).text)["data"]["entity_list"]
            for each in r:
                if each["entity_type"] == "人名":
                    dic["法人"] = each["entity"]
                    break
        else:
            dic["法人"] = legalPerson

    return dic


# 联系方式
def num_extractor(dic, line):
    tmp = ["联系方式1", "联系方式2", "联系方式3"]
    # 手机
    phone = re.finditer("1[34578]\d{9}", line)
    count = 0
    for num in phone:
        # 排除身份证中提取手机号
        if num.span()[0] - 1 >= 0 and line[num.span()[0] - 1].isdigit(): continue
        dic[tmp[count]] = num.group()
        count += 1
        if count > 2: break
    # 座机
    landline = re.findall("0\\d{2,3}-\\d{7,8}", line)
    if count <= 2 and landline:
        for num in landline:
            dic[tmp[count]] = num
            count += 1
            if count > 2: break
    return dic


# 职位
def position(dic, line):
    pos = ["总经理", "董事长", "执行董事", "校长"]
    if "职务" in line or "职位" in line and "职位" not in dic:
        start = max(line.find("职务"), line.find("职位")) + 3
        end = line.find(",", start) if line.find(",", start) != -1 else line.find("。", start)
        if end == -1: end = len(line)
        pos = line[start: end].strip("\t").strip("\n").split("\t")
        dic["职位"] = pos[0]
    elif "职位" not in dic:
        for p in pos:
            if p in line:
                dic["职位"] = p
            break
    return dic


def gender_extractor(dic, line):
    if ",男," in line and "性别" not in dic.keys():
        gender = "男"
        dic["性别"] = gender
    elif ",女," in line and "性别" not in dic.keys():
        gender = "女"
        dic["性别"] = gender
    elif "性别:" in line and "性别" not in dic.keys():
        start = line.find("性别")
        for i in range(start, len(line)):
            if line[i] == "男":
                gender = "男"
                dic["性别"] = gender
                break
            elif line[i] == "女":
                gender = "女"
                dic["性别"] = gender
                break
    return dic


def birthday_extractor(dic, line):
    birthDay = re.findall("(\d{4}([年/-]\d{1,2}([月/-]\d{1,2}(日|$)|[月/-]$|$)|年$|$))", line)
    if birthDay and "生日" not in dic.keys():
        if len(birthDay[0][0]) != 4: dic["生日"] = birthDay[0][0]
    if "出生日期" in line and "生日" not in dic.keys():
        start = line.find("出生日期") + 5
        end = line.find(",", start) if line.find(",", start) != -1 else line.find("。", start)
        if end == -1: end = len(line)
        birthday = line[start: end].strip("\t").strip("\n").split("\t")
        dic["生日"] = birthday[0]
    return dic


def nation_extractor(dic, line):
    if "民族:" in line and "民族" not in dic.keys():
        start = line.find("民族:") + 3
        end = len(line) if line.find(",", start) == line.find("。", start) == -1 else \
            max(line.find(",", start), line.find("。", start))
        nation = line[start: end]
        dic["民族"] = nation

    elif "民族" not in dic.keys():
        for n in NATION:
            if n in line:
                nation = n
                dic["民族"] = nation
                break
    return dic


def address_extractor(dic, line):
    def helper(address):
        lst = ["统一信用代码", "身份证", "电话", "联系电话", "法定代表人", "邮编", "家庭", "注册地址", "统一社会信用代码"]
        for s in lst:
            if s in address:
                address = address[0: address.find(s)]
        return address

    def helper2(address):
        max_len = 0
        t = 0
        for i, add in enumerate(address):
            if len(add) > max_len:
                max_len = len(add)
                t = i
        return t

    line = line.strip().rstrip("身份证住址:").rstrip("注册地址:").rstrip("住所地:").rstrip("住所:")
    if ("省" in line and "市" in line) or ("省" in line and "县" in line):
        start = line.find("省") - 2 if line.find("省") - 2 > 0 else 0
        end = line.find(",", start) if line.find(",", start) != -1 else line.find("。", start)
        if end == -1:
            end = len(line)
        address = line[start: end].strip("\t").strip("\n").strip("注册地址:").strip("身份证住址:").strip(":")
        dic["地址"] = helper(address)
    elif "市" in line and "区" in line:
        start = line.find("市") - 2 if line.find("市") - 2 > 0 else 0
        end = line.find(",", start) if line.find(",", start) != -1 else line.find("。", start)
        if end == -1:
            end = len(line)
        address = line[start: end].strip("\t").strip("\n").strip("注册地址:").strip("身份证住址:").strip(":")
        dic["地址"] = helper(address)
    elif "地址" in line:
        start = line.rfind("地址") + 3
        end = line.find(",", start) if line.find(",", start) != -1 else line.find("。", start)
        if end == -1:
            end = len(line)
        address = line[start: end].strip("\t").strip("\n").strip("注册地址:").strip("身份证住址:")
        dic["地址"] = helper(address)
    elif "住址" in line:
        start = line.rfind("住址") + 3
        end = line.find(",", start) if line.find(",", start) != -1 else line.find("。", start)
        if end == -1:
            end = len(line)
        address = line[start: end].strip("\t").strip("\n").strip("注册地址:").strip("身份证住址:")
        dic["地址"] = helper(address)
    elif "住所地" in line or "住所" in line:
        start = line.rfind("住所") + 3
        end = line.find(",", start) if line.find(",", start) != -1 else line.find("。", start)
        if end == -1:
            end = len(line)
        address = line[start: end].strip("\t").strip("\n").strip("注册地址:").strip("身份证住址:").strip(":")
        dic["地址"] = helper(address)
    return dic


def signature(dic, lines):
    for i, line in enumerate(lines[0: 10]):
        if "申请人:" in line and "有无签名" not in dic.keys():
            if 2 <= len(line.strip()) - 4 <= 4 or 2 <= len(lines[i + 1]) <= 4:
                dic["有无签名"] = "有签名"
            break
    if "有无签名" not in dic.keys():
        dic["有无签名"] = "无签名"
    return dic


# 仲裁机构
def institute_extractor(dic, lines):
    for line in lines:
        if "仲裁机构" not in dic.keys() and ("仲裁委员会" in line or "仲裁院" in line
                                         or "仲裁庭" in line or "委员会" in line or "仲裁委员" in line) and len(line) < 20:
            dic["仲裁机构"] = line.strip().strip("\t").strip("\n")
            break
    return dic


def apply_date(dic, lines):
    for line in lines:
        birthDay = re.findall("(\d{4}([年/-]\d{1,2}([月/-]\d{1,2}(日|$)|[月/-]$|$)|年$|$))", line)
        if birthDay and "申请日期" not in dic.keys():
            dic["申请日期"] = birthDay[0][0]
        break
    return dic


# 申请事项
def event_extractor(dic, line, lines):
    lst = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "、", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    if "申请事项" in line or "诉讼请求" in line or "仲裁请求" in line or "诉讼申请" in line \
            or "申请请求" in line or "申请要求" in line or "申请仲裁事项" in line or "请求事项" in line or "仲裁要求" in line:
        # print(line)
        line_num = 0
        index = lines.index(line)
        flag = False
        # 该行有具体事项
        if len(line.strip()) > 10:
            line_num += 1
            flag = True
        for i in range(index + 1, index + 11):
            if i < len(lines) and lines[i].strip()[0: 1] in lst:
                # print(lines[i])
                line_num += 1
        # print(line_num)
        if flag:
            c = 0
            while c < line_num:
                dic["申请事项%d" % (c + 1)] = lines[index + c].strip("申请事项:").strip("诉讼请求:")
                c += 1
        else:
            c = 1
            while c <= line_num:
                dic["申请事项%d" % c] = lines[index + c].strip()
                c += 1
    return dic


# 事实及理由
def reason_extractor(dic, lines):
    res = ""
    start, end = 0, len(lines)
    for i, line in enumerate(lines):
        if "事实" in line and "理由" in line:
            start = i
        elif "此致" in line:
            end = i
    for i in range(start, end):
        res += lines[i]
    dic["事实及理由"] = res.strip().strip("事实及理由").strip("事实和理由").strip(":").strip("与理由:")
    return dic


# 将顺序错乱的文本排序
def lines_sort(lines):
    count = 0
    for i, line in enumerate(lines):
        if len(line.strip()) < 15 and ("仲裁申请书" in line or "仲裁反申请书" in line):
            count = i
    return lines[count:] + lines[0: count]
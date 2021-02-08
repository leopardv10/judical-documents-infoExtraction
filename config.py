# coding:utf-8
import os

# BASE_DIR = '/data/file_converter_web/'
BASE_DIR = '/Users/wangyayun/Documents/cloud/python_workspace/file2txt'
# BASE_DIR = './'
UPLOAD_BASE_PATH = os.path.join(BASE_DIR, "upload/{}/")
RESULT_BASE_PATH = os.path.join(BASE_DIR, "result/{}/")
RESULT_BASE_TEMP_PATH = os.path.join(BASE_DIR, "result/{}/temp/")
FEEDBACK_UPLOAD_PATH = os.path.join(BASE_DIR, "feedback/upload/")
FEEDBACK_RESULT_PATH = os.path.join(BASE_DIR, "feedback/result/")

FUNC_DICT = {
    'html2md': 'HTML转MD文件',
    'pdf2img': 'PDF转图片',
    'pdf2md': 'PDF转MD文件',
    'word2excel': 'WORD转EXCEL文件',
    'word2md': 'WORD转MD文件',
    'img2md': '图片转MD文件',
    'img2txt': 'OCR测试',
    'pdf2md_pro': 'PDF转MD文件（复杂版本）',
    'pdf2md_english': 'PDF转MD文件（英文）'
}

UPLOAD_HTML2MD_PATH = os.path.join(BASE_DIR, "upload/html2md/")
UPLOAD_PDF2IMG_PATH = os.path.join(BASE_DIR, "upload/pdf2img/")
UPLOAD_PDF2MD_PATH = os.path.join(BASE_DIR, "upload/pdf2md/")
UPLOAD_WORD2EXCEL_PATH = os.path.join(BASE_DIR, "upload/word2excel/")
UPLOAD_WORD2MD_PATH = os.path.join(BASE_DIR, "upload/word2md/")
UPLOAD_IMG2MD_PATH = os.path.join(BASE_DIR, "upload/img2md/")
UPLOAD_PDF2MD_PRO_PATH = os.path.join(BASE_DIR, "upload/pdf2md_pro/")
UPLOAD_PDF2MD_ENGLISH_PATH = os.path.join(BASE_DIR, "upload/pdf2md_english/")
UPLOAD_BATCH_PATH = os.path.join(BASE_DIR, "upload/batch/")

RESULT_WORD2EXCEL_PATH = os.path.join(BASE_DIR, "result/word2excel/")
RESULT_IMG2MD_TEMP_PATH = os.path.join(BASE_DIR, "result/img2md/temp/")
RESULT_IMG2MD_PATH = os.path.join(BASE_DIR, "result/img2md/")
RESULT_PDF2IMG_PATH = os.path.join(BASE_DIR, "result/pdf2img/")
RESULT_PDF2MD_PATH = os.path.join(BASE_DIR, "result/pdf2md/")
RESULT_WORD2MD_PATH = os.path.join(BASE_DIR, "result/word2md/")
RESULT_HTML2MD_PATH = os.path.join(BASE_DIR, "result/html2md/")
RESULT_PDF2MD_PRO_PATH = os.path.join(BASE_DIR, "result/pdf2md_pro/")
RESULT_PDF2MD_ENGLISH_PATH = os.path.join(BASE_DIR, "result/pdf2md_english/")
RESULT_BATCH_PATH = os.path.join(BASE_DIR, "result/batch/")

STATIC_PATH = os.path.join(BASE_DIR, "app/static/")

UPLOAD_PATH = {
    'pdf2md': UPLOAD_PDF2MD_PATH,
    'pdf2md_pro': UPLOAD_PDF2MD_PRO_PATH,
    'pdf2md_english': UPLOAD_PDF2MD_ENGLISH_PATH
}

RESULT_PATH = {
    'pdf2md': RESULT_PDF2MD_PATH,
    'pdf2md_pro': RESULT_PDF2MD_PRO_PATH,
    'pdf2md_english': RESULT_PDF2MD_ENGLISH_PATH
}

# img2md
# LENGTH_OFFSET: 行最小长度min_line_length偏移量
LENGTH_OFFSET = 5
# LENGTH_RANGE：从行数排名的前3名取最大值作为行字数基准
LENGTH_RANGE = 3

# OCR API
OCR_API = 'http://172.27.232.36:8506'
# OCR_API = "http://172.27.231.82:8512"
# OCR_API = 'http://172.27.231.11:31908'
PREDICT_URL = OCR_API + '/lab/ocr/predict/general'
OCR_TABLE_URL = OCR_API + '/lab/ocr/predict/table'


# NER API
NER_API = "http://m7-model-gpu23:8100/predict"


# ALLOWED EXTENSIONS
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'docx', 'pdf', 'wps', 'html', 'htm', 'zip', 'doc']
ALLOWED_IMG_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
ALLOWED_WORD_EXTENSIONS = ['doc', 'docx', 'wps']
ALLOWED_PDF_EXTENSIONS = ['pdf']
ALLOWED_HTML_EXTENSIONS = ['html', 'htm']

# 剔除word中影响文件转换效果的标签
REMOVE_TAG = ['w:ins .+?', 'w:sdt', 'w:sdtContent', 'w:hyperlink .+?']

# MYSQL
MYSQL_HOST = '172.27.128.72'
MYSQL_USERNAME = 'wangyayun'
MYSQL_PASSWORD = 'ai4every1'
MYSQL_DATABASE = 'file_converter'
MYSQL_PORT = 3306

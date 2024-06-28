#! usr/bin/env python3
# -*- coding:utf-8 -*-
 
"""
@Author:jsheng
"""

import re
import six


# 空格
space = u' '
# 换行符
line_breaker = u'\n'
# 字符形式的unicode
re_unicode= re.compile(u'\\\\u[a-zA-Z0-9]{4}')
# 字符形式的utf8
re_uft8 = re.compile(u'\\\\x[a-zA-Z0-9]{2}')
# url
re_url= re.compile(u'(https?|ftp|file):(//)?[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')
# 中文字符集合
re_han = re.compile(
    u"([^\u4E00-\u9FA5a-zA-Z0-9【\[\]】{}（()）《》；;，,。.:：“”<>！!？?、\"'*‘’%+-.@=\\\\|/\n _])", re.U
)
# CDATA
re_cdata = re.compile(u'//<!\[CDATA\[[^>]*//\]\]>', re.I)  
# Script
re_script = re.compile(u'<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I) 
# Style
re_style = re.compile(u'<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)
# HTML换行
re_br = re.compile(u'<br\s?.*?/?>')  
re_p = re.compile(u'</?p\s?.*?/?>')
# HTML注释
re_comment = re.compile(u'<!--[^>]*-->')
# HTML注释
re_comment1 = re.compile(u'<![^>]*-->')
# 普通HTML语法标识
re_comp = re.compile(u'</?\w+[^>]*>')
# 连续换行
re_multiple_line_breakers = re.compile('[\n]+')
# 连续空格
re_multiple_spaces = re.compile('[ ]+')
# HTML特殊字符
CHAR_ENTITIES = {
    'nbsp': ' ',
    '160': ' ',
    'lt': '<',
    '60': '<',
    'gt': '>',
    '62': '>',
    'amp': '&',
    '38': '&',
    'quot': '"',
    '34': '"', 
    'ldquo': '"',
    "rdquo": '"',
    "13": '\r'
}
re_char_entity = re.compile(u'&#?(?P<name>\w+);')


def chr_with_six(num):
    if six.PY3:
        char = chr(num)
    elif six.PY2:
        char = unichr(num)
    else:
        raise ValueError("Not running on Python2 or Python 3?")
    return char


def full_2_half(s):
    """ Convert full-width character to half-width one """
    n = list()
    for char in s:
        num = ord(char)
        if num == 0x3000:
            num = 32
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xfee0
        char = chr_with_six(num)
        n.append(char)
    return ''.join(n)

def replace_html(s):
    """ Deprecated! convert html special terms to normal ones """
    s = s.replace(u'&quot;', u'"')
    s = s.replace(u'&amp;', u'&')
    s = s.replace(u'&lt;', u'<')
    s = s.replace(u'&gt;', u'>')
    s = s.replace(u'&nbsp;', u' ')
    s = s.replace(u"&ldquo;", u"“")
    s = s.replace(u"&rdquo;", u"”")
    s = s.replace(u"&mdash;", u"")
    s = s.replace(u"\xa0", u" ")
    return s

def strip_control_characters(s):
    """ 去除ASCII控制字符，编码为0~31，但保留编码为10的\n和编码为13的\r，然后去除不可见编码"""
    word = ''
    num=0
    for i in s:
        if ord(i)>31 or ord(i) == 10 or ord(i) == 13:
            word += i
            num+=1
    
    word = word.encode("gbk", errors="ignore").decode("gbk", errors="ignore")
    return word

def replace_char_entity(htmlstr):
    sz = re_char_entity.search(htmlstr)
    while sz:
        key = sz.group('name')  # 去除&;后entity,如>为gt
        try:
            htmlstr = re_char_entity.sub(CHAR_ENTITIES[key], htmlstr, 1)
            sz = re_char_entity.search(htmlstr)
        except KeyError:
            if key.isdigit():
                # 将&#+数字恢复成unicode
                char = chr_with_six(int(key))
                htmlstr = re_char_entity.sub(char, htmlstr, 1)
            else:
                # 否则以空串代替
                htmlstr = re_char_entity.sub('', htmlstr, 1)
            sz = re_char_entity.search(htmlstr)
    return htmlstr

def remove_and_convert_html(content):
    content = re_cdata.sub('', content)  # 去掉CDATA
    content = re_script.sub('', content)  # 去掉SCRIPT
    content = re_style.sub('', content)  # 去掉style
    content = re_br.sub('\n', content)  # 将br转换为换行
    content = re_p.sub('\n', content)  # 将p转换为换行
    content = re_comp.sub('', content)
    content = re_comment.sub('', content)
    content = re_comment1.sub('', content)
    content = replace_char_entity(content)  # 替换html特有符号
    content = content.replace(u"\xa0", u" ")
    return content

def preprocess(content):
    """ 标准处理流程，每一步输入输出都为unicode """
    # 处理html特有字符
    content = remove_and_convert_html(content)
    # 去掉控制字符，不含\n和\r
    content = strip_control_characters(content)
    # 全角转半角
    content = full_2_half(content)
    # 将文章开头与结尾的空格和换行符去掉
    content = content.strip()
    # 将\r改成\n
    content = content.replace(u'\r', u'\n')
    content = content.replace('“', '')
    # 将多个连续换行符用单个换行符替换
    content = re_multiple_line_breakers.sub('\n', content)
    # 连续空格
    content = re_multiple_spaces.sub(' ', content)
    return content

def decent_preprocess(content):
    content = preprocess(content)
    #只保留需要的字符
    content=re_han.sub('', content)
    #去掉网址
    content=re_url.sub('', content)
    return content
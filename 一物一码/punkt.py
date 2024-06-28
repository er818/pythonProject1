#! usr/bin/env python3
# -*- coding:utf-8 -*-
 
"""
@Author:jsheng
"""

from 一物一码.preprocess import preprocess, decent_preprocess, line_breaker

punct_initiator = u'。;!?\n'
punct_follower = u'".。;)”\'’?!\n'

def punct(content, include_line_breaker=False):
    sentence = u''
    sentences = list()
    # 0 = Normal, 1 = pre cut
    state = 0
    has_line_breaker = False
    for word in content:
        is_cut = False
        if state == 0:
            if word in punct_initiator:
                state = 1
        else:
            if word not in punct_follower:
                state = 0
                is_cut = True
        if is_cut:
            sentence = sentence.strip()
            if sentence:
                sentences.append(sentence)
            if include_line_breaker and has_line_breaker and sentences[-1] != u"\n":
                sentences.append(line_breaker)
                has_line_breaker = False
            sentence = u''
        if word != "\n":
            sentence += word
        else:
            has_line_breaker = True
    if sentence:
        sentence = sentence.strip()
        if sentence:
            sentences.append(sentence)

    return sentences

def preprocess_and_punct(content, is_decent=False, include_line_breaker=False):
    if is_decent:
        content = decent_preprocess(content)
    else:
        content = preprocess(content)
    sentences = punct(content, include_line_breaker)
    sentence = ''.join(sentences)

    return sentence


if __name__=='__main__':
    sents = ['BB000006130.9%氯化钠注射液(500ML袋)', '奥布卡因凝胶 x', '★血清总胆红素测定(化学法或酶促法']
    for sent in sents:
        print(preprocess_and_punct(sent, is_decent=True, include_line_breaker=True))



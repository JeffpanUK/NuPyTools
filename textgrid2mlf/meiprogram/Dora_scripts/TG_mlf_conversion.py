#!/usr/bin/env python3
# -*- coding:utf8 -*-

"""
Function:
Convert mlf-TG files.

Usage:
python3 ./TG_mlf_conversion.py -i inputfile/folder -o outputfolder -l langtype -t mlf2tg/tg2mlf/mlf2tg_full/tg_full2mlf

For more information, please refer to TG_mlf_conversion说明.txt

Created by Dora XIA on 28th June 2017.
"""

import re
import sys
import copy
import os, os.path
import logging
from optparse import OptionParser
from unicodeops import UnicodeOps

#指定存放lhp-spt mapping文件以及phonemes文件的路径
mapping_path = "../database/mlfcheck/tools/raw-data"

class load_refs(object):
    """
    load lhp-spt mapping table等必要文件
    """
    def __init__(self, logger, langtype):
        self.logger = logger
        self.langtype = langtype

    def find_lhp2spt_mapping(self):
        """
        找到目标语言的lhp-spt对应表
        """
        if not os.path.isdir(mapping_path):
            logger.error("Cannot find the mapping tables! Should be in ../database/mlfcheck/tools/raw-data!")
            sys.exit(-1)
        puncfile = os.path.join(mapping_path, "punc.txt")
        plosive_file_enx = os.path.join(mapping_path, "ENU_phonemes.txt")
        if self.langtype == "mnx":
            lhp_spt_mapping = os.path.join(mapping_path, "ALL_PYT_to_SPT.txt")
            plosive_file = os.path.join(mapping_path, "MNC_phonemes.txt")
        elif self.langtype == "shc":
            lhp_spt_mapping = os.path.join(mapping_path, "ALL_LHP_to_SPT_shc.txt")
            plosive_file = os.path.join(mapping_path, "SHC_phonemes.txt")
        elif self.langtype == "sic":
            lhp_spt_mapping = os.path.join(mapping_path, "ALL_LHP_to_SPT_sic.txt")
            plosive_file = os.path.join(mapping_path, "SIC_phonemes.txt")
        elif self.langtype == "cah":
            lhp_spt_mapping = os.path.join(mapping_path, "ALL_YPT_to_SPT_cah.txt")
            plosive_file = os.path.join(mapping_path, "CAH_phonemes.txt")
        elif self.langtype == "enx":
            lhp_spt_mapping = None  # 英文的TG里直接用的是spt(且没有tone)而不是lhp,故不用转换
            plosive_file = None

        return lhp_spt_mapping, plosive_file, plosive_file_enx, puncfile

    def load_lhp2spt_mapping(self):
        """
        读取lhp-spt对应表，存在一个dictionary里，key为lhp, value为spt;
        读取phonemes table,存储爆破音信息
        """
        lhp_spt_mapping, plosive_file, plosive_file_enx, puncfile = self.find_lhp2spt_mapping()
        lhp2spt_table = {}
        spt2lhp_table = {}
        plosive_table = {}
        plosive_table_enx = {}
        phonemes = []
        phonemes_enx = []
        if self.langtype != "enx":
            try:
                # print(lhp_spt_mapping)
                with open(lhp_spt_mapping, "r", encoding="utf-8") as f1:
                    for line in f1:
                        lhp, spt = line.strip().split("\t")
                        if lhp not in lhp2spt_table:
                            lhp2spt_table[lhp] = spt
                        if spt not in spt2lhp_table:
                            spt2lhp_table[spt] = lhp
                with open(plosive_file, "r", encoding="cp437") as f2:
                    for line in f2:
                        try:
                            phoneme, whether_plosive, whether_voiceless = line.strip().split("\t") #目前只用到是否是爆破音；先不管是否voiced
                            plosive_table[phoneme] = whether_plosive
                            phonemes.append(phoneme)
                        except:  # 忽略文件最上面那些header
                            pass
            except:
                self.logger.error("Cannot find the lhp2spt table/ the phonemes table! Or you didn't use Python3!")
                sys.exit(-1)
        else:  # 如果是英文，则忽略。因为下面还会load英文的
            pass

        # load英文的
        try:
            with open(plosive_file_enx, "r", encoding="cp437") as f2:
                for line in f2:
                    try:
                        phoneme, whether_plosive = line.strip().split("\t")
                        plosive_table_enx[phoneme] = whether_plosive
                        phonemes_enx.append(phoneme)
                    except:  # 忽略文件最上面那些header
                        pass
        except:
            self.logger.error("Cannot find ENX_phonemes.txt!")
            sys.exit(-1)
        return lhp2spt_table, spt2lhp_table, plosive_table, plosive_table_enx, phonemes, phonemes_enx, puncfile



"""
把mlf转换成TG。有两种选择:
mlf2tg_full: 11层的TG：文本，汉字，拼音，音素，半音素，韵律边界，句重音，语言，语气，风格，词重音。
mlf2tg:       7层的TG: 文本，汉字，拼音，韵律边界，词重音，语言，语气。
"""
class mlf2tg(object):
    def __init__(self, logger, langtype, mlf_file):
        self.logger = logger
        self.langtype = langtype
        self.mlf_file = mlf_file

    def mlf2tg_format(self):
        """
        把mlf格式的信息转成TG格式：汉字，拼音，音素，半音素，韵律边界，句重音，语言，语气，风格，词重音都是list，包含每个元素的开始时间

        比如 characters = [[字1,开始,结尾],[字2，开始,结尾]...]
        最后处理得到的信息存在 mlf2tg_info这个字典里
        """
        mlf2tg_info = {}
        characters = []
        spt = []
        lhp = []
        prosody = []
        stress = []
        focus = []
        language = []
        manner = []
        manner_dct = {}
        phonemes = []
        semi_phonemes = []
        cur_spt = ""
        cur_tone = ""
        process = mlfParse(logger,self.langtype)
        mlfInfo = process.compare_spts(self.mlf_file)
        cur_manner = mlfInfo["manner"]
        duration = float(mlfInfo["duration"])/1000
        script = [mlfInfo["script"], 0, duration]
        chars = process.GetCharList(mlfInfo["script"]) #尚未加上时间信息
        all_info = mlfInfo["all_info"]
        prosody.append(["4",all_info[0][0][0][0][1][1]]) #把最初的四级边界加进来


        #每种信息分开处理，免得互相影响出错（缺点是要增加几个loop)

        #韵律边界
        try:
            for i in range(len(all_info)): #三级边界
                if i > 0:
                    prosody.append(["3", all_info[i][0][0][0][0][1]])
                    prosody.append(["3", all_info[i][0][0][0][1][1]]) #三级边界都是成对的
                for j in range(len(all_info[i])-1): # 二级边界
                    if j > 0:
                        prosody.append(["2", all_info[i][j][0][0][0][1]])
                    for k in range(len(all_info[i][j])):  # 韵律词
                        if k > 0:
                            prosody.append(["1", all_info[i][j][k][0][0][1]])
                        for l in range(len(all_info[i][j][k]) - 2):  # 字
                            if l > 0:
                                prosody.append(["0", all_info[i][j][k][l][0][1]])
        except:
            self.logger.error("韵律边界出错！")

        #句重音
        try:
            for i in range(len(all_info)):  # 三级边界
                for j in range(len(all_info[i]) - 1):  # 二级边界
                    for k in range(len(all_info[i][j])):  # 韵律词
                        if all_info[i][j][k][0][0][0] == "#":
                            focus.append([None, all_info[i][j][k][0][0][1]])
                            focus.append([all_info[i][j][k][-2], all_info[i][j][k][0][1][1]])
                            #manner.append(["None", all_info[i][j][k][0][0][1]])
                            #manner.append([all_info[i][j][k][-1], all_info[i][j][k][0][1][1]])
                        else:
                            focus.append([all_info[i][j][k][-2], all_info[i][j][k][0][0][1]])
                            #manner.append([all_info[i][j][k][-1], all_info[i][j][k][0][0][1]])
        except:
            self.logger.error("句重音出错！")

        #词重音和语言
        try:
            for i in range(len(all_info)):  # 三级边界
                for j in range(len(all_info[i]) - 1):  # 二级边界
                    for k in range(len(all_info[i][j])):  # 韵律词
                        for l in range(len(all_info[i][j][k]) - 2): #字
                            if all_info[i][j][k][l][0][0] == "#":
                                stress.append([None,all_info[i][j][k][l][0][1]]) # 静音段
                                stress.append([all_info[i][j][k][l][-3], all_info[i][j][k][l][1][1]]) # 静音后面那段
                                language.append([None, all_info[i][j][k][l][0][1]])  # 静音段
                                language.append([all_info[i][j][k][l][-1], all_info[i][j][k][l][1][1]])  # 静音后面那段
                            else:
                                stress.append([all_info[i][j][k][l][-3], all_info[i][j][k][l][0][1]])
                                language.append([all_info[i][j][k][l][-1], all_info[i][j][k][l][0][1]])
        except:
            self.logger.error("词重音或语言出错！")

        #字（英文是词）
        #后面得到spt及时间信息再处理比较方便

        #spt(之后会转成lhp)
        try:
            for i in range(len(all_info)):  # 三级边界
                for j in range(len(all_info[i]) - 1):  # 二级边界
                    for k in range(len(all_info[i][j])):  # 韵律词
                        for l in range(len(all_info[i][j][k]) - 2): #字
                            #获取声调信息
                            if all_info[i][j][k][l][-2] == None:
                                cur_tone = ""
                            else:
                                cur_tone = all_info[i][j][k][l][-2]
                            #把spt连在一起
                            for o in range(len(all_info[i][j][k][l]) - 3):  # 音素
                                if all_info[i][j][k][l][o][0] == "#" and o != len(all_info[i][j][k][l]) - 4: #静音段也要加进来 但最后一个字要单独处理，因为#在最后
                                    cur_spt = "#"
                                    spt.append(cur_spt)
                                    cur_spt = ""
                                else:
                                    cur_spt += all_info[i][j][k][l][o][0] + cur_tone
                            if l != len(all_info[i][j][k])-3 and all_info[i][j][k][l][-1] == True: # 如果是英文，而且没到韵律词结尾，则用-连接spt，不分开
                                cur_spt += "-"
                            else:
                                if cur_spt != "":
                                    spt.append(cur_spt)
                                    cur_spt = ""
        except:
            self.logger.error("spt有问题！")


        #音素和半音素
        try:
            for i in range(len(all_info)):  # 三级边界
                for j in range(len(all_info[i]) - 1):  # 二级边界
                    for k in range(len(all_info[i][j])):  # 韵律词
                        for l in range(len(all_info[i][j][k]) - 2): # 字
                            for m in range(len(all_info[i][j][k][l])-3): # 音素
                                phonemes.append([all_info[i][j][k][l][m][0], all_info[i][j][k][l][m][1]])
                                semi_phonemes.append([all_info[i][j][k][l][m][0], all_info[i][j][k][l][m][1]]) # 前一个半音素
                                semi_phonemes.append([all_info[i][j][k][l][m][2], all_info[i][j][k][l][m][3]]) # 后一个半音素
        except:
            self.logger.error("音素或半音素出错！")

        #最后的sil和时间也要加进来
        prosody.append(["4", all_info[-1][-2][-1][-3][-4][1]]) # 把最后的4级边界加进来
        #characters.append(["#", all_info[-1][-2][-1][-3][-4][1]])
        language.append([None,all_info[-1][-2][-1][-3][-4][1]])
        stress.append([None,all_info[-1][-2][-1][-3][-4][1]])
        focus.append([None,all_info[-1][-2][-1][-3][-4][1]])
        #manner.append(["None",all_info[-1][-2][-1][-3][-4][1]])
        # 处理一下最后一个字的spt，不然#会跟在spt里
        last_spt, tone = spt[-1].split("#")
        spt[-1] = last_spt
        spt.append("#")

        # 把spt转成lhp，并加上时间信息
        try:
            lang_position = 0
            for i in range(len(spt)):
                if language[lang_position][0] == None:  # 是静音段
                    lhp.append(["#", language[lang_position][1]])
                    lang_position += 1
                elif language[lang_position][0] == False:  # 是中文
                    try:
                        cur_spt = spt[i]
                        cur_lhp = process.spt2lhp(cur_spt)
                        lhp.append([cur_lhp, language[lang_position][1]])
                        lang_position += 1
                    except:#是英文但没打tag的情况
                        lhp.append([spt[i], language[lang_position][1]])
                        lang_position += len(spt[i].split("-"))
                elif language[lang_position][0] == True:  # 是英文
                    lhp.append([spt[i], language[lang_position][1]])
                    lang_position += len(spt[i].split("-"))

        except:
            self.logger.error("Cannot convert spt to lhp!")
            sys.exit(-1)

        #根据lhp及时间信息得到字的时间信息

        try:
            char_position = 0
            for i in range(len(lhp)):
                if lhp[i][0] == "#":
                    characters.append(lhp[i])
                    char_position -= 1
                else:
                    characters.append([chars[char_position], lhp[i][1]])
                char_position += 1
        except:
            self.logger.error("汉字行与spt行有出入！")
            sys.exit(-1)

        # 加入语气信息(加在最后三个音节上）
        whether_sil = False #看是否有静音段
        if cur_manner == True:
            for i in range(len(prosody)-2, len(prosody)-5, -1):
                if prosody[i][0] != "3":
                    manner_dct[prosody[i][1]] = True
                    #manner.append([True, prosody[i][1]])
                elif prosody[i-1][0] != "3": #如果是静音段开头
                    manner_dct[prosody[i][1]] = None
                    #manner.append([None, prosody[i][1]])
                else: # 如果是静音段结尾
                    whether_sil = True
                    manner_dct[prosody[i][1]] = True
                    #manner.append([True, prosody[i][1]])
            if whether_sil == True and prosody[-5][0] != "3":
                manner_dct[prosody[-5][1]] = True
                #manner.append([True, prosody[-5][1]])


        # 加入剩下的语气信息
        manner.append([None, 0.0]) #开始的静音段

        for i in range(len(prosody) - 1):
            if prosody[i][1] in manner_dct:
                manner.append([manner_dct[prosody[i][1]], prosody[i][1]])
            else:
                if prosody[i][0] == "3" and prosody[i+1][0] == "3":
                    manner.append([None, prosody[i][1]])
                else:
                    manner.append([False, prosody[i][1]])


        manner.append([None, prosody[-1][1]]) #最后的静音段


        #合并静音段之间的相同的语言/语气风格信息：
        try:
            combined_lang = []
            cur_time = ""
            combined_lang.append(language[0]) #第一个静音段
            for a in range(1,len(language)):
                if language[a][0] == language[a-1][0]:
                    pass
                elif language[a][0] == None:
                    combined_lang.append([None, language[a][1]])
                else:
                    cur_time = language[a][1]
                    combined_lang.append([language[a][0], cur_time])

            combined_manner = []
            cur_time = ""
            combined_manner.append(manner[0])  # 第一个静音段
            for a in range(1, len(manner)):
                if manner[a][0] == manner[a - 1][0]:
                    pass
                elif manner[a][0] == None:
                    combined_manner.append(manner[a])
                else:
                    cur_time = manner[a][1]
                    combined_manner.append([manner[a][0], cur_time])

            combined_style = [] #现在只有一种风格：TN
            combined_style.append(combined_lang[0])
            for a in range(1, len(combined_lang)):
                if combined_lang[a][0] == None:
                    combined_style.append(combined_lang[a])
                elif combined_lang[a] == True:
                    pass
                elif combined_lang[a][0] == False and combined_lang[a-1][0] != False:
                    combined_style.append(combined_lang[a])
        except:
            self.logger.error("语言/风格出错！")
            sys.exit(-1)


        #把所有信息存到一个dictionary里
        mlf2tg_info["duration"] = duration
        mlf2tg_info["script"] = script
        mlf2tg_info["characters"] = characters
        mlf2tg_info["lhp"] = lhp
        mlf2tg_info["phonemes"] = phonemes
        mlf2tg_info["semi_phonemes"] = semi_phonemes
        mlf2tg_info["prosody"] = prosody
        mlf2tg_info["stress"] = stress
        mlf2tg_info["focus"] = focus
        mlf2tg_info["language"] = combined_lang
        mlf2tg_info["manner"] = combined_manner
        mlf2tg_info["style"] = combined_style

        return mlf2tg_info


    def write2tg_full(self, outputfile):
        mlfInfo = self.mlf2tg_format()
        duration = mlfInfo["duration"]
        script = mlfInfo["script"]

        mlf2tg_info = self.mlf2tg_format()
        with open(outputfile, "w", encoding="utf-8") as ptg:
            # 写入textgrid的文件头
            ptg.write("File type = \"ooTextFile\"\n")
            ptg.write("Object class = \"TextGrid\"\n\n")
            ptg.write("0\n")
            ptg.write("%f" % duration)
            ptg.write("\n")
            ptg.write("<exists>\n11\n")  # 共11层

            # 写入第一层，文本层
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"文本\"\n")
            ptg.write("0\n")
            ptg.write("%f" % duration)
            ptg.write("\n")
            ptg.write("1\n")
            ptg.write("0\n")
            ptg.write("%f" % duration)
            ptg.write("\n")
            #script = re.split(" ", mlfInfo["script"], 2)[2]
            script = re.sub("\"", "\"\"", script[0]) # 注意，在praat中，interval中如果有英文的双引号，那么就要再加一个双引号来表示，就像一般的\来取本义字符一样。
            # script = re.sub("\"", "\"\"", script.encode("utf8"))
            ptg.write("\"%s\"" % script)
            ptg.write("\n")

            #写入第二层，汉字层
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"汉字\"\n")
            ptg.write("0\n")
            ptg.write("%f" % duration)
            ptg.write("\n")
            ptg.write("%d\n" % (len(mlf2tg_info["characters"])))
            #逐个写入汉字 注意要把#替换成sil或者sp
            for i in range(len(mlf2tg_info["characters"])):
                if i == 0: #句首的静音段
                    ptg.write("%f" % round(mlf2tg_info["characters"][i][1]/1000, 6))
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["characters"][i + 1][1]/1000, 6))
                    ptg.write("\n")
                    ptg.write("\"sil\"" + "\n")
                elif i == len(mlf2tg_info["characters"])-1: #句末的静音段
                    ptg.write("%f" % round(mlf2tg_info["characters"][i][1]/1000, 6))
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)
                    ptg.write("\"sil\"" + "\n")
                elif mlf2tg_info["characters"][i][0] != "#": #正常的字
                    ptg.write("%f" % round(mlf2tg_info["characters"][i][1]/1000, 6)) #这个字的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["characters"][i+1][1]/1000, 6)) #结束时间
                    ptg.write("\n")
                    ptg.write("\"" + mlf2tg_info["characters"][i][0] + "\"" + "\n") #字
                else: #句中的静音段
                    ptg.write("%f" % round(mlf2tg_info["characters"][i][1]/1000, 6)) #sp的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["characters"][i+1][1]/1000, 6)) #结束时间
                    ptg.write("\n")
                    ptg.write("\"sp\"" + "\n")

            #写入第三层 拼音层
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"拼音\"\n")
            ptg.write("0\n")
            ptg.write("%f" % duration)
            ptg.write("\n")
            ptg.write("%d\n" % (len(mlf2tg_info["lhp"])))
            # 逐个写入lhp 注意要把#替换成sil或者sp
            for i in range(len(mlf2tg_info["lhp"])):
                if i == 0:  # 句首的静音段
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i][1]/1000, 6))
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i + 1][1]/1000, 6))
                    ptg.write("\n")
                    ptg.write("\"sil\"" + "\n")
                elif i == len(mlf2tg_info["lhp"]) -1:  # 句末的静音段
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i][1]/1000, 6))
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)
                    ptg.write("\"sil\"" + "\n")
                elif mlf2tg_info["lhp"][i][0] != "#":  # 正常的pinyin/lhp/spt
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i][1]/1000, 6))  # 这个字的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i + 1][1]/1000, 6))  # 结束时间
                    ptg.write("\n")
                    ptg.write("\"" + mlf2tg_info["lhp"][i][0] + "\"" + "\n")  # 字
                else:  # 句中的静音段
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i][1]/1000, 6))  # sp的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i + 1][1]/1000, 6))  # 结束时间
                    ptg.write("\n")
                    ptg.write("\"sp\"" + "\n")

            #写入第四层，音素层
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"音素\"\n")
            ptg.write("0\n")
            ptg.write("%f" % duration)
            ptg.write("\n")
            ptg.write("%d\n" % (len(mlf2tg_info["phonemes"])))
            # 逐个写入音素 注意要把#替换成sil或者sp
            for i in range(len(mlf2tg_info["phonemes"])):
                if i == 0:  # 句首的静音段
                    ptg.write("%f" % round(mlf2tg_info["phonemes"][i][1]/1000, 6))
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["phonemes"][i + 1][1]/1000, 6))
                    ptg.write("\n")
                    ptg.write("\"sil\"" + "\n")
                elif i == len(mlf2tg_info["phonemes"]) -1:  # 句末的静音段
                    ptg.write("%f" % round(mlf2tg_info["phonemes"][i][1]/1000, 6))
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)
                    ptg.write("\"sil\"" + "\n")
                elif mlf2tg_info["phonemes"][i][0] != "#":  # 正常的pinyin/lhp/spt
                    ptg.write("%f" % round(mlf2tg_info["phonemes"][i][1]/1000, 6))  # 这个字的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["phonemes"][i + 1][1]/1000, 6))  # 结束时间
                    ptg.write("\n")
                    ptg.write("\""+ mlf2tg_info["phonemes"][i][0] + "\""+ "\n")  # 字
                else:  # 句中的静音段
                    ptg.write("%f" % round(mlf2tg_info["phonemes"][i][1]/1000, 6))  # sp的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["phonemes"][i + 1][1]/1000, 6))  # 结束时间
                    ptg.write("\n")
                    ptg.write("\"sp\"" + "\n")

            #写入第五层，半音素层
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"半音素\"\n")
            ptg.write("0\n")
            ptg.write("%f" % duration)
            ptg.write("\n")
            ptg.write("%d\n" % (len(mlf2tg_info["semi_phonemes"])))
            # 逐个写入音素 注意要把#替换成sil或者sp
            for i in range(len(mlf2tg_info["semi_phonemes"])):
                if i in [0, 1, len(mlf2tg_info["semi_phonemes"])-2]:  # 句首的静音段或句末的前半个静音段
                    ptg.write("%f" % round(mlf2tg_info["semi_phonemes"][i][1]/1000, 6))
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["semi_phonemes"][i + 1][1]/1000, 6))
                    ptg.write("\n")
                    ptg.write("\"sil\"" + "\n")
                elif i == len(mlf2tg_info["semi_phonemes"])-1:  # 句末的第二个静音段
                    ptg.write("%f" % round(mlf2tg_info["semi_phonemes"][i][1]/1000, 6))
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)
                    ptg.write("\"sil\"" + "\n")
                elif mlf2tg_info["semi_phonemes"][i][0] != "#":  # 正常的pinyin/lhp/spt
                    ptg.write("%f" % round(mlf2tg_info["semi_phonemes"][i][1]/1000, 6))  # 这个字的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["semi_phonemes"][i + 1][1]/1000, 6))  # 结束时间
                    ptg.write("\n")
                    ptg.write("\"" + mlf2tg_info["semi_phonemes"][i][0] + "\"" + "\n")  # 字
                else:  # 句中的静音段
                    ptg.write("%f" % round(mlf2tg_info["semi_phonemes"][i][1]/1000, 6))  # sp的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["semi_phonemes"][i + 1][1]/1000, 6))  # 结束时间
                    ptg.write("\n")
                    ptg.write("\"sp\"" + "\n")

            #写入第六层，韵律边界层
            ptg.write("\"TextTier\"\n")
            ptg.write("\"韵律边界\"\n")
            ptg.write("0\n%f\n" % duration)
            ptg.write("%d\n" % (len(mlf2tg_info["prosody"])))
            #逐个写入韵律边界
            for i in range(len(mlf2tg_info["prosody"])):
                ptg.write("%f" % round(mlf2tg_info["prosody"][i][1]/1000, 6)) #时间
                ptg.write("\n")
                ptg.write("\"" + mlf2tg_info["prosody"][i][0] + "\"\n") #韵律边界 （注意是否有“”）

            #写入第七层，句重音层
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"句重音\"\n")
            ptg.write("0\n%f\n" % duration)
            ptg.write("%d\n" % (len(mlf2tg_info["focus"])))
            #逐个写入句重音: False转写成0，True转写成1
            for i in range(len(mlf2tg_info["focus"])):
                if i == len(mlf2tg_info["focus"]) -1: #最后静音段
                    ptg.write("%f" % round(mlf2tg_info["focus"][i][1]/1000, 6))  # sil的开始时间
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)  # 结束时间
                    ptg.write("\"None\"" + "\n")
                else:
                    ptg.write("%f" % round(mlf2tg_info["focus"][i][1]/1000, 6))  # 这个句重音的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["focus"][i + 1][1]/1000, 6))  # 结束时间
                    ptg.write("\n")
                    if mlf2tg_info["focus"][i][0] == True:
                        ptg.write("\"1\"" + "\n")
                    elif mlf2tg_info["focus"][i][0] == False:
                        ptg.write("\"0\"" + "\n")
                    elif mlf2tg_info["focus"][i][0] == None:
                        ptg.write("\"None\"" + "\n")

            #写入第八层，语言层。如果中间没有静音段，相同的语言标记要合并。MNC：TC； ENX:TE； SHC: TSH； SIC:TCD；CAH: TCH
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"语言\"\n")
            ptg.write("0\n%f\n" % duration)
            ptg.write("%d\n" % (len(mlf2tg_info["language"])))
            if self.langtype == "enx":
                cur_lang = "TE"
            elif self.langtype == "mnx":
                cur_lang = "TC"
            elif self.langtype == "shc":
                cur_lang = "TSH"
            elif self.langtype == "sic":
                cur_lang = "TCD"
            elif self.langtype == "cah":
                cur_lang  = "TCH"
            #逐个写入语言信息
            for i in range(len(mlf2tg_info["language"])):
                if i == len(mlf2tg_info["language"]) - 1:  # 最后静音段
                    ptg.write("%f" % round(mlf2tg_info["language"][i][1]/1000, 6))  # sil的开始时间
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)  # 结束时间
                    ptg.write("\"None\"" + "\n")
                else:
                    ptg.write("%f" % round(mlf2tg_info["language"][i][1]/1000, 6))  # 这个lang的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["language"][i + 1][1]/1000, 6))  # 结束时间
                    ptg.write("\n")
                    if mlf2tg_info["language"][i][0] == True:
                        ptg.write("\"TE\"" + "\n")
                    elif mlf2tg_info["language"][i][0] == False:
                        ptg.write("\"" + cur_lang + "\"" + "\n")
                    elif mlf2tg_info["language"][i][0] == None:
                        ptg.write("\"None\"" + "\n")

            #写入第九层，语气层。False改写为TS, True改写为TQ
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"语气\"\n")
            ptg.write("0\n%f\n" % duration)
            ptg.write("%d\n" % (len(mlf2tg_info["manner"])))
            # 逐个写入语气信息
            for i in range(len(mlf2tg_info["manner"])):
                if i == len(mlf2tg_info["manner"]) -1:  # 最后静音段
                    ptg.write("%f" % round(mlf2tg_info["manner"][i][1]/1000, 6))  # sil的开始时间
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)  # 结束时间
                    ptg.write("\"None\"" + "\n")
                else:
                    ptg.write("%f" % round(mlf2tg_info["manner"][i][1]/1000, 6))  # 这个manner的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["manner"][i + 1][1]/1000, 6))  # 结束时间
                    ptg.write("\n")
                    if mlf2tg_info["manner"][i][0] == True:
                        ptg.write("\"TQ\"" + "\n")
                    elif mlf2tg_info["manner"][i][0] == False:
                        ptg.write("\"TS\"" + "\n")
                    elif mlf2tg_info["manner"][i][0] == None:
                        ptg.write("\"None\"" + "\n")

            #写入第十层，风格层。现在均为TN。
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"风格\"\n")
            ptg.write("0\n%f\n" % duration)
            ptg.write("%d\n" % (len(mlf2tg_info["style"])))
            # 逐个写入风格信息
            for i in range(len(mlf2tg_info["style"])):
                if i == len(mlf2tg_info["style"]) - 1:  # 最后静音段
                    ptg.write("%f" % round(mlf2tg_info["style"][i][1]/1000, 6))  # sil的开始时间
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)  # 结束时间
                    ptg.write("\"None\"" + "\n")
                else:
                    ptg.write("%f" % round(mlf2tg_info["style"][i][1]/1000, 6))  # 这个style的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["style"][i + 1][1]/1000, 6))  # 结束时间
                    ptg.write("\n")
                    if mlf2tg_info["style"][i][0] == None:
                        ptg.write("\"None\"" + "\n")
                    else:
                        ptg.write("\"TN\"" + "\n")

            #写入第十一层，词重音层。
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"词重音\"\n")
            ptg.write("0\n%f\n" % duration)
            ptg.write("%d\n" % (len(mlf2tg_info["stress"])))
            # 逐个写入词重音: False转写成0，True转写成1
            for i in range(len(mlf2tg_info["stress"])):
                if i == len(mlf2tg_info["stress"]) -1:  # 最后静音段
                    ptg.write("%f" % round(mlf2tg_info["stress"][i][1]/1000, 6))  # sil的开始时间
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)  # 结束时间
                    ptg.write("\"None\"" + "\n")
                else:
                    ptg.write("%f" % round(mlf2tg_info["stress"][i][1]/1000, 6))  # 这个词重音的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["stress"][i + 1][1]/1000, 6))  # 结束时间
                    ptg.write("\n")
                    if mlf2tg_info["stress"][i][0] == True:
                        ptg.write("\"1\"" + "\n")
                    elif mlf2tg_info["stress"][i][0] == False:
                        ptg.write("\"0\"" + "\n")
                    elif mlf2tg_info["stress"][i][0] == None:
                        ptg.write("\"None\"" + "\n")

    def write2tg_less(self, outputfile):
        #七层TG： 文本，汉字，拼音，韵律边界，词重音，语言，语气
        mlfInfo = self.mlf2tg_format()
        # duration = float(mlfInfo["duration"]) / 1000
        duration = mlfInfo["duration"]
        script = mlfInfo["script"]

        mlf2tg_info = self.mlf2tg_format()
        with open(outputfile, "w", encoding="utf-8") as ptg:
            # 写入textgrid的文件头
            ptg.write("File type = \"ooTextFile\"\n")
            ptg.write("Object class = \"TextGrid\"\n\n")
            ptg.write("0\n")
            ptg.write("%f" % duration)
            ptg.write("\n")
            ptg.write("<exists>\n7\n")  # 共7层

            # 写入第一层，文本层
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"文本\"\n")
            ptg.write("0\n")
            ptg.write("%f" % duration)
            ptg.write("\n")
            ptg.write("1\n")
            ptg.write("0\n")
            ptg.write("%f" % duration)
            ptg.write("\n")
            # script = re.split(" ", mlfInfo["script"], 2)[2]
            script = re.sub("\"", "\"\"",
                            script[0])  # 注意，在praat中，interval中如果有英文的双引号，那么就要再加一个双引号来表示，就像一般的\来取本义字符一样。
            # script = re.sub("\"", "\"\"", script.encode("utf8"))
            ptg.write("\"%s\"" % script)
            ptg.write("\n")

            # 写入第二层，汉字层
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"汉字\"\n")
            ptg.write("0\n")
            ptg.write("%f" % duration)
            ptg.write("\n")
            ptg.write("%d\n" % (len(mlf2tg_info["characters"])))
            # 逐个写入汉字 注意要把#替换成sil或者sp
            for i in range(len(mlf2tg_info["characters"])):
                if i == 0:  # 句首的静音段
                    ptg.write("%f" % round(mlf2tg_info["characters"][i][1] / 1000, 6))
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["characters"][i + 1][1] / 1000, 6))
                    ptg.write("\n")
                    ptg.write("\"sil\"" + "\n")
                elif i == len(mlf2tg_info["characters"]) - 1:  # 句末的静音段
                    ptg.write("%f" % round(mlf2tg_info["characters"][i][1] / 1000, 6))
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)
                    ptg.write("\"sil\"" + "\n")
                elif mlf2tg_info["characters"][i][0] != "#":  # 正常的字
                    ptg.write("%f" % round(mlf2tg_info["characters"][i][1] / 1000, 6))  # 这个字的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["characters"][i + 1][1] / 1000, 6))  # 结束时间
                    ptg.write("\n")
                    ptg.write("\"" + mlf2tg_info["characters"][i][0] + "\"" + "\n")  # 字
                else:  # 句中的静音段
                    ptg.write("%f" % round(mlf2tg_info["characters"][i][1] / 1000, 6))  # sp的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["characters"][i + 1][1] / 1000, 6))  # 结束时间
                    ptg.write("\n")
                    ptg.write("\"sp\"" + "\n")

            # 写入第三层 拼音层
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"拼音\"\n")
            ptg.write("0\n")
            ptg.write("%f" % duration)
            ptg.write("\n")
            ptg.write("%d\n" % (len(mlf2tg_info["lhp"])))
            # 逐个写入lhp 注意要把#替换成sil或者sp
            for i in range(len(mlf2tg_info["lhp"])):
                if i == 0:  # 句首的静音段
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i][1] / 1000, 6))
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i + 1][1] / 1000, 6))
                    ptg.write("\n")
                    ptg.write("\"sil\"" + "\n")
                elif i == len(mlf2tg_info["lhp"]) - 1:  # 句末的静音段
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i][1] / 1000, 6))
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)
                    ptg.write("\"sil\"" + "\n")
                elif mlf2tg_info["lhp"][i][0] != "#":  # 正常的pinyin/lhp/spt
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i][1] / 1000, 6))  # 这个字的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i + 1][1] / 1000, 6))  # 结束时间
                    ptg.write("\n")
                    ptg.write("\"" + mlf2tg_info["lhp"][i][0] + "\"" + "\n")  # 字
                else:  # 句中的静音段
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i][1] / 1000, 6))  # sp的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["lhp"][i + 1][1] / 1000, 6))  # 结束时间
                    ptg.write("\n")
                    ptg.write("\"sp\"" + "\n")

            # 写入第四层，韵律边界层
            ptg.write("\"TextTier\"\n")
            ptg.write("\"韵律边界\"\n")
            ptg.write("0\n%f\n" % duration)
            ptg.write("%d\n" % (len(mlf2tg_info["prosody"])))
            # 逐个写入韵律边界
            for i in range(len(mlf2tg_info["prosody"])):
                ptg.write("%f" % round(mlf2tg_info["prosody"][i][1] / 1000, 6))  # 时间
                ptg.write("\n")
                ptg.write("\"" + mlf2tg_info["prosody"][i][0] + "\"\n")  # 韵律边界 （注意是否有“”）


            # 写入第五层，词重音层。
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"词重音\"\n")
            ptg.write("0\n%f\n" % duration)
            ptg.write("%d\n" % (len(mlf2tg_info["stress"])))
            # 逐个写入词重音: False转写成0，True转写成1
            for i in range(len(mlf2tg_info["stress"])):
                if i == len(mlf2tg_info["stress"]) - 1:  # 最后静音段
                    ptg.write("%f" % round(mlf2tg_info["stress"][i][1] / 1000, 6))  # sil的开始时间
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)  # 结束时间
                    ptg.write("\"None\"" + "\n")
                else:
                    ptg.write("%f" % round(mlf2tg_info["stress"][i][1] / 1000, 6))  # 这个词重音的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["stress"][i + 1][1] / 1000, 6))  # 结束时间
                    ptg.write("\n")
                    if mlf2tg_info["stress"][i][0] == True:
                        ptg.write("\"1\"" + "\n")
                    elif mlf2tg_info["stress"][i][0] == False:
                        ptg.write("\"0\"" + "\n")
                    elif mlf2tg_info["stress"][i][0] == None:
                        ptg.write("\"None\"" + "\n")

            # 写入第六层，语言层。如果中间没有静音段，相同的语言标记要合并。MNC：TC； ENX:TE； SHC: TSH； SIC:TCD；CAH: TCH
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"语言\"\n")
            ptg.write("0\n%f\n" % duration)
            ptg.write("%d\n" % (len(mlf2tg_info["language"])))
            if self.langtype == "enx":
                cur_lang = "TE"
            elif self.langtype == "mnx":
                cur_lang = "TC"
            elif self.langtype == "shc":
                cur_lang = "TSH"
            elif self.langtype == "sic":
                cur_lang = "TCD"
            elif self.langtype == "cah":
                cur_lang = "TCH"
            # 逐个写入语言信息
            for i in range(len(mlf2tg_info["language"])):
                if i == len(mlf2tg_info["language"]) - 1:  # 最后静音段
                    ptg.write("%f" % round(mlf2tg_info["language"][i][1] / 1000, 6))  # sil的开始时间
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)  # 结束时间
                    ptg.write("\"None\"" + "\n")
                else:
                    ptg.write("%f" % round(mlf2tg_info["language"][i][1] / 1000, 6))  # 这个lang的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["language"][i + 1][1] / 1000, 6))  # 结束时间
                    ptg.write("\n")
                    if mlf2tg_info["language"][i][0] == True:
                        ptg.write("\"TE\"" + "\n")
                    elif mlf2tg_info["language"][i][0] == False:
                        ptg.write("\"" + cur_lang + "\"" + "\n")
                    elif mlf2tg_info["language"][i][0] == None:
                        ptg.write("\"None\"" + "\n")

            # 写入第七层，语气层。False改写为TS, True改写为TQ
            ptg.write("\"IntervalTier\"\n")
            ptg.write("\"语气\"\n")
            ptg.write("0\n%f\n" % duration)
            ptg.write("%d\n" % (len(mlf2tg_info["manner"])))
            # 逐个写入语气信息
            for i in range(len(mlf2tg_info["manner"])):
                if i == len(mlf2tg_info["manner"]) - 1:  # 最后静音段
                    ptg.write("%f" % round(mlf2tg_info["manner"][i][1] / 1000, 6))  # sil的开始时间
                    ptg.write("\n")
                    ptg.write("%f\n" % duration)  # 结束时间
                    ptg.write("\"None\"" + "\n")
                else:
                    ptg.write("%f" % round(mlf2tg_info["manner"][i][1] / 1000, 6))  # 这个manner的开始时间
                    ptg.write("\n")
                    ptg.write("%f" % round(mlf2tg_info["manner"][i + 1][1] / 1000, 6))  # 结束时间
                    ptg.write("\n")
                    if mlf2tg_info["manner"][i][0] == True:
                        ptg.write("\"TQ\"" + "\n")
                    elif mlf2tg_info["manner"][i][0] == False:
                        ptg.write("\"TS\"" + "\n")
                    elif mlf2tg_info["manner"][i][0] == None:
                        ptg.write("\"None\"" + "\n")




"""
Parse a mlf file. Modified from Mei Xiao's mlfParse.py
  self.mlfInfo: it stores all the information in the mlf file
       1) self.mlfInfo[version]: store the version of mlf format
       2) self.mlfInfo[script]: store the script of the recording
       3) self.mlfInfo[duration]: store the whole duration of the recording
       4) self.mlfInfo[phonemes]: store the whole phonemes' information in the format of a prosodic tree
       5) self.mlfInfo[demiphones]: store the whole phonemes' information in a list
            self.mlfInfo[demiphones] 结构如下：
            1.韵4层 = [韵3, 韵3..] #
            2.韵3层 = [韵2，韵2,...风格] %#
            3.韵2层 = [韵1，韵1，...] %
            4.韵1层（韵律词）=[词，拼音/lhp/spt,句重音,语气] -*
            5.字（音节)层 = [字，音素1，音素2，...,音调，词重音, 语言] -
            6.音素层 = [半音素1，半音素2，开始时间1,开始时间2]
"""
class mlfParse(object):
    def __init__(self, logger, langtype):
        self.logger = logger
        self.langtype = langtype
        refs = load_refs(logger, self.langtype)
        self.lhp2spt_table, self.spt2lhp_table, self.plosive_table, self.plosive_table_enx, self.phonemes, self.phonemes_enx, self.puncfile = refs.load_lhp2spt_mapping()

    def spt2lhp(self, spt):
        #把spt转成lhp
        lhp = self.spt2lhp_table[spt]
        return lhp

    def lhp2spt(self, lhp):
        #把lhp转成spt
        try:
            spt = self.lhp2spt_table[lhp]
        except:
            self.logger.error("%s is not a valid lhp in %s!" % (lhp, self.langtype))
            spt = ""
        return spt

    def GetCharList(self, script):
        """
        得到脚本中的中文汉字和英文单词组成的串，比如“这是final week”被转成['这','是','final', 'week']
        首先把中英文分开，然后分别计算
        note: I'm xxx. "i'm" is one word
        match cases: [alphabet] + "'" + "[A-Za-z]" (除了常用简写，rock'n'roll O'Connor这样的也是一个词)
        instances: 'm , 've , 'd, 'l, 's, s' , 're, 't, o'clock
        另外用破折号连接的词也分成两个，和"'"处理相同
        """
        self.uniops = UnicodeOps(self.logger, self.puncfile)
        numberpat = self.uniops.getNumbers()
        puncs = self.uniops.getAllPuncs()
        alphabetpat = self.uniops.getAlphabets()
        charlist = []
        enxchars = ""

        for ichar in range(len(script)):
            # query next char and the previous char
            if ichar == 0:
                prechar = None
            else:
                prechar = script[ichar - 1]
            if ichar == len(script) - 1:
                nextchar = None
            else:
                nextchar = script[ichar + 1]
            # 如果当前char是数字，请回去先把脚本修改了再做
            if re.match(numberpat, script[ichar]):
                self.logger.error("numbers found in the script!")
            # 如果是中文字符
            elif self.uniops.isChinese(script[ichar]):
                # 先把英语加上去
                if enxchars != "":
                    charlist.append(enxchars)
                    enxchars = ""
                charlist.append(script[ichar])
            # 如果是标点，请继续，不过要先把英文单词存进去
            # 注意英文单引号，I'm的情况
            elif script[ichar] in puncs:
                if script[ichar] in ["'", "’"]:
                    if re.match("[a-zA-Z]", prechar) and re.match("[A-Za-z]", nextchar):
                        enxchars += "'"
                    elif prechar == "s" and nextchar == " ":
                        enxchars += "'"
                    else:
                        if enxchars != "":
                            charlist.append(enxchars)
                            enxchars = ""
                else:
                    if enxchars != "":
                        charlist.append(enxchars)
                        enxchars = ""
            # 如果是字母，就放到tmp中
            elif re.match(alphabetpat, script[ichar]):
                enxchars += script[ichar]
            # 如果是空格等，把英语添加进去，然后继续
            elif re.match(r"[ \t]", script[ichar]):
                if enxchars != "":
                    charlist.append(enxchars)
                    enxchars = ""
        # 如果最后一个是英语单词
        if enxchars != "":
            charlist.append(enxchars)
            enxchars = ""
        return charlist


    def parse_below(self, mlf_file):
        #parse mlf文件spt行下面那些行的信息
        mlfInfo = {}
        line_position = 0
        cur_semi = "" #此行的半音素
        pre_semi = "" # 上一行的半音素
        pre_semi_2 = "" #上上行的半音素
        pre_semi_3 = "" #上上上行的半音素
        pre_start_time = None

        start_time = None
        cur_stress = False #词重音
        cur_focus = False #句重音
        cur_tone = None #音调
        cur_lang = False # 语言 若为True则是TE（英语）
        cur_manner = False #语气 陈述为TS，疑问为TQ (TQ加在最后三个音节上；有的mlf里只有TQ开始标记，没有结尾标记。目前的处理是一旦看到TQ开始标记，就在最后三个音节加TQ）
        cur_style = False #风格 在现在版本里的mlf里没有，默认为TN


        phoneme = [] #第6层
        character = [] #零级边界（第5层）
        word = [] #一级边界（第4层）
        bnd_small = [] #二级边界（第3层）
        bnd_big = [] #三级边界（第2层）
        bnd_script = [] #四级边界（第1层）
        print(mlf_file)
        with open(mlf_file,"r", encoding="cp437") as f1:
            for line in f1:
                line = line.strip()
                line_position += 1

                #存储version,script,spt,duration信息
                if "*** mlf" in line:
                    version = line.split(": ")[1]
                elif "*** txt" in line:
                    script = line.split("txt: ")[1]
                    fn = open(os.path.join(r"D:\Documents\PRM\selected-tiantian\sent", os.path.basename(mlf_file)[:-3]+"sent"), 'w', encoding="utf-8")
                    fn.write("%s\n"%(script.encode('cp437').decode('gbk')))
                    fn.close()
                elif "*** spt" in line: # 之后再parse spt line，并和下面的信息对比看是否有出入
                    spt = line.split(": ")[1]
                elif "*** msec" in line:
                    duration = line.split(": ")[1]

                #存储下面行的信息
                elif line_position >= 6:
                    try:
                        cur_semi, start_time, whether_processed = line.split("    ")
                        start_time = float(start_time)
                    except:# 可能是tone或者韵律边界/重音/TQ tag等
                        cur_semi = line
                    if cur_semi == pre_semi or cur_semi == pre_semi + "!":
                        phoneme = [pre_semi, pre_start_time, cur_semi, start_time] # 6. 音素层
                        character.append(phoneme)

                    elif cur_semi in ["0","1","2","3","4","5","6","7","8","9"]: #音调
                        cur_tone = cur_semi
                    elif cur_semi == "\"": #词重音
                        cur_stress = True
                    elif cur_semi == "\\TE\\": #判断是否是英语
                        cur_lang = True
                    elif cur_semi == "\\/TE\\": #把英语关掉
                        cur_lang = False
                    elif cur_semi == ".0": #句重音为0
                        cur_focus = False
                    elif cur_semi == ".1": #句重音为1
                        cur_focus = True
                    elif cur_semi == "\\TQ\\": #判断是否是疑问语气
                        cur_manner = True
                    #elif cur_semi == "\\/TQ\\":
                    #    cur_manner = False
                    elif cur_semi == "-": #读到零级边界，存储之前的第6层信息,归零
                        character.append(cur_stress)
                        character.append(cur_tone)
                        if pre_semi == "\\/TE\\":
                            character.append(True)
                        else:
                            character.append(cur_lang)
                        word.append(character)
                        character = []
                        cur_stress = False
                        cur_tone = None
                        #cur_lang = False
                    elif cur_semi == "-*": #读到一级边界，存储之前的第5层信息，归零
                        character.append(cur_stress)
                        character.append(cur_tone)
                        if pre_semi == "\\/TE\\":
                            character.append(True)
                        else:
                            character.append(cur_lang)
                        word.append(character)
                        word.append(cur_focus)
                        #if pre_semi == "\\/TQ\\" or pre_semi_2 == "\\/TQ\\":
                        #    word.append(True)
                        #else:
                        #    word.append(cur_manner)
                        word.append(False) #语气信息先标成False。再根据真的语气信息改
                        bnd_small.append(word)


                        word = []
                        character = []
                        cur_focus = False
                        #cur_manner = False
                        cur_stress = False
                        cur_tone = None
                        #cur_lang = False #不对！\TE\W¡.0-*W|L.0-*⌐a.0\/TE\ 这样的中间的phoneme就没法被认为是TE了

                    elif cur_semi == "%": #读到二级边界，存储之前的第4层信息，归零
                        character.append(cur_stress)
                        character.append(cur_tone)
                        if pre_semi == "\\/TE\\":
                            character.append(True)
                        else:
                            character.append(cur_lang)
                        word.append(character)
                        word.append(cur_focus)
                        #if pre_semi == "\\/TQ\\" or pre_semi_2 == "\\/TQ\\":
                        #    word.append(True)
                        #else:
                        #    word.append(cur_manner)
                        word.append(False) #语气信息先标为False，再根据真正的语气信息改
                        bnd_small.append(word)
                        bnd_big.append(bnd_small)
                        bnd_small = []
                        word = []
                        character = []
                        cur_focus = False
                        #cur_manner = False
                        cur_stress = False
                        cur_tone = None
                        #cur_lang = False

                    elif cur_semi == "#" and pre_semi == "%": #读到三级边界，存储之前的第3层信息，归零。注意此时已经经过二级边界的处理
                        bnd_big.append(cur_style)
                        bnd_script.append(bnd_big)
                        bnd_big = []
                        bnd_small = []
                        word = []
                        character = []
                        cur_focus = False
                        #cur_manner = False
                        cur_stress = False
                        cur_tone = None
                        #cur_lang = False #也有跨过三级边界的TE tag!
                    if cur_semi == "#" and pre_semi == "#" and pre_semi_2 != "%"and line_position >8: #读到四级边界，说明读完了 不一定！三级边界是% # #三行
                        character.append(cur_stress)
                        character.append(cur_tone)
                        if pre_semi_2 == "\\/TE\\" or pre_semi_3 == "\\/TE\\":
                            character.append(True)
                        else:
                            character.append(cur_lang)
                        word.append(character)
                        word.append(cur_focus)
                        #if pre_semi_2 == "\\/TQ\\" or pre_semi_3 == "\\/TQ\\":
                        #    word.append(True)
                        #else:
                        #    word.append(cur_manner)
                        word.append(False) #语气信息先标为False，再根据真正的语气信息改
                        bnd_small.append(word)
                        bnd_big.append(bnd_small)
                        bnd_big.append(cur_style)
                        bnd_script.append(bnd_big)

                    pre_semi_3 = pre_semi_2
                    pre_semi_2 = pre_semi
                    pre_semi = cur_semi
                    pre_start_time = start_time


        # 把信息都加到一个dictionary里
        mlfInfo["version"] = version
        mlfInfo["script"] = script.encode("cp437").decode("gbk")
        # print(script)
        # mlfInfo["script"] = script.decode("cp437")
        mlfInfo["spt"] = spt
        mlfInfo["duration"] = duration
        mlfInfo["all_info"] = bnd_script
        mlfInfo["manner"] = cur_manner #暂时先把语气信息单独加进来



        return mlfInfo

    def parse_above(self, mlf_file):
        """
        记录spt行的信息，以便等下和下面行信息对比是否一致。并检查是不是该语言的spt符号
        phonemes是此语言的spt符号的list; phonemes_enx是英文的
        """
        spt = self.parse_below(mlf_file)["spt"]
        cur_symbol = "" #现在的符号
        pre_symbol = "" # 上一个符号
        pre_symbol_2 = "" #上上个符号
        cur_stress = False #词重音
        cur_focus = False #句重音
        cur_tone = None #音调
        cur_lang = False # 语言 若为True则是TE（英语）
        #pre_lang = False #见到TE结束标记，这个还是TE，下一个才是非TE
        #pre_lang_2 = False
        cur_manner = False #语气 陈述为TS，疑问为TQ
        cur_style = False #风格 在现在版本里的mlf里没有，默认为TN

        phoneme = "" #第6层
        character = [] #零级边界（第5层）
        word = [] #一级边界（第4层）
        bnd_small = [] #二级边界（第3层）
        bnd_big = [] #三级边界（第2层）
        bnd_script = [] #四级边界（第1层）
        for i in range(len(spt)): # 逐个读取spt行信息
            cur_symbol = spt[i]
            if cur_symbol in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"] and pre_symbol != ".":  # 音调
                cur_tone = cur_symbol
            elif cur_symbol == "\"":  # 词重音
                cur_stress = True
            elif cur_symbol == "E" and pre_symbol == "T" and pre_symbol_2 =="\\":  # 判断是否是英语
                cur_lang = True
            elif cur_symbol == "E" and pre_symbol == "T" and pre_symbol_2 =="/": #英语tag是否已结束
                cur_lang = False
            elif cur_symbol == "T" and pre_symbol in ["\\", "/"] and spt[i+1] =="E":# 已判断是否是英语，这里忽略 (要注意把\TE\T这样后面一个作为spt的T排除）
                pass
            #elif cur_symbol == "T" and pre_symbol in ["\\", "/"] and pre_symbol_2 != "E":
            #    pass
            elif cur_symbol == "0" and pre_symbol == ".":  # 句重音为0
                cur_focus = False
            elif cur_symbol == "1" and pre_symbol == ".":  # 句重音为1
                cur_focus = True
            elif cur_symbol == "Q" and pre_symbol == "T" and pre_symbol_2 == "\\":  # 判断是否是疑问语气
                cur_manner = True
            #elif cur_symbol == "Q" and pre_symbol == "T" and pre_symbol_2 == "/": #疑问语气是否已结束
            #    cur_manner = False
            elif cur_symbol == "T" and pre_symbol in ["\\", "/"] and spt[i+1] =="Q":# 已判断是否是疑问语气，这里忽略 (要注意把\TQ\T这样后面一个作为spt的T排除）
                pass
            elif cur_symbol == "-":  # 读到零级边界，存储之前的第6层信息,归零
                character.append(cur_stress)
                character.append(cur_tone)
                if spt[i-5:i] == "\\/TE\\":
                    character.append(True)
                else:
                    character.append(cur_lang)
                word.append(character)
                character = []
                cur_stress = False
                cur_tone = None
                #cur_lang = False
            elif cur_symbol == "*" and pre_symbol == "-":  # 读到一级边界，存储之前的第5层信息，归零
                word.append(cur_focus)
                word.append(False) #语气先标为False，之后再根据实际情况改
                bnd_small.append(word)
                word = []
                character = []
                cur_focus = False
                #cur_manner = False
                cur_stress = False
                cur_tone = None
                #cur_lang = False

            elif cur_symbol == "%":  # 读到二级边界，存储之前的第4层信息，归零
                character.append(cur_stress)
                character.append(cur_tone)
                if spt[i-5:i] == "\\/TE\\":
                    character.append(True)
                else:
                    character.append(cur_lang)
                word.append(character)
                word.append(cur_focus)
                #if spt[i-5:i] == "\\/TQ\\":
                #    word.append(True)
                #else:
                #    word.append(cur_manner)
                word.append(False)  # 语气先标为False，之后再根据实际情况改
                bnd_small.append(word)
                bnd_big.append(bnd_small)
                bnd_small = []
                word = []
                character = []
                cur_focus = False
                #cur_manner = False
                cur_stress = False
                cur_tone = None
                #cur_lang = False

            elif cur_symbol == "#" and pre_symbol == "%":  # 读到三级边界，存储之前的第3层信息，归零。注意此时已经经过二级边界的处理
                bnd_big.append(cur_style)
                bnd_script.append(bnd_big)
                bnd_big = []
                bnd_small = []
                word = []
                character = []
                cur_focus = False
                #cur_manner = False
                cur_stress = False
                cur_tone = None
                #cur_lang = False #发现也有越过三级边界的TE tag!

            elif cur_symbol == "#" and pre_symbol not in ["%",""]:  # 读到四级边界，说明读完了
                character.append(cur_stress)
                character.append(cur_tone)
                if spt[i-5:i] == "\\/TE\\" or spt[i-10:i-5] == "\\/TE\\":
                    character.append(True)
                else:
                    character.append(cur_lang)
                word.append(character)
                word.append(cur_focus)
                #if spt[i-5:i] == "\\/TQ\\" or spt[i-10:i-5] == "\\/TQ\\":
                #    word.append(True)
                #else:
                #    word.append(cur_manner)
                word.append(False)  # 语气先标为False，之后再根据实际情况改
                bnd_small.append(word)
                bnd_big.append(bnd_small)
                bnd_big.append(cur_style)
                bnd_script.append(bnd_big)

            elif cur_symbol in [".","\\","/","#"]: #还可能是其他符号 比如重音/language tag的一部分
                pass

            elif cur_symbol in self.phonemes or cur_symbol in self.phonemes_enx:
                phoneme = cur_symbol # 6. 音素层
                character.append(phoneme)

            else:
                self.logger.error("%s in %s is not a valid spt symbol for this language! Encoding alright?" % (cur_symbol, os.path.basename(mlf_file)))
            pre_symbol_2 = pre_symbol
            pre_symbol = cur_symbol

        return bnd_script, cur_manner

    def compare_spts(self,mlf_file):
        """
        比较mlf里上面和下面的spt信息是否有出入
        """
        spt_below = self.parse_below(mlf_file)["all_info"]
        manner_below = self.parse_below(mlf_file)["manner"]
        spt_above, manner_above = self.parse_above(mlf_file)

        if manner_below != manner_above:
            self.logger.error("%s上下语气标注不符！ 上面是%，下面是%s" % (os.path.basename(mlf_file), manner_above, manner_below))
        for i in range(len(spt_above)): #每个i是三级边界
            bnd_big = spt_above[i]
            for j in range(len(bnd_big)-1): #每个j是二级边界。先忽略风格信息（因为现在风格都是TN）
                bnd_small = bnd_big[j]
                for k in range(len(bnd_small)): #每个k是韵律词
                    word = bnd_small[k]
                    chars, focus, manner = word[:-2], word[-2], word[-1]
                    if focus != spt_below[i][j][k][-2]:
                        self.logger.error("%s上下句重音标注不符！ 上面是%s，下面是%s" % (os.path.basename(mlf_file),focus,spt_below[i][j][k][-2]))
                    #if manner != spt_below[i][j][k][-1]:
                    #    self.logger.error("%s上下语气标注不符！ 上面是%s，下面是%s" % (os.path.basename(mlf_file), manner, spt_below[i][j][k][-1]))
                    for x in range(len(chars)): #每个x是每个字
                        phonemes, stress, tone, lang = chars[x][:-3], chars[x][-3], chars[x][-2], chars[x][-1]
                        if stress != spt_below[i][j][k][x][-3]:
                            self.logger.error("%s上下词重音标注不符！ 上面是%s，下面是%s" % (os.path.basename(mlf_file), stress, spt_below[i][j][k][x][-3]))
                        if tone != spt_below[i][j][k][x][-2]:
                            self.logger.error("%s上下音调标注不符！ 上面是%s，下面是%s" % (os.path.basename(mlf_file), tone, spt_below[i][j][k][x][-2]))
                        if lang != spt_below[i][j][k][x][-1]:
                            self.logger.error("%s上下语言标注不符！ 上面是%s，下面是%s" % (os.path.basename(mlf_file), lang, spt_below[i][j][k][x][-1]))
                        z = -1
                        for y in range(len(phonemes)): #每个y是每个音素
                            phoneme = phonemes[y]
                            z += 1
                            if spt_below[i][j][k][x][z][0] == "#": #下面的信息存储了#，上面的没有。所以看到#先忽略
                                z += 1
                            if phoneme != spt_below[i][j][k][x][z][0]:
                                self.logger.error("%s上下有音素不符！ 上面是%s, 下面是%s" % (os.path.basename(mlf_file), phoneme, spt_below[i][j][k][x][z][0]))
        return self.parse_below(mlf_file) #下面列的信息作为转成TG的input

class tg2mlf(object):
    def __init__(self, logger, langtype, actiontype, tg_file):
        self.logger = logger
        self.langtype = langtype
        self.actiontype = actiontype
        self.tg_file = tg_file
        self.mlf_parse = mlfParse(self.logger, self.langtype)
        refs = load_refs(logger, self.langtype)
        self.lhp2spt_table, self.spt2lhp_table, self.plosive_table, self.plosive_table_enx, self.phonemes, self.phonemes_enx, self.puncfile = refs.load_lhp2spt_mapping()

    def readTG_less(self):
        """
        读取一个7层的TextGrid文件，并存储每层信息。
        信息存在一个dictionary里，以开始时间为key,内容为value
        """

        tg_info = {}
        original_value = [None, None, None, None, None, None, None, None, None, None]  # 每个key对应的value都是长度为11的list，分别存储汉字，拼音，音素，半音素，韵律边界，句重音，语言，语气，风格，词重音
        line_number = 0
        flag_text = 0
        flag_character = 0
        flag_pinyin = 0
        flag_prosody = 0
        flag_stress = 0
        flag_language = 0
        flag_manner = 0

        with open(self.tg_file, "r", encoding="utf-8") as f1:
            for line in f1:
                line = line.strip("\n")
                line_number += 1
                # 先找到TextGrid是哪种格式（全都顶格写 or 有一层一层缩进）
                if line_number == 4:
                    if line == "0":
                        format = "simple"
                    elif "xmin" in line:
                        format = "complex"
                    else:
                        self.logger.error("%s: Wrong Format in the TG file!\n" % os.path.basename(self.tg_file))
                        break

                if line_number == 7 and "11" in line: #判断是否是7层的TG
                    self.logger.error("The TG has 11 instead of 7 tiers!")
                    sys.exit(-1)

                # 看读到了哪层信息
                if "\"文本\"" in line:
                    flag_text = 1

                if "\"汉字\"" in line:
                    flag_text = 0
                    flag_character = 1
                    character_line = line_number

                elif "\"拼音\"" in line:
                    flag_character = 0
                    flag_pinyin = 1
                    pinyin_line = line_number

                elif "\"韵律边界\"" in line:
                    flag_pinyin = 0
                    flag_prosody = 1
                    prosody_line = line_number

                elif "\"词重音\"" in line:
                    flag_prosody = 0
                    flag_stress = 1
                    stress_line = line_number

                elif "\"语言\"" in line:
                    flag_stress = 0
                    flag_language = 1
                    language_line = line_number

                elif "\"语气\"" in line:
                    flag_language = 0
                    flag_manner = 1
                    manner_line = line_number


                # 存储每一层信息
                # 两种格式的TextGrid要分开处理
                if line_number > 4:  # line4之前未判断是什么格式

                    # 简单格式的TG
                    if format == "simple":
                        if line_number == 5:  # 存储时长信息
                            duration = str(float(line) * 1000)
                        elif line_number == 15:  # 存储文本信息
                            script = line[1:-1]

                        if flag_character == 1:  # 存储汉字信息
                            if (line_number - character_line) % 3 == 1 and (line_number - character_line) >= 4:
                                cur_start_time = line
                            elif (line_number - character_line) % 3 == 0 and (line_number - character_line) >= 6:
                                cur_character = line[1:-1]
                                # tg_info[cur_start_time] = original_value #为何不行而下面的方法行？
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time] = [cur_character, None, None, None, None, None, None, None, None, None]

                        elif flag_pinyin == 1:  # 存储拼音信息
                            if (line_number - pinyin_line) % 3 == 1 and (line_number - pinyin_line) >= 4:
                                cur_start_time = line
                            elif (line_number - pinyin_line) % 3 == 0 and (line_number - pinyin_line) >= 6:
                                cur_pinyin = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                try:
                                    tg_info[cur_start_time][1] = cur_pinyin

                                except:
                                    self.logger.error("第%f秒拼音时间和其他信息未对齐！" % cur_start_time)
                                    sys.exit(-1)

                        elif flag_prosody == 1:  # 存储韵律边界信息
                            if (line_number - prosody_line) % 2 == 0 and (line_number - prosody_line) >= 4:
                                cur_start_time = line
                            elif (line_number - prosody_line) % 2 == 1 and (line_number - prosody_line) >= 5:
                                cur_prosody = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                if cur_start_time in tg_info:
                                    tg_info[cur_start_time][4] = cur_prosody
                                else:
                                    tg_info[cur_start_time] = [None, None, None, None, cur_prosody, None, None, None, None, None]

                        elif flag_stress == 1:  # 存储词重音信息
                            if (line_number - stress_line) % 3 == 1 and (line_number - stress_line) >= 4:
                                cur_start_time = line
                            elif (line_number - stress_line) % 3 == 0 and (line_number - stress_line) >= 6:
                                cur_stress = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                try:
                                    tg_info[cur_start_time][9] = cur_stress
                                except:
                                    self.logger.error("第%f秒词重音时间和其他信息未对齐！" % cur_start_time)
                                    sys.exit(-1)

                        elif flag_language == 1:  # 存储语言信息
                            if (line_number - language_line) % 3 == 1 and (line_number - language_line) >= 4:
                                cur_start_time = line
                            elif (line_number - language_line) % 3 == 0 and (line_number - language_line) >= 6:
                                cur_language = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                try:
                                    tg_info[cur_start_time][6] = cur_language
                                except:
                                    self.logger.error("第%f秒语言时间和其他信息未对齐！" % cur_start_time)
                                    sys.exit(-1)

                        elif flag_manner == 1:  # 存储语气信息
                            if (line_number - manner_line) % 3 == 1 and (line_number - manner_line) >= 4:
                                cur_start_time = line
                            elif (line_number - manner_line) % 3 == 0 and (line_number - manner_line) >= 6:
                                cur_manner = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                try:
                                    tg_info[cur_start_time][7] = cur_manner
                                except:
                                    self.logger.error("第%f秒语气时间和其他信息未对齐！" % cur_start_time)
                                    sys.exit(-1)


                    # 复杂信息的TG
                    elif format == "complex":
                        if line_number == 5:  # 存储时长信息
                            duration = line.split(" = ")[1]
                            duration = str(float(duration) * 1000)

                        if flag_text == 1 and "text = " in line:  # 存储文本信息
                            script = line.split(" = ")[1]
                            script = re.sub(r'[\s\"]', "", script)

                        elif flag_character == 1:  # 存储汉字信息
                            if (line_number - character_line) % 4 == 1 and (line_number - character_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - character_line) % 4 == 3 and (line_number - character_line) >= 7:
                                cur_character = line.split(" = ")[1]
                                cur_character = re.sub(r'[\s\"]', "", cur_character)
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time] = [cur_character, None, None, None, None, None, None, None, None,None]

                        elif flag_pinyin == 1:  # 存储拼音信息
                            if (line_number - pinyin_line) % 4 == 1 and (line_number - pinyin_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - pinyin_line) % 4 == 3 and (line_number - pinyin_line) >= 7:
                                cur_pinyin = line.split(" = ")[1]
                                cur_pinyin = re.sub(r'[\s\"]', "", cur_pinyin)
                                cur_start_time = round(float(cur_start_time), 6)
                                try:
                                    tg_info[cur_start_time][1] = cur_pinyin
                                except:
                                    self.logger.error("第%f秒拼音时间和其他信息未对齐！" % cur_start_time)
                                    sys.exit(-1)

                        elif flag_prosody == 1:  # 存储韵律边界信息
                            if (line_number - prosody_line) % 3 == 2 and (line_number - prosody_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - prosody_line) % 3 == 0 and (line_number - prosody_line) >= 6:
                                cur_prosody = line.split(" = ")[1]
                                cur_prosody = re.sub(r'[\s\"]', "", cur_prosody)
                                cur_start_time = round(float(cur_start_time), 6)
                                if cur_start_time in tg_info:
                                    tg_info[cur_start_time][4] = cur_prosody
                                else:
                                    tg_info[cur_start_time] = [None, None, None, None, cur_prosody, None, None, None, None, None]


                        elif flag_stress == 1:  # 存储词重音信息
                            if (line_number - stress_line) % 4 == 1 and (line_number - stress_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - stress_line) % 4 == 3 and (line_number - stress_line) >= 7:
                                cur_stress = line.split(" = ")[1]
                                cur_stress = re.sub(r'[\s\"]', "", cur_stress)
                                cur_start_time = round(float(cur_start_time), 6)
                                try:
                                    tg_info[cur_start_time][9] = cur_stress
                                except:
                                    self.logger.error("第%f秒词重音时间和其他信息未对齐！" % cur_start_time)
                                    sys.exit(-1)

                        elif flag_language == 1:  # 存储语言信息
                            if (line_number - language_line) % 4 == 1 and (line_number - language_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - language_line) % 4 == 3 and (line_number - language_line) >= 7:
                                cur_language = line.split(" = ")[1]
                                cur_language = re.sub(r'[\s\"]', "", cur_language)
                                cur_start_time = round(float(cur_start_time), 6)
                                try:
                                    tg_info[cur_start_time][6] = cur_language
                                except:
                                    self.logger.error("第%f秒语言时间和其他信息未对齐！" % cur_start_time)
                                    sys.exit(-1)

                        elif flag_manner == 1:  # 存储语气信息
                            if (line_number - manner_line) % 4 == 1 and (line_number - manner_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - manner_line) % 4 == 3 and (line_number - manner_line) >= 7:
                                cur_manner = line.split(" = ")[1]
                                cur_manner = re.sub(r'[\s\"]', "", cur_manner)
                                cur_start_time = round(float(cur_start_time), 6)
                                try:
                                    tg_info[cur_start_time][7] = cur_manner
                                except:
                                    self.logger.error("第%f秒语气时间和其他信息未对齐！" % cur_start_time)
                                    sys.exit(-1)


        # 把lhp/pinyin转成spt
        try:
            lang = False
            for key in tg_info:
                if tg_info[key][6] == "TE":
                    lang = True
                elif tg_info[key][6] in ["TC", "TSH", "TCH", "TCD"]:
                    lang = False
                if tg_info[key][0] != None:
                    if tg_info[key][0] in ["sil", "sp"]:  # 静音段
                        cur_spt = "#"
                        tg_info[key][3] = "#"
                    elif lang == True:  # 如果是英文则不变
                        cur_spt = tg_info[key][1]
                    elif lang == False:
                        cur_spt = self.mlf_parse.lhp2spt(tg_info[key][1])
                    tg_info[key][1] = cur_spt
        except:
            self.logger.error("Cannot convert lhp/pinyin to spt!")
            sys.exit(-1)

        # 根据时间信息升序
        tg_info_new = sorted(self.dict2list(tg_info), key=lambda x: x[0], reverse=False)

        # 添加句重音
        try:
            flag_prosody = 0
            focus = "0"
            for x in range(1,len(tg_info_new)):
                # 这个韵律词里至少有一个词重音为1时，句重音为1。否则为0
                if tg_info_new[x][1][4] in ["1","2","3","4"]:
                    if focus == "0" and flag_prosody != 0:
                        tg_info_new[flag_prosody][1][5] = "0"
                    if focus == "1":
                        tg_info_new[flag_prosody][1][5] = "1"
                    flag_prosody = x
                    focus = "0"

                if tg_info_new[x][1][9] == "1":
                    focus = "1"
        except:
            self.logger.error("无法正确生成句重音！")
            sys.exit(-1)


        #添加音素行和半音素行 时间信息均分
        try:
            cur_spt = None
            tg_info_dct = {} #先把tuple还原成dictionary
            for i in range(len(tg_info_new)):
                tg_info_dct[tg_info_new[i][0]] = tg_info_new[i][1]
            for i in range(len(tg_info_new)-1): #记得加上最后的一条
                if tg_info_new[i][1][0] != None: #英文多音节词只看第一个
                    if tg_info_new[i][1][1] != None:
                        cur_spt = tg_info_new[i][1][1]
                    each_spt = cur_spt.split("-")#有可能存在英文多音节词
                    for a in range(len(each_spt)):
                        cur_char_duration = tg_info_new[i+a+1][0] - tg_info_new[i+a][0] #每个字的时长
                        cur_spt_notone = re.findall(r'[^0-9]', each_spt[a])
                        cur_phoneme_duration = cur_char_duration/len(cur_spt_notone)
                        cur_semiphoneme_duration = cur_phoneme_duration / 2

                        #添加音素信息
                        for j in range(len(cur_spt_notone)):
                            cur_key = tg_info_new[i+a][0] + cur_phoneme_duration*j
                            if cur_key in tg_info_dct:
                                tg_info_dct[cur_key][2] = cur_spt_notone[j]
                            else:
                                tg_info_dct[cur_key] = [None, None, cur_spt_notone[j], None, None, None, None, None, None, None, None]
                        #添加半音素信息
                        for k in range(len(cur_spt_notone)):
                            cur_key_1 = tg_info_new[i+a][0] + cur_phoneme_duration*k
                            cur_key_2 = cur_key_1 + cur_semiphoneme_duration
                            if cur_spt_notone[k] in self.plosive_table:
                                if self.plosive_table[cur_spt_notone[k]] == "y":
                                    cur_semiphoneme = cur_spt_notone[k] + "!"
                                else:
                                    cur_semiphoneme = cur_spt_notone[k]
                            elif cur_spt_notone[k] in self.plosive_table_enx:
                                if self.plosive_table_enx[cur_spt_notone[k]] == "y":
                                    cur_semiphoneme = cur_spt_notone[k] + "!"
                                else:
                                    cur_semiphoneme = cur_spt_notone[k]
                            else:
                                cur_semiphoneme = cur_spt_notone[k]
                            tg_info_dct[cur_key_1][3] = cur_spt_notone[k] #加入前半个半音素
                            tg_info_dct[cur_key_2] = [None, None, None, cur_semiphoneme, None, None, None, None, None, None, None]

        except:
            self.logger.error("无法正确生成音素/半音素信息！")
            sys.exit(-1)

        #加入最后的静音段
        tg_info_dct[tg_info_new[-1][0]] = tg_info_new[-1][1]
        tg_info_dct[tg_info_new[-1][0]][2] = "#"
        tg_info_dct[(float(duration)/1000-tg_info_new[-1][0])/2 + tg_info_new[-1][0]] = [None, None, None, "#", None, None, None, None, None, None, None]


        tg_info_new1 = sorted(self.dict2list(tg_info_dct), key=lambda x: x[0], reverse=False)  # 根据时间信息升序


        return tg_info_new1, duration, script

    def readTG_full(self):
        """
        读取一个11层的TextGrid文件，并存储每层信息。
        信息存在一个dictionary里，以开始时间为key,内容为value
        """
        tg_info = {}
        original_value = [None, None, None, None, None, None, None, None, None, None] #每个key对应的value都是长度为11的list，分别存储汉字，拼音，音素，半音素，韵律边界，句重音，语言，语气，风格，词重音
        line_number = 0
        flag_text = 0
        flag_character = 0
        flag_pinyin = 0
        flag_prosody = 0
        flag_focus = 0
        flag_stress = 0
        flag_phoneme = 0
        flag_semiphoneme = 0
        flag_language = 0
        flag_manner = 0
        flag_style = 0

        with open(self.tg_file,"r", encoding = "utf-8") as f1:
            for line in f1:
                line = line.strip("\n")
                line_number += 1
                # 先找到TextGrid是哪种格式（全都顶格写 or 有一层一层缩进）
                if line_number == 4:
                    if line == "0":
                        format = "simple"
                    elif "xmin" in line:
                        format = "complex"
                    else:
                        self.logger.error("%s: Wrong Format in the TG file!\n" % os.path.basename(self.tg_file))
                        break

                if line_number == 7 and "7" in line: #判断是否是11层的TG
                    self.logger.error("The TG has 7 instead of 11 tiers!")
                    sys.exit(-1)

                # 看读到了哪层信息
                if "\"文本\"" in line:
                    flag_text = 1

                if "\"汉字\"" in line:
                    flag_text = 0
                    flag_character = 1
                    character_line = line_number

                elif "\"拼音\"" in line:
                    flag_character = 0
                    flag_pinyin = 1
                    pinyin_line = line_number

                elif "\"音素\"" in line:
                    flag_pinyin = 0
                    flag_phoneme = 1
                    phoneme_line = line_number

                elif "\"半音素\"" in line:
                    flag_phoneme = 0
                    flag_semiphoneme = 1
                    semi_line = line_number

                elif "\"韵律边界\"" in line:
                    flag_semiphoneme = 0
                    flag_prosody = 1
                    prosody_line = line_number

                elif "\"句重音\"" in line:
                    flag_prosody = 0
                    flag_focus = 1
                    focus_line = line_number

                elif "\"语言\"" in line:
                    flag_focus = 0
                    flag_language = 1
                    language_line = line_number

                elif "\"语气\"" in line:
                    flag_language = 0
                    flag_manner = 1
                    manner_line = line_number

                elif "\"风格\"" in line:
                    flag_manner = 0
                    flag_style = 1
                    style_line = line_number

                elif "\"词重音\"" in line:
                    flag_style = 0
                    flag_stress = 1
                    stress_line = line_number

                #存储每一层信息
                # 两种格式的TextGrid要分开处理
                if line_number > 4:  # line4之前未判断是什么格式

                    #简单格式的TG
                    if format == "simple":
                        if line_number == 5:  # 存储时长信息
                            duration = str(float(line)*1000)
                        elif line_number == 15:  # 存储文本信息
                            script = line[1:-1]

                        if flag_character == 1:  # 存储汉字信息
                            if (line_number - character_line) % 3 == 1 and (line_number - character_line) >= 4:
                                cur_start_time = line
                            elif (line_number - character_line) % 3 == 0 and (line_number - character_line) >= 6:
                                cur_character = line[1:-1]
                                #tg_info[cur_start_time] = original_value #为何不行而下面的方法行？
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time] = [cur_character, None, None, None, None, None, None, None, None, None]

                        elif flag_pinyin == 1:  # 存储拼音信息
                            if (line_number - pinyin_line) % 3 == 1 and (line_number - pinyin_line) >= 4:
                                cur_start_time = line
                            elif (line_number - pinyin_line) % 3 == 0 and (line_number - pinyin_line) >= 6:
                                cur_pinyin = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][1] = cur_pinyin

                        elif flag_phoneme == 1: #存储音素信息
                            if (line_number - phoneme_line) % 3 == 1 and (line_number - phoneme_line) >= 4:
                                cur_start_time = line
                            elif (line_number - phoneme_line) % 3 == 0 and (line_number - phoneme_line) >= 6:
                                cur_phoneme = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                if cur_start_time in tg_info:
                                    tg_info[cur_start_time][2] = cur_phoneme
                                else:
                                    tg_info[cur_start_time] = [None, None, cur_phoneme, None, None, None, None, None, None, None]

                        elif flag_semiphoneme == 1: #存储半音素信息
                            if (line_number - semi_line) % 3 == 1 and (line_number - semi_line) >= 4:
                                cur_start_time = line
                            elif (line_number - semi_line) % 3 == 0 and (line_number - semi_line) >= 6:
                                cur_semiphoneme = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                if cur_start_time in tg_info:
                                    tg_info[cur_start_time][3] = cur_semiphoneme
                                else:
                                    tg_info[cur_start_time] = [None, None, None, cur_semiphoneme, None, None, None, None, None, None]

                        elif flag_prosody == 1: #存储韵律边界信息
                            if (line_number - prosody_line) % 2 == 0 and (line_number - prosody_line) >= 4:
                                cur_start_time = line
                            elif (line_number - prosody_line) % 2 == 1 and (line_number - prosody_line) >= 5:
                                cur_prosody = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][4] = cur_prosody
                        elif flag_focus == 1: # 存储句重音信息
                            if (line_number - focus_line) % 3 == 1 and (line_number - focus_line) >= 4:
                                cur_start_time = line
                            elif (line_number - focus_line) % 3 == 0 and (line_number - focus_line) >= 6:
                                cur_focus = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][5] = cur_focus

                        elif flag_language == 1: #存储语言信息
                            if (line_number - language_line) % 3 == 1 and (line_number - language_line) >= 4:
                                cur_start_time = line
                            elif (line_number - language_line) % 3 == 0 and (line_number - language_line) >= 6:
                                cur_language = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][6] = cur_language

                        elif flag_manner == 1: #存储语气信息
                            if (line_number - manner_line) % 3 == 1 and (line_number - manner_line) >= 4:
                                cur_start_time = line
                            elif (line_number - manner_line) % 3 == 0 and (line_number - manner_line) >= 6:
                                cur_manner = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][7] = cur_manner

                        elif flag_style == 1: #存储风格信息
                            if (line_number - style_line) % 3 == 1 and (line_number - style_line) >= 4:
                                cur_start_time = line
                            elif (line_number - style_line) % 3 == 0 and (line_number - style_line) >= 6:
                                cur_style = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][8] = cur_style

                        elif flag_stress == 1: #存储词重音信息
                            if (line_number - stress_line) % 3 == 1 and (line_number - stress_line) >= 4:
                                cur_start_time = line
                            elif (line_number - stress_line) % 3 == 0 and (line_number - stress_line) >= 6:
                                cur_stress = line[1:-1]
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][9] = cur_stress

                    #复杂信息的TG
                    elif format == "complex":
                        if line_number == 5:  # 存储时长信息
                            duration = line.split(" = ")[1]
                            duration = str(float(duration)*1000)

                        if flag_text == 1 and "text = " in line:  # 存储文本信息
                            script = line.split(" = ")[1]
                            script = re.sub(r'[\s\"]', "", script)

                        elif flag_character == 1:  # 存储汉字信息
                            if (line_number - character_line) % 4 == 1 and (line_number - character_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - character_line) % 4 == 3 and (line_number - character_line) >= 7:
                                cur_character = line.split(" = ")[1]
                                cur_character = re.sub(r'[\s\"]', "", cur_character)
                                cur_start_time = round(float(cur_start_time),6)
                                tg_info[cur_start_time] = [cur_character, None, None, None, None, None, None, None, None, None]

                        elif flag_pinyin == 1:  # 存储拼音信息
                            if (line_number - pinyin_line) % 4 == 1 and (line_number - pinyin_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - pinyin_line) % 4 == 3 and (line_number - pinyin_line) >= 7:
                                cur_pinyin = line.split(" = ")[1]
                                cur_pinyin = re.sub(r'[\s\"]', "", cur_pinyin)
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][1] = cur_pinyin

                        elif flag_phoneme == 1: #存储音素信息
                            if (line_number - phoneme_line) % 4 == 1 and (line_number - phoneme_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - phoneme_line) % 4 == 3 and (line_number - phoneme_line) >= 7:
                                cur_phoneme = line.split(" = ")[1]
                                cur_phoneme = re.sub(r'[\s\"]', "", cur_phoneme)
                                cur_start_time = round(float(cur_start_time), 6)
                                if cur_start_time in tg_info:
                                    tg_info[cur_start_time][2] = cur_phoneme
                                else:
                                    tg_info[cur_start_time] = [None, None, cur_phoneme, None, None, None, None, None, None, None]

                        elif flag_semiphoneme == 1: #存储半音素信息
                            if (line_number - semi_line) % 4 == 1 and (line_number - semi_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - semi_line) % 4 == 3 and (line_number - semi_line) >= 7:
                                cur_semiphoneme = line.split(" = ")[1]
                                cur_semiphoneme = re.sub(r'[\s\"]', "", cur_semiphoneme)
                                cur_start_time = round(float(cur_start_time), 6)
                                if cur_start_time in tg_info:
                                    tg_info[cur_start_time][3] = cur_semiphoneme
                                else:
                                    tg_info[cur_start_time] = [None, None, None, cur_semiphoneme, None, None, None, None, None, None]

                        elif flag_prosody == 1: #存储韵律边界信息
                            if (line_number - prosody_line) % 3 == 2 and (line_number - prosody_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - prosody_line) % 3 == 0 and (line_number - prosody_line) >= 6:
                                cur_prosody = line.split(" = ")[1]
                                cur_prosody = re.sub(r'[\s\"]', "", cur_prosody)
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][4] = cur_prosody

                        elif flag_focus == 1: # 存储句重音信息
                            if (line_number - focus_line) % 4 == 1 and (line_number - focus_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - focus_line) % 4 == 3 and (line_number - focus_line) >= 7:
                                cur_focus = line.split(" = ")[1]
                                cur_focus = re.sub(r'[\s\"]', "", cur_focus)
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][5] = cur_focus

                        elif flag_language == 1: #存储语言信息
                            if (line_number - language_line) % 4 == 1 and (line_number - language_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - language_line) % 4 == 3 and (line_number - language_line) >= 7:
                                cur_language = line.split(" = ")[1]
                                cur_language = re.sub(r'[\s\"]', "", cur_language)
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][6] = cur_language

                        elif flag_manner == 1: #存储语气信息
                            if (line_number - manner_line) % 4 == 1 and (line_number - manner_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - manner_line) % 4 == 3 and (line_number - manner_line) >= 7:
                                cur_manner = line.split(" = ")[1]
                                cur_manner = re.sub(r'[\s\"]', "", cur_manner)
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][7] = cur_manner

                        elif flag_style == 1: #存储风格信息
                            if (line_number - style_line) % 4 == 1 and (line_number - style_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - style_line) % 4 == 3 and (line_number - style_line) >= 7:
                                cur_style = line.split(" = ")[1]
                                cur_style = re.sub(r'[\s\"]', "", cur_style)
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][8] = cur_style

                        elif flag_stress == 1: #存储词重音信息
                            if (line_number - stress_line) % 4 == 1 and (line_number - stress_line) >= 5:
                                cur_start_time = line.split(" = ")[1]
                            elif (line_number - stress_line) % 4 == 3 and (line_number - stress_line) >= 7:
                                cur_stress = line.split(" = ")[1]
                                cur_stress = re.sub(r'[\s\"]', "", cur_stress)
                                cur_start_time = round(float(cur_start_time), 6)
                                tg_info[cur_start_time][9] = cur_stress

        #把lhp/pinyin转成spt
        try:
            lang = False
            for key in tg_info:
                if tg_info[key][6] == "TE":
                    lang = True
                elif tg_info[key][6] in ["TC", "TSH", "TCH", "TCD"]:
                    lang = False
                if tg_info[key][0] != None:
                    if tg_info[key][0] in ["sil", "sp"]: #静音段
                        cur_spt = "#"
                    elif lang == True: # 如果是英文则不变
                        cur_spt = tg_info[key][1]
                    elif lang == False:
                        cur_spt = self.mlf_parse.lhp2spt(tg_info[key][1])
                    tg_info[key][1] = cur_spt
        except:
            self.logger.error("Cannot convert lhp/pinyin to spt!")
            sys.exit(-1)

        tg_info_new = sorted(self.dict2list(tg_info), key=lambda x: x[0], reverse=False)  # 根据时间信息升序

        return tg_info_new, duration, script

    def dict2list(self, dic):
        # 给字典排序
        keys = dic.keys()
        vals = dic.values()
        lst = [(key, val) for key, val in zip(keys, vals)]
        return lst

    def TG2mlf(self):
        #把经过readTG的TG信息转成mlf格式
        if self.actiontype == "tg_full2mlf":
            tg_info_new, duration, script = self.readTG_full()
        elif self.actiontype == "tg2mlf":
            tg_info_new, duration, script = self.readTG_less()

        mlf_info_above = "" #spt行
        mlf_info_below = [] # mlf下面行的信息
        cur_tone = ""
        cur_focus = None
        pre_TE_tag = None
        TE_tag = None
        cur_manner = None
        manner_flag = 0 #看是否已添加TQ的开始标志
        lang_flag = 0
        lang_enx = False
        #把静音段用#表示
        for i in range(len(tg_info_new)):

            for j in range(len(tg_info_new[i][1])):
                if tg_info_new[i][1][j] in ["sil", "sp"]:
                    tg_info_new[i][1][j] = "#"

            #找到语气信息
            if tg_info_new[i][1][7] == "TS":
                cur_manner = False
            elif tg_info_new[i][1][7] == "TQ" and manner_flag == 0: #语气开始
                mlf_info_below.append("\\TQ\\")
                mlf_info_above += "\\TQ\\"
                manner_flag += 1

            if manner_flag == 1 and i == len(tg_info_new) -2: #语气结束
                mlf_info_below.append("\\/TQ\\")
                mlf_info_above += "\\/TQ\\"


            #找到语言信息
            if tg_info_new[i][1][6] == "TE":
                TE_tag = True
            elif tg_info_new[i][1][6] in ["TC", "TSH", "TCD", "TCH"]:
                TE_tag = False
            #加上语言信息的开始标志
            if TE_tag == True and tg_info_new[i][1][4] not in ["0", None] and mlf_info_above[-1] != "%" and i != len(tg_info_new) -2 :
                mlf_info_below.append("\\TE\\")
                mlf_info_above += "\\TE\\"
            pre_TE_tag = TE_tag



            #加上词重音
            if tg_info_new[i][1][9] == "1":
                mlf_info_below.append("\"")
                mlf_info_above += "\""

            ######加上最正常的行
            if tg_info_new[i][1][3] != None:
                cur_line = tg_info_new[i][1][3] + "    " + str(round(tg_info_new[i][0]*1000, 1)) + "    " + "100"
                mlf_info_below.append(cur_line)


            if tg_info_new[i][1][2] != None:
                mlf_info_above += tg_info_new[i][1][3]

            #加上音调
            if tg_info_new[i][1][0] not in [None, "#"]:
                if len(tg_info_new[i][1][1]) >=2 and tg_info_new[i][1][1][1] in ["0","1","2","3","4","5","6","7","8","9"]:
                    cur_tone = tg_info_new[i][1][1][1]
                else:
                    cur_tone = ""
            if tg_info_new[i-1][1][3] != None:
                if tg_info_new[i][1][3] in [tg_info_new[i-1][1][3], tg_info_new[i-1][1][3]+"!"] and tg_info_new[i][1][0] == None: #后一个条件防止上一个字的最后一个phoneme和下一个字的第一个phoneme相同
                    if tg_info_new[i-1][1][1] != "#" and cur_tone != "":
                        mlf_info_below.append(cur_tone)
                        mlf_info_above += cur_tone

            # 加上句重音
            if tg_info_new[i][1][5] == "0":
                cur_focus = ".0"
            elif tg_info_new[i][1][5] == "1":
                cur_focus = ".1"
            if i != len(tg_info_new) -1:
                if cur_focus != None and tg_info_new[i+1][1][4] in ["1", "2", "3","4"]:
                    if tg_info_new[i-1][1][0] != "#": #三级边界的开头不用加
                        mlf_info_below.append(cur_focus)
                        mlf_info_above += cur_focus

            #加上语言的结束标志
            if i != len(tg_info_new) - 1:
                if pre_TE_tag == True and tg_info_new[i + 1][1][4] in ["1", "2", "3", "4"] and mlf_info_below[-2][0] != "#":
                    mlf_info_below.append("\\/TE\\")
                    mlf_info_above += "\\/TE\\"


            #加上韵律边界
            if i != len(tg_info_new) -1:
                if tg_info_new[i+1][1][4] not in [None, "None"]: #到达韵律边界
                    #添加韵律边界
                    if tg_info_new[i+1][1][4] == "0":
                        mlf_info_below.append("-")
                        mlf_info_above += "-"
                    if tg_info_new[i+1][1][4] == "1":
                        mlf_info_below.append("-*")
                        mlf_info_above += "-*"
                    elif tg_info_new[i+1][1][4] == "2":
                        mlf_info_below.append("%")
                        mlf_info_above += "%"
                    elif tg_info_new[i+1][1][4] == "3" and tg_info_new[i-1][1][4] != "3": #三级边界只用加一个%。#已包含在半音素里（是吗？）
                        mlf_info_below.append("%")
                        mlf_info_above += "%"
        return script, duration, mlf_info_above, mlf_info_below

    def write2mlf(self, outputfile):
        """
        把TG2mlf的output写入mlf文件
        """
        script, duration, mlf_info_above, mlf_info_below = self.TG2mlf()
        script = script.encode("utf-8").decode("cp437")
        with open(outputfile,"w", encoding = "cp437") as f1:
            f1.write("*** mlf: v2.00\n")
            f1.write("*** txt: %s\n" % script)
            f1.write("*** spt: %s\n" % mlf_info_above)
            f1.write("*** msec: %.1f\n\n" % float(duration))
            for i in mlf_info_below:
                f1.write(i + "\n")


class Converse(object):
    def __init__(self, logger, langtype, actiontype):
        self.logger = logger
        self.langtype = langtype
        self.actiontype = actiontype
        self.success = 0 #成功转换的文件数
        self.fail = 0 #未成功转换的文件数

    def converse(self, fname, savefoldername):
        if os.path.isfile(fname) and os.path.splitext(fname)[1] == ".mlf":
            saveFileName = os.path.join(savefoldername, os.path.splitext(os.path.basename(fname))[0] + ".TextGrid")
            self.converseFile(fname, saveFileName)
        elif os.path.isfile(fname) and os.path.splitext(fname)[1] == ".TextGrid":
            saveFileName = os.path.join(savefoldername, os.path.splitext(os.path.basename(fname))[0] + ".mlf")
            self.converseFile(fname, saveFileName)
        elif os.path.isdir(fname):
            self.converseFolder(fname, savefoldername)
        else:
            self.logger.error("unknown file or folder name: %s" % fname)
        self.logger.info("Successfully converted %d files! Failed to convert %d files!" % (self.success, self.fail))

    def converseFile(self, fname, savefilename):
        #self.logger.info("Processing %s" % os.path.basename(fname))
        # try:
            if self.actiontype == "mlf2tg_full":
                processing = mlf2tg(logger, self.langtype, fname)
                processing.write2tg_full(savefilename)
            elif self.actiontype == "mlf2tg":
                processing = mlf2tg(logger, self.langtype, fname)
                processing.write2tg_less(savefilename)
            elif self.actiontype in ["tg_full2mlf", "tg2mlf"]:
                processing = tg2mlf(logger, self.langtype, self.actiontype, fname)
                processing.write2mlf(savefilename)
            self.success += 1
        # except:
            # self.logger.error("[%s]: cannot convert this file\n" % os.path.basename(fname))
            # self.fail += 1
            #	if os.path.exists(savefilename):
            #		os.remove(savefilename)

    def converseFolder(self, foldername, savefoldername):
        files = os.listdir(foldername)
        for iFile in files:
            curFile = os.path.join(foldername, iFile)
            saveFile = os.path.join(savefoldername, iFile)

            if os.path.isfile(curFile) and os.path.splitext(curFile)[1] == ".mlf":
                saveFile = os.path.splitext(saveFile)[0] + ".TextGrid"
                self.converseFile(curFile, saveFile)
            elif os.path.isfile(curFile) and os.path.splitext(curFile)[1] == ".TextGrid":
                saveFile = os.path.splitext(saveFile)[0] + ".mlf"
                self.converseFile(curFile, saveFile)
            elif os.path.isdir(curFile):
                if not os.path.exists(saveFile):
                    os.makedirs(saveFile)
                self.converseFolder(curFile, saveFile)

if __name__ == "__main__":
    logger = logging.getLogger()
    formatter = logging.Formatter('[%(filename)s:%(lineno)d] - [%(asctime)s] : *%(levelname)s* | (%(funcName)s) %(message)s', '%Y-%m-%d %H:%M:%S',)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler(os.path.splitext(os.path.abspath(__file__))[0]+".log", 'w')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

    optparser = OptionParser()
    optparser.add_option('-i', "--input", dest="input", action="store", default=None,
                         help="please input the input file/foldername")
    optparser.add_option('-o', "--output", dest="output", action="store", default=None,
                         help="please input the output folder name")
    optparser.add_option('-l', "--langtype", dest="langtype", action="store", default=None,
                         help="please input the langtype enx/mnx/shc/sic/cah")
    optparser.add_option('-t', "--type", dest="type", action="store", default=None,
                     help="please input the type of action mlf2tg/tg2mlf/mlf2tg_full/tg_full2mlf")

    options, args = optparser.parse_args()
    if len(args) != 0:
        logger.error("wrong arguments format!")
        sys.exit(-1)

    if options.input == None or options.output == None:
        logger.error("you have to give input or output folder or filenames!\nUsage: python3 TG_mlf_conversion.py -i inputfolder/file -o outputfolder -t mlf2tg/mlf2tg_full/tg_full2mlf/tg2mlf")
        sys.exit(-1)

    if options.input == options.output:
        logger.error("Input folder and output folder should not be the same!")
        sys.exit(-1)

    if options.langtype not in ["mnx","enx","shc","sic","cah"]:
        logger.error("Wrong langtype! Should be one of mnx/enx/shc/sic/cah")
        sys.exit(-1)

    if options.type not in ["mlf2tg", "tg2mlf", "mlf2tg_full", "tg_full2mlf"]:
        logger.error("Wrong action type! Should be one of mlf2tg/mlf2tg_full/tg_full2mlf/tg2mlf")
        sys.exit(-1)

    elif not os.path.isdir(options.output):
        logger.error("Output should be a folder!")
        sys.exit(-1)

    processor = Converse(logger, options.langtype, options.type)
    processor.converse(options.input, options.output)
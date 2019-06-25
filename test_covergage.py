# coding=utf-8

from cmath import e
from bs4 import BeautifulSoup, Comment
from itertools import islice
import os, sys, tempfile, subprocess, re


def get_diff_by_version(lgr, A_V, B_V):
    """
    获取两次提交之间修改的文件列表 通过后缀名进行过滤.
    :param lgr: git 项目的文件夹.
    :param A_V: 提交 common_start_id 的 hash.
    :param B_V: 提交 common_end_id 的 hash.
    :return: 改变的 java 文件的列表.
    """
    cmd = ['cd %s; git diff %s %s --stat' % (lgr, A_V, B_V)]
    result = []
    try:
        out_tmp = tempfile.SpooledTemporaryFile(max_size=10 * 1000)
        fileno = out_tmp.fileno()
        obj = subprocess.Popen(cmd, stdout=fileno, stderr=fileno, shell=True)
        obj.wait()
        out_tmp.seek(0)
        lines = out_tmp.readlines()
        for value in lines:
            value = value.decode()
            pre = value.split('|')[0].strip()
            if pre[-5:] == ".java":  # 应该考虑一下.kt 结尾
                result.append(pre)
                # else:
                #     pass
        return result
    except Exception as e:
        print("failue by e:", e)
    finally:
        if out_tmp:
            out_tmp.close()


def git_diff_by_file(lgr, A_V, B_V, diff_module, all_commit_in_feature_branch):
    """
    获取增量Java 文件和对应的修改行数 .
    :param lgr: git 项目的文件夹.
    :param A_V: 提交 common_start_id 的 hash.
    :param B_V: 提交 common_end_id 的 hash.
    :param diff_module 改变的 java 文件的列表.
    :param all_commit_in_feature_branch 当前分支除 develop分支的多有 common_id
    :return:返回字典：改变的Java 的文件名字和修改的行数["a.java":[1,2,3],"b.java":[4,5]]
    """
    diff = {}
    for mp in diff_module:
        classname = mp.split('/')[-1].strip()
        print("classname:", classname)
        get_module_path = subprocess.getoutput('cd %s;find . -name "%s"' % (lgr, classname))
        print("module_path:", get_module_path)
        cmd = ['cd %s; git blame %s' % (lgr, get_module_path)]
        try:
            out_tmp = tempfile.SpooledTemporaryFile(max_size=10 * 1000)
            fileno = out_tmp.fileno()
            obj = subprocess.Popen(cmd, stdout=fileno, stderr=fileno, shell=True)
            obj.wait()
            out_tmp.seek(0)
            lines = out_tmp.readlines()
            class_diff = []
            # for value in lines:
            for idx, value in enumerate(lines):
                value = value.decode()[:8]
                if value in all_commit_in_feature_branch:
                    class_diff.append(idx + 1)
                else:
                    continue
        except Exception as e:
            print("fail by e:", e)
        if len(class_diff) != 0:
            diff[get_module_path] = class_diff
    print("git_diff_by_file_diff", diff)
    return diff


def get_project_and_file_path(root_dir, java_file):
    """
    增量统计代码覆盖主方法.
    :param root_dir: git 项目的文件夹（jacoco 报告文件夹）.
    :param java_file: 改变的Java 的文件名字和修改的行数["a.java":[1,2,3],"b.java":[4,5]].
    """
    print("value:", java_file.values())
    for k, v in java_file.items():
        print("K is:", k, "V is:", v)
        JavaFileName = k.split('/')[-1].strip()
        insertFileName = JavaFileName[:-5]
        # ValueLen = len(v)
        # print("value len:", ValueLen)
        # insert +
        for parent, dirnames, fileNames in os.walk(root_dir):
            for fileName in fileNames:
                fileNamePath = os.path.join(parent, fileName)
                indexNamePath = os.path.join(parent, "index.html")
                if JavaFileName + ".html" == fileName:
                    # java中变更行数材，插入+到对应java.html文件中，并返回覆盖行数、总变更数
                    DiffLineNumber, total_diff_number, imperfect_number = Diff_Line_Number(fileNamePath, v)
                    # 没有新增代码则不做为0插入（代码有新增，但不是主要方法，主要为常量、import包、空格等）
                    if total_diff_number == 0:
                        continue
                    # 更改index.html文件布局，在后面插入列
                    update_Index_Html_File(indexNamePath)
                    insertFileNames = insertFileName + ".html"
                    # 插入结果到对应包名下（java.html文件统计页）index.html文件
                    insert_Total_Index_Html(indexNamePath, insertFileNames, total_diff_number, DiffLineNumber, imperfect_number)
                    # 插入包路径下index.html 覆盖统计
                    totalDiffLine, totalTRLine, totalIMPLine = update_Total_Html(indexNamePath, total_diff_number, DiffLineNumber, imperfect_number)
                    indexFilePath = os.path.dirname(parent) + "/index.html"
                    insertIndexFileName = (fileNamePath.split('/')[-2].split())
                    update_Index_Html_File(indexFilePath)
                    # 根目录index.html插入包代码覆盖、和新增
                    insert_Total_Index_Html(indexFilePath, insertIndexFileName, totalDiffLine, totalTRLine, totalIMPLine)
                    # 统计所有新增和覆盖结果
                    get_diff_total_line(indexFilePath)


def get_diff_total_line(indexHtmlPath):
    """
    统计所有包的代码覆盖和修改行数和未完全覆盖行数并写入index.
    :param indexHtmlPath: jacoco 根目录index.html .
    """
    DiffNum = 0
    soup = BeautifulSoup(openFile(indexHtmlPath), 'lxml')
    #对应包的修改行数
    a = soup.find_all(id="DiffN")

    for k in a:
        DiffNum += int(k.string)
        totalDiffNum = soup.find(id="u")
        totalDiffNum.string = str(DiffNum)
        CRNum = 0
        # 对应包的覆盖行数
        b = soup.find_all(id="CRN")
    for i in b:
        CRNum += int(i.string)
        totalCRN = soup.find(id="TCR")
        totalCRN.string = str(CRNum)
        IMPNum = 0
        c = soup.find_all(id="v")
    for j in c:
        IMPNum += int(j.string)
        IMPCRN = soup.find(id="IMP")
        IMPCRN.string = str(IMPNum)
    writeFile(indexHtmlPath, soup)


def update_Total_Html(indexHtmlPath, DiffNum, CrNum, ImpNum):
    """
    jacoco 报告包目录下的 index.html 文件插入覆盖和新增统计行数
    :param indexHtmlPath: 包目录下的 index.html 文件.
    :param DiffNum: 增量代码行数.
    :param CrNum: 覆盖代码行数.
    :return 返回当前包的增量和覆盖代码总行数和未完全覆盖行数
    """
    soup = BeautifulSoup(openFile(indexHtmlPath), 'lxml')
    num = soup.find(id="u")
    num.string = str(int(num.string) + DiffNum)
    num.string = (num.string)
    CR = soup.find(id="TCR")
    CR.string = str(int(CR.string) + CrNum)
    CR.string = (CR.string)
    IMP = soup.find(id="IMP")
    IMP.string = str(int(IMP.string) + ImpNum)
    IMP.string = (IMP.string)
    writeFile(indexHtmlPath, soup)
    return num.string, CR.string, IMP.string


# 获取差异的行数
def Diff_Line_Number(indexHtmlPath, number):
    """
    java类中变更行数材，插入+到对应java.html文件中.
    :param indexHtmlPath: Java.html 文件.
    :param number: 当前 java 文件增量代码行数.
    :return 返回当前 Java 类的覆盖和增量行数和未完全覆盖行数.
    """
    diff_number = 0
    total_diff_number = 0
    imperfect_number = 0
    soup = BeautifulSoup(openFile(indexHtmlPath), 'lxml')
    for i in number:
        s = soup.find("span", id="L" + str(i))
        # print("s  is ==", s)
        plus = soup.new_string("+")
        if s is not None and s.string is not None:
            total_diff_number = total_diff_number + 1
            if s['class'][0] == 'fc':
                diff_number = diff_number + 1
            elif s['class'][0] == 'pc':
                imperfect_number = imperfect_number + 1
            s.string.insert_before(plus)
    writeFile(indexHtmlPath, soup)
    return diff_number, total_diff_number, imperfect_number


def update_Index_Html_File(htmlPath):
    """
    html路径下的diff、未完全覆盖和covered列插入.
    :param htmlPath: Java.html 文件.
    """
    soup = BeautifulSoup(openFile(htmlPath), 'lxml')
    Diff_text = soup.find_all(text="Diff")
    if Diff_text:
        print("pass")
    else:
        diff_line_tag = soup.new_tag('td')
        diff_line_tag['class'] = "sortable ctr2"
        diff_line_tag.string = "Diff"
        diff_line_tag['id'] = "n"
        diff_line_tag['onclick'] = "toggleSort(this)"
        diff = soup.find_all(text="Missed")
        diff_ = diff[-1].find_next('td')
        imperfect_number_tag = soup.new_tag('td')
        imperfect_number_tag['class'] = "sortable ctr2"
        imperfect_number_tag.string = "Imper"
        imperfect_number_tag['id'] = 'o'
        imperfect_number_tag['onclick'] = "toggleSort(this)"
        inperfect_ = diff[-2].find_next('td')
        imperfect_num = soup.new_tag('td')
        imperfect_num['class'] = "ctr2"
        imperfect_num['id'] = "IMP"
        imperfect_num.string = str("0")
        totalNum = soup.new_tag('td')
        totalNum['class'] = "ctr2"
        totalNum['id'] = "u"
        totalNum.string = str("0")
        totalName = soup.find_all('tfoot')
        totalCR = soup.new_tag('td')
        totalCR['class'] = "ctr2"
        totalCR['id'] = "TCR"
        totalCR.string = str("0")
        total = totalName[-1].find_next('tr')
        CR = soup.new_tag('td')
        CR['class'] = "sortable ctr2"
        CR.string = "Covered"
        CR['id'] = "CR"
        CR['onclick'] = "toggleSort(this)"
        total.append(totalCR)
        total.append(imperfect_num)
        total.append(totalNum)
        diff_.insert_after(diff_line_tag)
        diff_.append(CR)
        diff_.append(imperfect_number_tag)
        writeFile(htmlPath, soup)


def openFile(index_Html_File_Path):
    filePath = open(index_Html_File_Path)
    data = filePath.read()
    filePath.close
    return data


def writeFile(index_Html_File_Path, write_data):
    file = open(index_Html_File_Path, 'w')
    file.write(str(write_data))
    file.close()


def insert_Total_Index_Html(indexHtmlPath, Name, DiffNum, CrNum, ImperNum):
    """
    html写入总的增量和覆盖代码数量和未完全覆盖数量.
    :param indexHtmlPath: index.html 文件.
    :param DiffNum: 增量代码数量.
    :param CrNum: 覆盖代码数量.
    :param ImperNum: 不完全覆盖代码数量.
    """
    fileName = "".join(Name)
    soup = BeautifulSoup(openFile(indexHtmlPath), 'lxml')
    num = soup.find_all(href=re.compile(fileName))
    print("num is:", num)
    if len(num) >= 2:
        for i, j in enumerate(num):
            if j.string != fileName:
                del num[i]
        print("inset html file name is:", num)
    elif len(num) == 0:
        fileName_new = "%s(\s\w+)?" % (fileName)[:-5]
        num = soup.find_all(attrs={"href": re.compile(fileName_new)})
        print("file name not find and replace by new num:", num)
        if len(num) == 0:
            print("this file ont find:", Name)
            return
    # print("href is :", num)
    try:
        CRN = num[0].parent.parent
        print("CRN.parent.parent is ：", CRN)
    except Exception as e:
        # CRN=num
        print("Exception", e)
    CR = CRN.find(id='CRN')
    if CR is None:
        total = soup.new_tag('td')
        total['class'] = "ctr2"
        total['id'] = "CRN"
        total.string = str(CrNum)
        CRN.append(total)
    else:
        CR.string = str(CrNum)

    m = num[0].parent.parent
    imper_nem = m.find(id="v")
    if imper_nem is None:
        imperCR = soup.new_tag('td')
        imperCR['class'] = "ctr2"
        imperCR['id'] = "v"
        imperCR.string = str(ImperNum)
        print ("ImperNum", ImperNum)
        m.append(imperCR)
    else:
        imper_nem.string = str(ImperNum)
    n = num[0].parent.parent
    diff_nem = n.find(id="DiffN")
    if diff_nem is None:
        totalCR = soup.new_tag('td')
        totalCR['class'] = "ctr2"
        totalCR['id'] = "DiffN"
        totalCR.string = str(DiffNum)
        n.append(totalCR)
    else:
        diff_nem.string = str(DiffNum)
    writeFile(indexHtmlPath, soup)


def is_main_branch(lgr, app_name):
    """
        判断是否为主分支.
        :param lgr: git 项目的文件夹.
        :param app_name: APP 名称.
        :return 返回Boolean.
    """
    if (app_name == "Bigolive"):
        main_branch = "bigo_show_develop"
    else:
        main_branch = "develop"

    cmd_get_origin_br_name = ['cd %s; git rev-parse --abbrev-ref --symbolic-full-name @{u}' % (lgr)]
    result = []
    try:
        out_tmp = tempfile.SpooledTemporaryFile(max_size=10 * 1000)
        fileno = out_tmp.fileno()
        obj = subprocess.Popen(cmd_get_origin_br_name, stdout=fileno, stderr=fileno, shell=True)
        obj.wait()
        out_tmp.seek(0)
        br_name = out_tmp.read().decode('utf-8').strip()
        idx = br_name.rfind('/')
        length = len(br_name)
        if (main_branch == br_name[idx + 1:length]):
            return True
        else:
            return False

    except Exception as e:
        print("failue by e:", e)
    finally:
        if out_tmp:
            out_tmp.close()


def get_all_commit_in_current_branch(lgr, is_main_branch, A_V, B_V):
    """
    剔除两个 commitid 之间分支非主分支commitid.
    :param lgr: git 项目的文件夹.
    :param A_V: 提交 common_start_id 的 hash.
    :param B_V: 提交 common_end_id 的 hash.
    :param is_main_branch: 是否为主分支.
    :return: 两个commitid之间所有当前分支的commitid.
    """
    if (is_main_branch):
        cmd_get_all_commit = ['cd %s; git log %s...%s --format="%%H" ' % (lgr, A_V, B_V)]
    else:
        cmd_get_all_commit = ['cd %s; git log %s...%s --no-merges --first-parent --format="%%H" ' % (lgr, A_V, B_V)]

    result = []
    try:
        out_tmp = tempfile.SpooledTemporaryFile(max_size=10 * 1000)
        fileno = out_tmp.fileno()
        obj = subprocess.Popen(cmd_get_all_commit, stdout=fileno, stderr=fileno, shell=True)
        obj.wait()
        out_tmp.seek(0)
        lines = out_tmp.readlines()
        for value in lines:
            result.append(value.decode('utf-8').strip()[:8])
        return result
    except Exception as e:
        print("failue by e:", e)
    finally:
        if out_tmp:
            out_tmp.close()


if __name__ == "__main__":
    local_git_repoisty_dir = "/data/jenkins/workspace/workspace/like-android_jacoco_2"
    print("local_git_repoisty_dir is :", local_git_repoisty_dir)
    A_V = sys.argv[1]
    B_V = sys.argv[2]
    app_name = sys.argv[3]
    get_version_diff_name = get_diff_by_version(local_git_repoisty_dir, A_V, B_V)
    get_all_commit_in_current_branch = get_all_commit_in_current_branch(local_git_repoisty_dir,
                                                                        is_main_branch(local_git_repoisty_dir,
                                                                                       app_name), A_V, B_V)
    get_diff_file_name_and_lines = git_diff_by_file(local_git_repoisty_dir, A_V, B_V, get_version_diff_name,
                                                    get_all_commit_in_current_branch)
    get_diff_file_name_and_lines=git_diff_by_file(local_git_repoisty_dir, A_V, B_V, get_version_diff_name)
    # local_git_repoisty_dir = "/Users/billli/Downloads/jacocoReport/html"
    # get_diff_file_name_and_lines = {'./iHeima/com/yy/iheima/util/BitmapUtil.java': [32, 43, 657, 658, 659, 661, 662],'./iHeimaLib/src/sg/bigo/live/protocol/filter/FetchFiltersByGroupIdProtocol.java': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151]}
    get_project_and_file_path(local_git_repoisty_dir, get_diff_file_name_and_lines)

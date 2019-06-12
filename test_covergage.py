#coding=utf-8

from cmath import e
from bs4 import BeautifulSoup,Comment
from itertools import islice
import os, sys, tempfile, subprocess, re


#获取版本差异，通过后缀名进行过滤
def get_diff_by_version(lgr,A_V,B_V):
    cmd=['cd %s; git diff %s %s --stat'%(lgr,A_V,B_V)]
    result=[]
    try:
        out_tmp=tempfile.SpooledTemporaryFile(max_size=10*1000)
        fileno=out_tmp.fileno()
        obj=subprocess.Popen(cmd, stdout=fileno, stderr=fileno, shell=True)
        obj.wait()
        out_tmp.seek(0)
        lines=out_tmp.readlines()
        for value in lines:
            value = value.decode()
            pre=value.split('|')[0].strip()
            #print(pre)
            # if "SXGCDS" in pre:
            #     pass
            if pre[-5:]==".java":
                result.append(pre)
            else:
                pass
        return result
    except Exception as e:
            print("failue by e:",e)
    finally:
            if out_tmp:
                out_tmp.close()


#通过传入版本差异module，找到对应的文件
# def git_diff_by_file(lgr,A_V,B_V,diff_module):
#     diff={}
#     for mp in diff_module:
#         classname=mp.split('/')[-1].strip()
#         # print("classname:",classname)
#         # get_module_cmd=['cd %s;find . -name "%s"'%(lgr,classname)]
#         # get_module_path=subprocess.Popen(get_module_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).stdout.read()
#         # cmd=['cd %s; git diff %s %s -- %s'%(lgr, A_V, B_V, get_module_path)]
#         get_module_path = subprocess.getoutput('cd %s;find . -name "%s"' %(lgr, classname))
#         cmd = ['cd %s; git diff %s %s -- %s' % (local_git_repoisty_dir, A_V, B_V, get_module_path)]
#         try:
#             out_tmp=tempfile.SpooledTemporaryFile(max_size=10*1000)
#             fileno=out_tmp.fileno()
#             obj=subprocess.Popen(cmd, stdout=fileno, stderr=fileno, shell=True)
#             obj.wait()
#             out_tmp.seek(0)
#             lines=out_tmp.readlines()
#             i = 0
#             flag = 0
#             begin_line = 0
#             time = 0
#             diff_line = 0
#             class_diff = []
#
#             for value in lines:
#                 value = value.decode()
#                 if "new file" in value:
#                     class_diff.append(0)
#                     break
#                 elif "@@" in value :
#                     begin_line=0
#                     flag=0
#                     begin_line=value.split('@@')[1].split('+')[1].split(',')[0]
#                     i=i+1
#                     flag=i
#                 elif value.startswith('+') and "+++" not in value:
#                     i=i+1
#                     diff_line=int(begin_line) + i - int(flag) -1
#                     class_diff.append(diff_line)
#                 elif value.startswith('-') and "---" not in value:
#                     pass
#                 else:
#                     i=i+1
#         except Exception as e:
#             print("fail by e:",e)
#
#         diff[get_module_path]=class_diff
#     print("diff:", type(diff))
#     return diff


#获取项目与差异文件路径

#通过传入版本差异module，找到对应的文件
def git_diff_by_file(lgr,A_V,B_V,diff_module,all_commit_in_feature_branch):
    diff={}
    for mp in diff_module:
        classname=mp.split('/')[-1].strip()
        print("classname:",classname)
        # get_module_cmd=['cd %s;find . -name "%s"'%(lgr,classname)]
        # get_module_path=subprocess.Popen(get_module_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).stdout.read()
        # cmd=['cd %s; git diff %s %s -- %s'%(lgr, A_V, B_V, get_module_path)]
        get_module_path = subprocess.getoutput('cd %s;find . -name "%s"' %(lgr, classname))
        print("module_path:",get_module_path)
        # cmd = ['cd %s; git diff %s %s -- %s' % (local_git_repoisty_dir, A_V, B_V, get_module_path)]
        cmd = ['cd %s; git blame %s' % (local_git_repoisty_dir, get_module_path)]
        try:
            out_tmp=tempfile.SpooledTemporaryFile(max_size=10*1000)
            fileno=out_tmp.fileno()
            obj=subprocess.Popen(cmd, stdout=fileno, stderr=fileno, shell=True)
            obj.wait()
            out_tmp.seek(0)
            lines=out_tmp.readlines()
            i = 0
            flag = 0
            begin_line = 0
            time = 0
            diff_line = 0
            class_diff = []
            # for value in lines:
            for idx,value in enumerate(lines):
                value = value.decode()[:8]
                if value in all_commit_in_feature_branch:
                    class_diff.append(idx + 1)
                else:
                    continue
        except Exception as e:
            print("fail by e:",e)
        if class_diff is not None:
            diff[get_module_path]=class_diff
    print("git_diff_by_file_diff",diff)
    return diff

def get_project_and_file_path(root_dir,java_file):
    print("value:",java_file.values())
    for k,v in java_file.items():
        print("K is:",k,"V is:",v)
        JavaFileName=k.split('/')[-1].strip()
        insertFileName=JavaFileName[:-5]
        ValueLen=len(v)
        print("value len:", ValueLen)

        # insert +
        for parent, dirnames, fileNames in os.walk(root_dir):
            for fileName in fileNames:
                fileNamePath=os.path.join(parent, fileName)
                indexNamePath=os.path.join(parent,"index.html")
                if JavaFileName + ".html" == fileName:
                    # print("insert fileName",JavaFileName,fileNamePath)
                    # f=open(fileNamePath)
                    # date=f.read()
                    # f.close()
                    # n=0
                    # tempfile=os.path.join(parent,"tempFile.html")
                    # with open(fileNamePath,"r+") as f:
                    #     for x in f:
                    #         n+=1
                    #         if n in v:
                    #             print("N value is:",n)
                    #             result="+ " + x
                    #             with open(tempfile,"a") as t:
                    #                 t.write(result)
                    #         else:
                    #             x=" " + x
                    #             with open(tempfile,"a") as t:
                    #                 t.write(x)
                    # t.close()
                    # os.remove(fileNamePath)
                    # os.rename(tempfile,fileNamePath)
                    DiffLineNumber,total_diff_number=Diff_Line_Number(fileNamePath,v)
                    update_Index_Html_File(indexNamePath)
                    insertFileNames=insertFileName+".html"
                    insert_Total_Index_Html(indexNamePath, insertFileNames, total_diff_number, DiffLineNumber)
                    totalDiffLine,totalTRLine=update_Total_Html(indexNamePath,total_diff_number,DiffLineNumber)
                    indexFilePath=os.path.dirname(parent)+"/index.html"
                    insertIndexFileName=(fileNamePath.split('/')[-2].split())
                    update_Index_Html_File(indexFilePath)
                    insert_Total_Index_Html(indexFilePath, insertIndexFileName, totalDiffLine, totalTRLine)
                    get_diff_total_line(indexFilePath)


#获取差总共差异行数
def get_diff_total_line(indexHtmlPath):
    DiffNum = 0
    soup = BeautifulSoup(openFile(indexHtmlPath), 'lxml')
    a = soup.find_all(id="DiffN")
    # print a
    for k in a:
        DiffNum += int(k.string)
        totalDiffNum = soup.find(id="u")
        totalDiffNum.string = str(DiffNum)
        CRNum = 0
        b = soup.find_all(id="CRN")
    for i in b:
        CRNum += int(i.string)
        # print("CRNum:", CRNum)
        totalCRN = soup.find(id="TCR")
        # print(totalCRN)
        totalCRN.string = str(CRNum)
    writeFile(indexHtmlPath, soup)


#写入内层index文件，total、Diff and Covered
def update_Total_Html(indexHtmlPath, DiffNum, CrNum):
    soup = BeautifulSoup(openFile(indexHtmlPath), 'lxml')
    num = soup.find(id="u")
    num.string = str(int(num.string) + DiffNum)
    num.string = (num.string)
    CR = soup.find(id="TCR")
    CR.string = str(int(CR.string) + CrNum)
    CR.string = (CR.string)
    writeFile(indexHtmlPath,soup)
    return num.string, CR.string

#获取差异的行数
def Diff_Line_Number(indexHtmlPath,number):
    diff_number= 0
    total_diff_number=0
    soup = BeautifulSoup(openFile(indexHtmlPath), 'lxml')
    for i in number:
        s = soup.find("span", id = "L" +str(i))
        print("s  is ==",s)
        plus = soup.new_string("+")
        if s is not None and s.string is not None:
            if s['class'][0] == 'fc':
                diff_number = diff_number + 1
                # s.string.insert_before(plus)
            elif s['class'][0] == 'pc':
                total_diff_number = total_diff_number + 1
                # s.string.insert_before(plus)
            else:
                total_diff_number=total_diff_number + 1
                print("s.string is:",s.string)
            s.string.insert_before(plus)
    writeFile(indexHtmlPath, soup)
    total_diff_number = total_diff_number + diff_number
    return diff_number,total_diff_number

#html路径下的diff列插入
def update_Index_Html_File(htmlPath):
    soup = BeautifulSoup(openFile(htmlPath), 'lxml')
    Diff_text = soup.find_all(text="Diff")
    if Diff_text:
        print("pass")
    else:
        # print(Diff_text)
        diff_line_tag = soup.new_tag('td')
        diff_line_tag['class'] = "sortable ctr2"
        diff_line_tag.string = "Diff"
        diff_line_tag['id'] = "n"
        diff_line_tag['onclick'] = "toggleSort(this)"
        diff = soup.find_all(text="Missed")
        diff_ = diff[-1].find_next('td')
        # print "diff_",diff_
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
        total.append(totalNum)
        diff_.insert_after(diff_line_tag)
        diff_.append(CR)
        writeFile(htmlPath, soup)

def openFile(index_Html_File_Path):
        filePath=open(index_Html_File_Path)
        data=filePath.read()
        filePath.close
        return data

def writeFile(index_Html_File_Path,write_data):
    file=open(index_Html_File_Path,'w')
    file.write(str(write_data))
    file.close()



#写入总的覆盖率
def insert_Total_Index_Html(indexHtmlPath, Name, DiffNum, CrNum):
    fileName = "".join(Name)
    soup = BeautifulSoup(openFile(indexHtmlPath),'lxml')
    num=soup.find_all(href=re.compile(fileName))
    print("num is:",num)
    if len(num) >= 2:
        for i,j in enumerate(num):
            if j.string != fileName:
                del num[i]
        print("inset html file name:",j.string,"  num string:",num)
    elif len(num) == 0:
        fileName_new ="%s(\s\w+)?"%(fileName)[:-5]
        num_new = soup.find_all(attrs={"href": re.compile(fileName_new)})
        for i,j in enumerate(num_new):
            j["href"]=fileName[:-5]+".java.html"
        print ("num_new:",num_new)
        writeFile(indexHtmlPath, soup)
        return
    print("href is :", num)
    try:
        CRN=num[0].parent.parent
        print("CRN.parent.parent is ：",CRN)
    except Exception as e:
        # CRN=num
        print("Exception", e)
    CR=CRN.find(id='CRN')
    if CR is None:
        total=soup.new_tag('td')
        total['class']="ctr2"
        total['id']="CRN"
        print("CRNum", CrNum)
        total.string=str(CrNum)
        CRN.append(total)
        print("CRN is new:", CRN)
    else:
        CR.string=str(CrNum)

    n=num[0].parent.parent
    diff_nem=n.find(id="DiffN")
    if diff_nem is None:
        totalCR=soup.new_tag('td')
        totalCR['class']="ctr2"
        totalCR['id']="DiffN"
        totalCR.string=str(DiffNum)
        n.append(totalCR)
    else:
        diff_nem.string=str(DiffNum)
    writeFile(indexHtmlPath,soup)


def is_main_branch(lgr,app_name):
    if(app_name == "Bigolive"):
        main_branch="bigo_show_develop"
    else:
        main_branch="develop"    

    cmd_get_origin_br_name=['cd %s; git rev-parse --abbrev-ref --symbolic-full-name @{u}'%(lgr)]

    result=[]
    try:
        out_tmp=tempfile.SpooledTemporaryFile(max_size=10*1000)
        fileno=out_tmp.fileno()
        obj=subprocess.Popen(cmd_get_origin_br_name, stdout=fileno, stderr=fileno, shell=True)
        obj.wait()
        out_tmp.seek(0)
        br_name=out_tmp.read().decode('utf-8').strip()
        idx=br_name.rfind('/')
        length=len(br_name)
        if(main_branch == br_name[idx+1:length]):
            return True
        else:
            return False
                
    except Exception as e:
            print("failue by e:",e)
    finally:
            if out_tmp:
                out_tmp.close()


#获取两个commitid之间所有当前分支的commitid（非主分支不包括merge过来的commitid）
def get_all_commit_in_current_branch(lgr,is_main_branch,A_V,B_V):
    if(is_main_branch):
        cmd_get_all_commit=['cd %s; git log %s...%s --format="%%H" '%(lgr,A_V,B_V)]
    else:
        cmd_get_all_commit=['cd %s; git log %s...%s --no-merges --first-parent --format="%%H" '%(lgr,A_V,B_V)]

    result=[]
    try:
        out_tmp=tempfile.SpooledTemporaryFile(max_size=10*1000)
        fileno=out_tmp.fileno()
        obj=subprocess.Popen(cmd_get_all_commit, stdout=fileno, stderr=fileno, shell=True)
        obj.wait()
        out_tmp.seek(0)
        lines=out_tmp.readlines()
        for value in lines:
            result.append(value.decode('utf-8').strip()[:8])
        return result
    except Exception as e:
            print("failue by e:",e)
    finally:
            if out_tmp:
                out_tmp.close()


if __name__ == "__main__":
    local_git_repoisty_dir=os.getcwd()
    local_git_repoisty_dir="/data/jenkins/workspace/workspace/like-android_jacoco_2"
    print("local_git_repoisty_dir is :",local_git_repoisty_dir)
    A_V=sys.argv[1]
    B_V=sys.argv[2]
    app_name=sys.argv[3]
    # A_V="908031f164e8bcdad8a9bbffb1a40c371c2c3dc7"
    # B_V="e9d70e7ce62a9e15b9145357d9c3f20d483a62e6"

    get_version_diff_name=get_diff_by_version(local_git_repoisty_dir, A_V, B_V)
    get_all_commit_in_current_branch = get_all_commit_in_current_branch(local_git_repoisty_dir, is_main_branch(local_git_repoisty_dir,app_name), A_V, B_V)
    get_diff_file_name_and_lines = git_diff_by_file(local_git_repoisty_dir, A_V, B_V, get_version_diff_name,
                                                    get_all_commit_in_current_branch)
    # get_diff_file_name_and_lines=git_diff_by_file(local_git_repoisty_dir, A_V, B_V, get_version_diff_name)
    # local_git_repoisty_dir = "/Users/billli/Downloads/jacocoReport/html"
    # get_diff_file_name_and_lines = {'./iHeimaLib/src/sg/bigo/live/protocol/filter/FetchFiltersByGroupIdProtocol.java': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151]}
    get_project_and_file_path(local_git_repoisty_dir,get_diff_file_name_and_lines)


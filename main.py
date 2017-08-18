from cpscrape import *
import requests
from captchaparser import *
from PIL import Image
import os
import base64
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import re


def main():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)#ssl warning disable

    if not os.path.exists("CoursePageDownloads"):
        os.mkdir("CoursePageDownloads")

    uname="YOUR_USERNAME_HERE"
    passwd="YOUR_PASSWORD_HERE"
    semSubId='VL2017181'

    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    }
    mainpage = requests.get('https://vtopbeta.vit.ac.in/vtop/', headers=headers, verify=False)

    cookie=mainpage.cookies['JSESSIONID']
    cookie='JSESSIONID='+cookie


    root = BeautifulSoup(mainpage.text, "html.parser")
    img_data = root.find_all("img")[1]["src"].strip("data:image/png;base64,")
    with open("captcha.png", "wb") as fh:
        fh.write(base64.b64decode(img_data))
    img=Image.open("captcha.png")
    captchaCheck=CaptchaParse(img)


    newheader={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36','cookie':cookie}
    logindata={'uname':uname,'passwd':passwd,'captchaCheck':captchaCheck}
    login=requests.post('https://vtopbeta.vit.ac.in/vtop/processLogin',headers=newheader,data=logindata,verify=False)


    timetable=requests.post('https://vtopbeta.vit.ac.in/vtop/processViewTimeTable',headers=newheader,data={'semesterSubId':semSubId},verify=False)
    tt=BeautifulSoup(timetable.text,"html.parser")
    table=tt.find_all(class_="table")[0]
    facnames=[]
    crsnames=[]
    classids=[]
    slots=[]
    venues=[]
    for row in table.find_all("tr"):
        col=row.find_all("td")
        col=col[:-1]
        if len(col)!=0 and col[4].get_text().strip()!='EPJ':
            classids.append(col[1].get_text().strip())
            crsnames.append(col[2].get_text().strip()+'-'+col[3].get_text().strip())
            slots.append(col[11].get_text().replace('+','/'))
            venues.append(col[12].get_text().strip())
            facnames.append(col[13].p.text)



    for i in range(0,len(classids)):
        cp=requests.post('https://vtopbeta.vit.ac.in/vtop/getCourseForCoursePage',headers=newheader,data={'semSubId':semSubId,'paramReturnId':'getCourseForCoursePage'},verify=False)
        cpsrc=BeautifulSoup(cp.text,"html.parser")
        options=cpsrc.find("select",attrs={'id':"courseCode"})
        classId=classids[i]
        slotName=slots[i]
        teachercp=requests.post('https://vtopbeta.vit.ac.in/vtop/processViewStudentCourseDetail',headers=newheader,verify=False,
            data={
            'slotName':slotName,
            'classId':classId,
            'allottedProgram':'ALL',
            'semSubId':semSubId
            })

        rows1,rows2=parsethepage(teachercp)
        for key in rows1.keys():#upper table parsing
            link='https://vtopbeta.vit.ac.in'+rows1[key]
            if not os.path.exists("CoursePageDownloads//linklists.txt"):
                with open("CoursePageDownloads//linklists.txt","w") as f:
                    f.write(link+'\n')
            else:
                with open("CoursePageDownloads//linklists.txt","r") as f:
                    links=[i.strip('\n') for i in f.readlines()]
                if link in links:
                    continue
                else:
                    with open("CoursePageDownloads//linklists.txt","a") as f:
                        f.write(link+'\n')
            dl=requests.get(link,headers=newheader,verify=False)
            path="CoursePageDownloads//"+crsnames[i]+'//'+facnames[i]+'-'+slots[i].replace('/','+')
            if not os.path.exists("CoursePageDownloads//"+crsnames[i]):
                os.mkdir("CoursePageDownloads//"+crsnames[i])
            if not os.path.exists(path):
                os.mkdir(path)
            filename=filename=dl.headers['Content-disposition'][21:]
            fext=filename[filename.rfind('.'):]
            fname=key+fext
            path+='//'+fname
            if not os.path.exists(path):
                with open(path,"wb") as f:
                    for chunk in dl:
                        f.write(chunk)
            print("downloaded ",fname)


        for j in range(0,len(rows2)):#lower table parsing
            link='https://vtopbeta.vit.ac.in'+rows2[j][4]
            if not os.path.exists("CoursePageDownloads//linklists.txt"):
                with open("CoursePageDownloads//linklists.txt","w") as f:
                    f.write(link+'\n')
            else:
                with open("CoursePageDownloads//linklists.txt","r") as f:
                    links=[i.strip('\n') for i in f.readlines()]
                if link in links:
                    continue
                else:
                    with open("CoursePageDownloads//linklists.txt","a") as f:
                        f.write(link+'\n')
            dl=requests.get(link,headers=newheader,verify=False)
            path="CoursePageDownloads//"+crsnames[i]+'//'+facnames[i]+'-'+slots[i].replace('/','+')
            if not os.path.exists("CoursePageDownloads//"+crsnames[i]):
                os.mkdir("CoursePageDownloads//"+crsnames[i])
            if not os.path.exists(path):
                os.mkdir(path)
            filename=dl.headers['Content-disposition'][21:]
            ect=0
            for k in range(0,len(filename)):
                if filename[k]=='_':
                    ect+=1
                if ect==5:
                    fext='-'+filename[k+1:]
                    break
            fname = re.sub('[\/:*?"<>|]','-', rows2[j][3]+'-'+rows2[j][1])
            path+="//"+fname+fext
            if not os.path.exists(path):
                with open(path,"wb") as f:
                    for chunk in dl:
                        f.write(chunk)
            print("downloaded ",fname+fext)
    os.remove("captcha.png")
main()

import re
import codecs
import chardet
import os
import threading
import time
import requests
import re
from collections import Counter
import datetime


class Synchronize:
    def __init__(self,category,gold):
        initTime = datetime.datetime.now().replace(minute=0, second=0).timestamp()
        self.initTime = initTime
        #初始化变量
        self.top = {}
        self.Json = {}
        self.array = []
        self.allIP = set()
        self.IP = ''
        self.machine = ''
        # 默认路径

        if category =='' or 1:
            category = 'C:\\Users\\Administrator\\Desktop\\176\\MirServer\\'
            print('默认路径')
        self.category = category
        print('路径：',self.category)
        #默认元宝路径
        if gold == '' or None :
            gold = "%sMir200\\Envir\\QuestDiary\\64pay充值元宝\\元宝\\"%category
            print('默认元宝路径')
        self.gold = gold
        print('元宝路径：', self.gold )

    #开启5秒自循环
    def fn(self):
        print('5秒自循环中')
        self.getGold()
        self.rejectRepeat()
        self.little_timerStart = threading.Timer(4, self.fn).start()


    #获取每1小时执行一次
    def fn_HalfHour(self):
        #改半小时
        now = 60*60 - ((datetime.datetime.now().timestamp()) - self.initTime)
        if now > 60*30:
            now -= 60*30
        elif now > 60*15:
            now -= 60*15
        #防止出现负数
        elif now < 5:
            now = 60

        print('本次数据更新时间剩余',int(now/60),'分钟','然后每',int(now/60),'分钟整点更新一次')
        #Timer中函数不能加括号
        #错误例子Timer(5, fn_HalfHour（）)

        #每半小时清空元宝数量
        self.addIP()
        self.getAllIP()
        # try:
        self.sendMSG()
        # except:
        #     print('数据传送失败，远程服务器未开器')
        self.top = {}
        self.Json = {}
        self.array.clear()
        self.big_timerStart = threading.Timer(now, self.fn_HalfHour).start()


    def cancel(self):
        self.big_timerStart.cancel()
        self.little_timerStart.cancel()

    # 剔除重复元宝
    def rejectRepeat(self):
        temp_top = self.top.copy()
        temp_society = self.Json.copy()
        for k, v in self.top.items():
            for j, y in self.Json.items():
                if k == j and v == y:
                    temp_top.pop(k)
        l, m = Counter(temp_top), Counter(temp_society)
        # 10分钟的总元宝和帐号数据
        self.Json = dict(l + m)

    #获取RunGate目录所有txt
    def getRunGate(self):
        rootdir = r"%sRunGate" %self.category
        newfile = r"%sRunGate\today.txt" %self.category
        path = []
        for root, dirs, files in os.walk(rootdir):
            for file in files:
                filex = file.split('.')
                filelens = filex[len(filex) - 1]
                if filelens == 'txt':
                    path.append(os.path.join(root, file))
        f = open(newfile, 'w')
        for file in path:
            for line in open(file):
                f.writelines(line)
        f.close()





    #集成增加IP，用户名，机器码
    def addIP(self):
        self.getRunGate()
        for k ,key in self.Json.items():
            print('Json', self.Json)
            jsonC = {}
            self.getIP(k)
            self.getMachineID(k)
            self.getCharaterName(k)
            jsonC['username'] = k
            jsonC['元宝'] = key
            jsonC['ip'] = self.IP
            jsonC['机器码'] = self.machine
            jsonC['character'] = self.charaterName

            self.array.append(jsonC)




    #获取所有登录的IP
    def getAllIP(self):
        # file = r"%stoday.txt"%self.category
        file = r"%sRunGate\today.txt" % self.category
        user = 'IP:'
        with codecs.open(file, "r", encoding="ansi") as f:
            data = f.readlines()
            for dataline in data:
                r = str(re.findall(user, dataline)).replace('[\'', '').replace('\']', '')
                if r == user:
                    account = re.search('IP:', dataline).span()
                    charater = re.search('机器码:', dataline).span()
                    begin = int(account[1])
                    end = int(charater[0] - 1)
                    ip = dataline[begin:end]
                    self.allIP.add(ip)
                else:
                    self.IP = ''

    #获取账号IP
    def getIP(self,user):
        # file = r"%stoday.txt"%self.category
        file = r"%sRunGate\today.txt" % self.category
        user = user
        with codecs.open(file, "r", encoding="ansi") as f:
            data = f.readlines()
            for dataline in data:
                r = str(re.findall(user, dataline)).replace('[\'', '').replace('\']', '')
                if r == user:
                    account = re.search('IP:', dataline).span()
                    charater = re.search('机器码:', dataline).span()
                    begin = int(account[1])
                    end = int(charater[0] - 1)
                    ip = dataline[begin:end]
                    self.IP = ip
                    break
                else:
                    self.IP = ''
    #获取机器码
    def getMachineID(self,user):
        # file = r"%stoday.txt"%self.category
        file = r"%sRunGate\today.txt" % self.category
        user = user
        with codecs.open(file, "r", encoding="ansi") as f:
            data = f.readlines()
            for dataline in data:
                r = str(re.findall(user, dataline)).replace('[\'', '').replace('\']', '')
                if r == user:
                    account = re.search('机器码:', dataline).span()
                    try:
                        charater = re.search('用户机器码:', dataline).span()
                    except :
                        #如果没有结束索引值，直接取最后一个，并+1
                        charater2 = re.search('.$',dataline).span()
                        a = [charater2[0]+1,charater2[1]]
                        charater = a
                    begin = int(account[1])
                    end = int(charater[0] - 1)
                    mc = dataline[begin:end]
                    self.machine = mc
                    break
                else:
                    self.machine = ''

    #发送给服务器
    def sendMSG(self):
        import json

        url = "http://ambulance176.site/legendattach/test"
        self.servername = self.getServerName()
        print('SendMSGarray',self.array)
        print('SendMSG AllIP',self.allIP)
        print('SendMSG AllIP',self.servername)

        headers = {'Content-Type': 'application/json'}
        data = {
            "array":self.array,
            "allip":list(self.allIP),
            "servername":self.servername
        }

        response = requests.post(url, headers=headers,data=json.dumps(data))
        print('发送成功')
        print('提示码：',response)

    #获取角色名
    def getCharaterName(self,user):
        # file = r"%stoday.txt"%self.category
        file = r"%sRunGate\today.txt" % self.category
        user = user
        with codecs.open(file, "r", encoding="ansi") as f:
            data = f.readlines()
            for dataline in data:
                r = str(re.findall(user, dataline)).replace('[\'', '').replace('\']', '')
                if r == user:
                    account = re.search('角色:', dataline).span()
                    charater = re.search('IP:', dataline).span()
                    begin = int(account[1])
                    end = int(charater[0] - 1)
                    ip = dataline[begin:end]
                    self.charaterName = ip
                    break
                else:
                    self.charaterName = ''


    #获取服务器名
    def getServerName(self):
        with open("%s\DBServer\dbsrc.ini"%self.category, 'r') as gold:
            text = gold.readlines()
            start = re.search('ServerName', str(text)).span()
            end = re.search('ServerAddr', str(text)).span()
            start = start[1]+1
            end = end[0] - 6
            strText = str(text)
            servername = strText[start:end]
            return servername

    def getGold(self):
        num1 = [i for i in range(1, 10)]
        num2 = [i for i in range(10, 100, 10)]
        num3 = [i for i in range(100, 1000, 100)]
        num4 = [i for i in range(1000, 10000, 1000)]
        num5 = [i for i in range(10000, 100000, 10000)]
        top = {}
        society = [list(num1),list(num2),list(num3),list(num4),list(num5)]
        for j in society:
            for i in j:
                result = self.getGoldAndUsername(i)
                try:
                    x,y = Counter(result),Counter(top)
                    top = dict(x+y)
                except:
                    pass
        self.top = top

    #获取元宝公用函数
    def getGoldAndUsername(self,i):
        try:
            with open('%s%s.txt'%(self.gold,i), 'r') as name:
                file = name.readlines()
                top = {}

                for f in file:
                    if f != '\n':
                        username = f.replace('\n', '')
                        temp = {}
                        temp[username] = i
                        x,y = Counter(top),Counter(temp)
                        top = dict(x+y)
                return top
        except:
            pass

if __name__ == "__main__":
    continues = True

    category = input('请严格输入服务端目录，例如：D:\\MirServser\\ ：')
    gold = input('请输入元宝目录，例如：C:\\Users\\Administrator\\Desktop\\176\\MirServer\\，如默认‘HF元宝’的目录请直接按回车：')
    try:
        with open('%s%s.txt' % (gold, 20), 'r') as name:
            file = name.readlines()
    except FileNotFoundError:
        category = input('输入有误，请确认目录正常或已创建了元宝路径 ：')
        try:
            with open('%s%s.txt' % (gold, 20), 'r') as name:
                file = name.readlines()
        except FileNotFoundError:
            print('超过错误次数，请重新打开本程序')


    sync = Synchronize(category=category,gold=gold)
    sync.fn()
    sync.fn_HalfHour()


# 1.pip install pyInstaller
# 2.pyinstaller -F .py  打包exe命令，cmd黑窗口


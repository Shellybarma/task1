import pickle
from threading import Thread,Lock
from Queue import Queue
import requests
from lxml import html
from requests import adapters
import re
import time


global que, flag,threadLock
threadLock = Lock()
que = Queue(maxsize=60000)
flag = False


def getorgandnamesp(p):
    dr = re.compile(r'\(|\)|\.|\:|\;|\<|\>|\~')
    p = dr.sub(' ', p)
    return p.split(" ")

def gethtml(URL,aname,org):
    try:
        s = requests.session()
        s.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3051.400 QQBrowser/9.6.11301.400'}
        html = s.get(url=URL, allow_redirects=True)
        if 300 <= html.status_code < 400:
            u = html.headers['location']
        else:
            u = html.url
        html.encoding = "utf8"
        textdata = html.text
        dr = re.compile(r'<script.*?script>', re.S)
        textdata = dr.sub(' ', textdata)
        dr = re.compile(r'<[^>]+>', re.S)
        textdata = dr.sub(' ', textdata)
        dr = re.compile(u'\s+', re.S)
        textdata = dr.sub(' ', textdata)
        dr = re.compile(aname, re.I)
        textdata = dr.sub('nAme', textdata)
        name_sp = getorgandnamesp(aname)
        for nsp in name_sp:
            if nsp.__len__() > 1:
                dr = re.compile(nsp, re.I)
                textdata = dr.sub('nAmesp', textdata)
        dr = re.compile(org, re.I)
        textdata = dr.sub('oRg', textdata)
        org_sp = getorgandnamesp(org)
        for osp in org_sp:
            if osp.__len__() > 1:
                dr = re.compile(osp, re.I)
                textdata = dr.sub('oRgsp', textdata)
        s.close()
        return u,textdata
    except Exception as what:
        s.close()
        return None,None

class MyThread(Thread):
    def __init__(self,path):
        Thread.__init__(self)
        self.writer = open(path,"w")
    def run(self):
        global flag,threadLock,que
        while True:
            if not que.empty():
                [url,hurl,id,name,org] = que.get()
                u,html = gethtml(url,name,org)
                if u==None and html ==None:
                    continue
                if u ==hurl:
                    w = id + "\t" + html + "\t1\n"
                else:
                    w = id + "\t" + html + "\t0\n"
                self.writer.writelines(w)
            else:
                if flag == True:
                    self.writer.close()
                    break
                else:
                    time.sleep(0.1)



def getpreurls(URL):
    try:
        session = requests.session()
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3051.400 QQBrowser/9.6.11301.400'}
        page = session.get(url=URL, allow_redirects=False)
        data = page.text.encode("utf-8")
        tree = html.fromstring(data)
        xpath = '/html/body//div[@id = "main"]/div/div[@class ="mw"]/div[@id ="rcnt"]/div[@class ="col"]/div[@id ="center_col"]/div[@class ="med"]/div[@id ="search"]/div/div/div/div[@class = "_NId"]/div[@class = "srg"]/div/div/div/h3/a/@href '
        urls = list(tree.xpath(xpath))
        session.close()
        return [noinList(u) for u in urls]
    except Exception, what:
        return []

def noinList(url):
    disList = ["https://www.facebook.com", "https://www.linkedin.com"]
    for l in disList:
        if url.find(l) != -1:
            return None
    return url

if __name__ == '__main__':

    u,t = gethtml("https://www.baidu.com/home/news/data/newspage?nid=9017416057025772472&n_type=0&p_from=1&dtype=-1","aa","ss")
    print t
    exit()
    file = open(r"C:\Users\Shellybarma\Downloads\8.20\training.txt")
    file2 = open(r"C:\Users\Shellybarma\Downloads\8.20\validation.txt")
    text = file.readlines()
    text2 = file2.readlines()

    threads = []
    thread_num = 16

    for i in xrange(thread_num):
        w = r"C:\Users\Shellybarma\Downloads\8.32\\" +str(i)+".txt"
        threads.append(MyThread(w))
    for i in threads:
        i.start()

    num = 0
    url_num =0
    len = text.__len__()/11
    start_time = time.time()
    while text:
        lines = text[:10]
        text = text[11:]
        id = lines[0][4:lines[0].__len__() - 1]
        name = lines[1][6:lines[1].__len__() - 1]
        org = lines[2][5:lines[2].__len__() - 1]
        surl = lines[3][21:lines[3].__len__() - 1]
        hurl = lines[4][10:lines[4].__len__() - 1]
        urls = getpreurls(surl)
        m = 0
        for url in urls:
            if url == None:
                continue
            que.put([url,hurl,id,name,org])
            url_num += 1
            m += 1
            if m >=3:
                break
        num += 1
        t = (time.time() - start_time) * (6000.0 - num) / num / 3600
        print num,"-th,queue size",que.qsize(),"/",url_num," ",t
        if num>50:
            break

    while not que.empty():
        print que.qsize()
        time.sleep(0.5)
    flag = True
    print "wait all jobs finish", ("time:%.2gs" % (time.time() - start_time))
    for i in threads:
        i.join()
    print "finish all jobs,with", thread_num, "need:", ("time:%.2gs" % (time.time() - start_time))







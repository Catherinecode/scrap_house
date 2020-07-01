# coding=utf-8
# 抓取二手房列表

import pandas as pd
import os
from selenium import webdriver
import numpy as np
import _thread
from selenium.webdriver.support.wait import WebDriverWait

def sub_resale_list_func(driver,communityid,filetowrite,province,lock):
    try:
        curnum = 0
        with open(filetowrite,'a+') as f:
            for subweb in communityid:
                print('现在开始抓取%s'%subweb)
                info = []
                web_outcome = 'https://' + province +'.ke.com/chengjiao/' + 'c' + str(subweb)+'/'
                driver.get(web_outcome)
                currurl = driver.current_url
                if currurl == web_outcome:

                    try:
                        WebDriverWait(driver, 20).until(
                            lambda driver: driver.find_element_by_xpath("//div[@class='content']/div[@class='leftContent']//ul[@class='listContent']"))
                    finally:
                        select = driver.find_element_by_xpath("//div[@class='content']/div[@class='leftContent']//ul[@class='listContent']")

                    lilist = select.find_elements_by_xpath('./li')
                    if len(lilist) > 0:
                        for link in lilist:
                            linkadj = link.find_element_by_xpath("./div[@class='info']/div[@class='title']/a")
                            value = linkadj.get_attribute('href')
                            id1 = value.split('/')
                            id2 = id1[-1].split('.')
                            info.append(id2[0])
                        select = driver.find_elements_by_xpath("//div[@class='page-box house-lst-page-box']/a")
                        s = len(select)
                        if s > 1:
                            for i in range(s-1):
                                subweb_outcome = 'https://' + province + '.ke.com/chengjiao/pg' + str(2 + i) + 'c' + str(subweb) + '/'
                                driver.get(subweb_outcome)
                                try:
                                    WebDriverWait(driver, 20).until(
                                        lambda driver: driver.find_element_by_xpath("//div[@class='content']/div[@class='leftContent']"
                                                                         "//ul[@class='listContent']"))
                                finally:
                                    select = driver.find_element_by_xpath("//div[@class='content']/div[@class='leftContent']"
                                                                         "//ul[@class='listContent']")

                                lilist = select.find_elements_by_xpath('./li')
                                if len(lilist) > 0:
                                    for link in lilist:
                                        linkadj = link.find_element_by_xpath("./div[@class='info']/div[@class='title']/a")
                                        value = linkadj.get_attribute('href')
                                        id1 = value.split('/')
                                        id2 = id1[-1].split('.')
                                        info.append(id2[0])

                        communityidlist = [subweb] * len(info)
                        infoadj = list(zip(communityidlist,info))

                        for subinfo in infoadj:
                            subcurinfostr = ' '.join([str(sub) for sub in subinfo])
                            f.write(subcurinfostr)
                            f.write('\n')
                    curnum += 1
                    print('%s小区的二手房列表抓取成功，还剩下%s个小区需要抓取' % (subweb, len(communityid) - curnum))

                else:
                    curnum += 1
                    print('%s小区网页不存在' % id)
    finally:
        lock.release()

def resale_list_func(driverpath,filetoread,filetowrite,province,threadnum):

    if os.path.exists(filetowrite):
        with open(filetowrite, 'r') as f:
            resale_list_codelist = f.readlines()
        codehavedone = [code.split('\n')[0].split(' ')[0] if '\n' in code else code.split(' ')[0] for code in
                        resale_list_codelist]
    else:
        codehavedone = []
    with open(filetoread,'r') as f:
        community_list = f.readlines()
        communityid = [code.split('\n')[0].split(' ')[0] if '\n' in code else code.split(' ')[0] for code in community_list]
    communityid = list(set(communityid).difference(set(codehavedone)))

    driverdict = {}
    for subthread in range(threadnum):
        driverdict['driver' + str(subthread)] = \
            webdriver.Chrome(executable_path=driverpath)

    communityiddict = {}
    block = np.ceil(len(communityid) / threadnum)
    for subthread in range(threadnum):
        try:
            communityiddict['communityid' + str(subthread)] = communityid[
                                                              int(block * subthread): int(block * (subthread + 1))]
        except:
            communityiddict['communityid' + str(subthread)] = communityid[int(block * subthread):]

    filetowritedict = {}
    for subthread in range(threadnum):
        filetowritedict[filetowrite.split('.')[0] + str(subthread)] = filetowrite.split('.')[0] + str(subthread) + str(
            '.') + filetowrite.split('.')[1]

    locks = []
    for i in range(threadnum):
        lock = _thread.allocate_lock()
        lock.acquire()
        locks.append(lock)

    for subthread in range(threadnum):
        try:
            _thread.start_new_thread(sub_resale_list_func, (driverdict['driver' + str(subthread)],
                                                              communityiddict['communityid' + str(subthread)],
                                                              filetowritedict[
                                                                  filetowrite.split('.')[0] + str(subthread)],
                                                              province, locks[subthread],))
        except:
            print("Error: 无法启动线程")
            driverdict['driver' + str(subthread)].close()

    for i in range(threadnum):
        while locks[i].locked():
            pass

    with open(filetowrite, 'a+') as f:
        for subthread in range(threadnum):
            with open(filetowritedict[filetowrite.split('.')[0] + str(subthread)], 'r') as g:
                data = g.readlines()
            for subdata in data:
                f.write(subdata)
            os.remove(filetowritedict[filetowrite.split('.')[0] + str(subthread)])
            try:
                driverdict['driver' + str(subthread)].close()
            except:
                continue

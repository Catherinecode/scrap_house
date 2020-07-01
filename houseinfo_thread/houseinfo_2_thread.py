# coding=utf-8
# 用于抓取小区的详细信息
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import numpy as np
import _thread
import re

def sub_community_all_func(driver, communityid, filetowrite, province,lock):
    try:
        with open(filetowrite, 'a+') as f:
            curnum = 0
            for id in communityid:
                web_outcome = 'https://' + province + '.ke.com/xiaoqu/' + str(id) + '/'
                driver.get(web_outcome)
                currurl = driver.current_url
                if currurl == web_outcome:

                    info = []
                    info.append(id)
                    try:
                        WebDriverWait(driver, 20).until(
                            lambda driver: driver.find_element_by_xpath("//div[@class='content']/div[1]"))
                    finally:
                        select = driver.find_element_by_xpath("//div[@class='content']/div[1]")
                    info.extend(select.text.split('\n'))

                    try:
                        WebDriverWait(driver, 20).until(
                            lambda driver: driver.find_elements_by_xpath("//div[@class='fl l-txt']/a[3]"))
                    finally:
                        select = driver.find_elements_by_xpath("//div[@class='fl l-txt']/a[3]")
                        select2 = driver.find_elements_by_xpath("//div[@class='fl l-txt']/a[4]")
                    for link in select:
                        info.append(link.text)
                    for link in select2:
                        info.append(link.text)

                    select = driver.find_elements_by_xpath("//span[@class='xiaoquUnitPrice']")
                    if select == []:
                        info.append([])
                    else:
                        for link in select:
                            info.append(link.text)
                    try:
                        WebDriverWait(driver, 20).until(
                            lambda driver: driver.find_elements_by_xpath("//div[@class='xiaoquInfoItem']/span[2]"))
                    finally:
                        select = driver.find_elements_by_xpath("//div[@class='xiaoquInfoItem']/span[2]")
                    for link in select:
                        info.append(link.text)

                    lalo = driver.find_elements_by_xpath("//script[@type='text/javascript']")[-1]
                    info.extend(re.findall(r'\d+\.\d+', lalo.get_attribute('textContent')))

                    subcurinfostr = '\t'.join([str(sub) for sub in info])
                    f.write(subcurinfostr)
                    f.write('\n')

                    curnum += 1
                    print('%s小区详细信息抓取成功，还剩下%s个小区需要抓取' % (id, len(communityid) - curnum))
                else:
                    curnum += 1
                    print('%s小区网页不存在'%id)

    finally:
        lock.release()


def community_all_func(driverpath,filetoread,filetowrite,province,threadnum):

    if os.path.exists(filetowrite):
        with open(filetowrite,'r') as f:
            community_detail_codelist = f.readlines()
        codehavedone = [code.split('\n')[0].split('\t')[0] if '\n' in code else code.split('\t')[0] for code in community_detail_codelist]
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
    block = np.ceil(len(communityid)/threadnum)
    for subthread in range(threadnum):
        try:
            communityiddict['communityid' + str(subthread)] = communityid[int(block * subthread) : int(block * (subthread + 1))]
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
            _thread.start_new_thread(sub_community_all_func, (driverdict['driver' + str(subthread)],
                                 communityiddict['communityid' + str(subthread)],
                                filetowritedict[filetowrite.split('.')[0] + str(subthread)],
                                                              province,locks[subthread],))
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
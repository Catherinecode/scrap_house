# coding=utf-8
# 用于爬取各个小区的租房成交记录
import os
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
import numpy as np
import _thread


def sub_rental_list_func(driver,communityidlist,filetowrite,province,lock):

    web_outcome = 'https://' + province + '.lianjia.com/xiaoqu/'
    try:
        with open(filetowrite,'a+') as f:
            curnum = 0
            for cid in communityidlist:
                webrequest = web_outcome + str(cid)
                driver.get(webrequest)
                currurl = driver.current_url
                if currurl == webrequest:
                    try:
                        session = driver.find_element_by_xpath('//div[@class = "rentListContent clear"]/div[1]/a')
                    except:
                        curnum += 1
                        f.write(str(cid) + ' ')
                        f.write('\n')
                        print('%s没有租房信息' % cid)
                        continue
                    hrefrent = session.get_attribute('href')
                    driver.get(hrefrent)
                    hrefdealPrice = driver.find_element_by_xpath('//div[@class = "detailPageTab"]/ul[1]')
                    select = hrefdealPrice.find_element_by_xpath("./li/a[contains(text(), '小区成交')]")
                    hrefdealPrice = select.get_attribute('href')
                    driver.get(hrefdealPrice)

                    '''
                    try:
                        WebDriverWait(driver, 10).until(
                            lambda driver: driver.find_element_by_xpath('//span[@class = "resblockDeal select"]'))
                    finally:
                        session = driver.find_element_by_xpath('//span[@class = "resblockDeal select"]')
                    session.click()
                    '''
                    curinfo = []

                    try:
                        try:
                            WebDriverWait(driver, 10).until(
                                lambda driver: driver.find_element_by_xpath('//div[@id = "resblockDeal"]/span[@class = "more"]'))
                        finally:
                            checkmore = driver.find_element_by_xpath('//div[@id = "resblockDeal"]/span[@class = "more"]')
                            checkmore.click()
                        session = driver.find_elements_by_xpath('//div[@id = "resblockDeal"]//div[@class = "list"]/div')

                        for ss in session:
                            code = ss.find_element_by_xpath('./div[@class="house"]/a').get_attribute('href').split('/')[-1].split('.')[0]
                            cdate = ss.find_element_by_xpath('./div[@class= "date"]').text
                            curinfo.append([cid,code,cdate])

                    except:
                        session = driver.find_elements_by_xpath('//div[@id = "resblockDeal"]//div[@class = "list"]/div')
                        if len(session) > 0:
                            for ss in session:
                                code = ss.find_element_by_xpath('./div[@class="house"]/a').get_attribute('href').split('/')[-1].split('.')[0]
                                cdate = ss.find_element_by_xpath('./div[@class= "date"]').text
                                curinfo.append([cid, code, cdate])
                        else:
                            curnum += 1
                            print('%s没有租房信息' % cid)
                            f.write(str(cid) + ' ')
                            f.write('\n')
                            continue
                    curnum += 1

                    for subcurinfo in curinfo:
                        subcurinfostr = ' '.join([str(sub) for sub in subcurinfo])
                        f.write(subcurinfostr)
                        f.write('\n')

                    print('%s爬取成功，还有%s个小区的成交记录需要爬取'%(cid,len(communityidlist)-curnum))
                else:
                    curnum += 1
                    print('%s小区网页不存在' % cid)
    finally:
        print('所有小区爬取成功')
        lock.release()


def rental_list_func(driverpath,filetoread,filetowrite,province,threadnum):
    if os.path.exists(filetowrite):
        with open(filetowrite, 'r') as f:
            rent_list_codelist = f.readlines()
        codehavedone = [code.split('\n')[0].split(' ')[0] if '\n' in code else code.split(' ')[0] for code in
                        rent_list_codelist]
    else:
        codehavedone = []
    with open(filetoread,'r') as f:
        community_list = f.readlines()
        communityidlist = [code.split('\n')[0].split(' ')[0] if '\n' in code else code.split(' ')[0] for code in community_list]
    communityidlist = list(set(communityidlist).difference(set(codehavedone)))

    driverdict = {}
    for subthread in range(threadnum):
        driverdict['driver' + str(subthread)] = \
            webdriver.Chrome(executable_path=driverpath)

    communityiddict = {}
    block = np.ceil(len(communityidlist) / threadnum)
    for subthread in range(threadnum):
        try:
            communityiddict['communityid' + str(subthread)] = communityidlist[
                                                              int(block * subthread): int(block * (subthread + 1))]
        except:
            communityiddict['communityid' + str(subthread)] = communityidlist[int(block * subthread):]

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
            _thread.start_new_thread(sub_rental_list_func, (driverdict['driver' + str(subthread)],
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

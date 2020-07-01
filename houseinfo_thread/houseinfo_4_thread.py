# coding=utf-8
# 用于爬取小区的二手房的详细信息
import os
import re
from selenium import webdriver
import numpy as np
import _thread
from selenium.webdriver.support.wait import WebDriverWait

def sub_resale_detail_func(driver,resale_list,filetowrite1,filetowrite2,province,lock):

    try:
        with open(filetowrite1, 'a+') as resale_detail_file:
            with open(filetowrite2, 'a+') as resale_feature_file:
                curnum = 0
                for subweball in resale_list:
                    print('开始收集%s'%subweball)

                    inform = []
                    resale_feature = []
                    resale_feature.append(subweball[0])
                    resale_feature.append(subweball[1])
                    inform.append(subweball[0])
                    subweb = subweball[1]
                    web_outcome = 'https://' + province + '.lianjia.com/chengjiao/'+ subweb +'.html'
                    driver.get(web_outcome)
                    inform.append(subweb)

                    try:
                        WebDriverWait(driver, 20).until(
                            lambda driver: driver.find_element_by_xpath("//div[@class='house-title']/div[@class='wrapper']"))
                    finally:
                        select = driver.find_element_by_xpath("//div[@class='house-title']/div[@class='wrapper']")
                    inform.append(select.find_element_by_xpath("./h1").get_attribute('textContent'))
                    inform.extend(select.find_element_by_xpath("./span").get_attribute('textContent').split(' '))


                    try:
                        select2 = driver.find_element_by_xpath("//div[@class='price']/span[@class='dealTotalPrice']/i")
                        inform.append(select2.text)
                    except:
                        inform.append('暂无信息')
                    try:
                        select3 = driver.find_element_by_xpath("//div[@class='price']/b")
                        inform.append(select3.text)
                    except:
                        inform.append('暂无信息')

                    select4 = driver.find_elements_by_xpath("//div[@class='msg']/span/label")
                    if len(select4) > 0:
                        for link in select4:
                            inform.append(link.text)
                    else:
                        inform.extend(['暂无信息']*6)

                    select5 = driver.find_elements_by_xpath("//div[@class='content']/ul/li")
                    for link in select5:
                        inform.append(link.text[4:])

                    select6 = driver.find_elements_by_xpath("//ul[@class='record_list']/li")
                    for link in select6:
                        try:
                            inform.append(link.find_element_by_xpath("./span[@class='record_price']").text)
                        except:
                            inform.append('暂无信息')
                        try:
                            recorddetail = link.find_element_by_xpath("./p[@class='record_detail']").text
                            recorddetaillist = recorddetail.split(',')
                            if len(recorddetaillist) > 1:
                                inform.append(re.findall(r'\d+', recorddetaillist[0])[0])  # 面积
                                inform.append(re.findall(r'\d+\-?\d+\-?\d+', recorddetaillist[1])[0])  # 日期
                            if len(recorddetaillist) == 1:
                                if '-' in recorddetail:
                                    inform.append('暂无信息')
                                    inform.append(re.findall(r'\d+\-?\d+\-?\d+',recorddetail)[0])
                                else:
                                    inform.append(re.findall(r'\d+', recorddetail)[0])
                                    inform.append('暂无信息')
                            else:
                                inform.extend(['暂无信息']*2)
                        except:
                            inform.append(['暂无信息']*2)


                    select7 = driver.find_elements_by_xpath("//div[@class='introContent showbasemore']/div")
                    resale_feature.extend([link.text.replace('\n', ':') if '\n' in link.text else '无名信息:' + link.text
                                           for link in select7])

                    subcurinfostr = '\t'.join([str(sub) for sub in inform])
                    resale_detail_file.write(subcurinfostr)
                    resale_detail_file.write('\n')

                    subcurinfostr = '\t'.join([str(sub) for sub in resale_feature])
                    resale_feature_file.write(subcurinfostr)
                    resale_feature_file.write('\n')

                    curnum += 1
                    print('%s抓取成功，还剩下%s个二手房需要抓取'%(subweball,len(resale_list) - curnum))


    finally:
        lock.release()

def resale_detail_func(driverpath,filetoread,filetowrite1,filetowrite2,province,threadnum):

    if os.path.exists(filetowrite1):
        with open(filetowrite1,'r') as f:
            resale_detail_codelist = f.readlines()
        codehavedone = [code.split('\n')[0].split('\t')[:2] if '\n' in code else code.split('\t')[:2] for code in resale_detail_codelist]
    else:
        codehavedone = []
    with open(filetoread,'r') as f:
        rentalcode = f.readlines()
    resale_listpre = [rent.split('\n')[0].split(' ') if '\n' in rent else rent.split(' ') for rent in rentalcode]
    resale_list = [resale for resale in resale_listpre if resale not in codehavedone]

    driverdict = {}
    for subthread in range(threadnum):
        driverdict['driver' + str(subthread)] = \
            webdriver.Chrome(executable_path=driverpath)

    communityiddict = {}
    block = np.ceil(len(resale_list) / threadnum)
    for subthread in range(threadnum):
        try:
            communityiddict['communityid' + str(subthread)] = resale_list[
                                                              int(block * subthread): int(block * (subthread + 1))]
        except:
            communityiddict['communityid' + str(subthread)] = resale_list[int(block * subthread):]

    filetowrite1dict = {}
    for subthread in range(threadnum):
        filetowrite1dict[filetowrite1.split('.')[0] + str(subthread)] = filetowrite1.split('.')[0] + str(subthread) + str(
            '.') + filetowrite1.split('.')[1]

    filetowrite2dict = {}
    for subthread in range(threadnum):
        filetowrite2dict[filetowrite2.split('.')[0] + str(subthread)] = filetowrite2.split('.')[0] + str(subthread) + str(
            '.') + filetowrite2.split('.')[1]

    locks = []
    for i in range(threadnum):
        lock = _thread.allocate_lock()
        lock.acquire()
        locks.append(lock)

    for subthread in range(threadnum):
        try:
            _thread.start_new_thread(sub_resale_detail_func, (driverdict['driver' + str(subthread)],
                                                            communityiddict['communityid' + str(subthread)],
                                                            filetowrite1dict[
                                                                filetowrite1.split('.')[0] + str(subthread)],
                                                              filetowrite2dict[
                                                                  filetowrite2.split('.')[0] + str(subthread)],
                                                            province, locks[subthread],))
        except:
            print("Error: 无法启动线程")
            driverdict['driver' + str(subthread)].close()

    for i in range(threadnum):
        while locks[i].locked():
            pass

    with open(filetowrite1, 'a+') as f1:
        with open(filetowrite2, 'a+') as f2:
            for subthread in range(threadnum):
                with open(filetowrite1dict[filetowrite1.split('.')[0] + str(subthread)], 'r') as g1:
                    data = g1.readlines()
                for subdata in data:
                    f1.write(subdata)
                os.remove(filetowrite1dict[filetowrite1.split('.')[0] + str(subthread)])

                with open(filetowrite2dict[filetowrite2.split('.')[0] + str(subthread)], 'r') as g2:
                    data = g2.readlines()
                for subdata in data:
                    f2.write(subdata)
                os.remove(filetowrite2dict[filetowrite2.split('.')[0] + str(subthread)])
                try:
                    driverdict['driver' + str(subthread)].close()
                except:
                    continue
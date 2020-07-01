# coding=utf-8
# 用于爬取各个小区的租房成交记录
import numpy as np
import _thread
import os
from selenium import webdriver

def sub_rentail_detail_func(driver,rentalcode,filetowrite,province,lock):

    web_outcome = 'https://' + province + '.lianjia.com/zufang/'
    curnum = 0
    try:
        with open(filetowrite,'a+') as f:
            for code in rentalcode:
                curinfo = []
                curinfo.extend(code)

                html = web_outcome + code[1] + '.html'
                driver.get(html)

                rentname = driver.find_element_by_xpath('//div[@class = "title-wrapper"]//h1[@class = "main"]').text
                curinfo.append(rentname)
                overview = driver.find_element_by_xpath('//div[@class = "overview"]')
                price = overview.find_element_by_xpath('.//div[@class = "price isRemove"]').text.split('\n')

                if len(price) < 4:
                    price.extend(['暂无信息'] * (4- len(price)))
                curinfo.extend(price)

                detail = overview.find_elements_by_xpath('.//div[@class = "zf-room"]/p')
                curinfo.extend([p.text.split('：')[-1] for p in detail[:4]])
                curinfo.append(detail[-1].text.split('：')[-1])

                introCo = driver.find_elements_by_xpath('//div[@class = "introContent"]/div[1]/div[2]/ul/li')
                curinfo.extend([p.text.split('：')[-1].replace(' ','') for p in introCo])


                subcurinfostr = '\t'.join([str(sub) for sub in curinfo])
                f.write(subcurinfostr)
                f.write('\n')
                curnum += 1
                print('%s租房信息爬取成功，还有%s未爬取'%(code,len(rentalcode) - curnum))
    finally:
        print('所有租房信息爬取成功')
        lock.release()

def rentail_detail_func(driverpath,filetoread,filetowrite,province,threadnum):

    if os.path.exists(filetowrite):
        with open(filetowrite, 'r') as f:
            rent_detail_codelist = f.readlines()
        codehavedone = [code.split('\n')[0].split('\t')[:2] if '\n' in code else code.split('\t')[:2] for code in
                        rent_detail_codelist]
    else:
        codehavedone = []

    with open(filetoread, 'r') as f:
        rentalcode = f.readlines()
    rentalcodepre = [rent.split('\n')[0].split(' ') if '\n' in rent else rent.split(' ') for rent in rentalcode]
    rentalcodepre = [rent[:2] for rent in rentalcodepre if len(rent) >= 2 and rent[1] != ' ' and rent[1] != '']
    rentalcode = [rent for rent in rentalcodepre if rent not in codehavedone]

    driverdict = {}
    for subthread in range(threadnum):
        driverdict['driver' + str(subthread)] = \
            webdriver.Chrome(executable_path=driverpath)

    communityiddict = {}
    block = np.ceil(len(rentalcode) / threadnum)
    for subthread in range(threadnum):
        try:
            communityiddict['communityid' + str(subthread)] = rentalcode[
                                                              int(block * subthread): int(block * (subthread + 1))]
        except:
            communityiddict['communityid' + str(subthread)] = rentalcode[int(block * subthread):]

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
            _thread.start_new_thread(sub_rentail_detail_func, (driverdict['driver' + str(subthread)],
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
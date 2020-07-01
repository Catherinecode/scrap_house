# coding=utf-8
# 获得小区列表
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import os
import pickle as pk

def community_list_func(driverpath,province,filetowrite):

    web_outcome = 'https://' + province + '.ke.com/xiaoqu/'
    driver = webdriver.Chrome(executable_path = driverpath)
    driver.get(web_outcome)
    filetoread = filetowrite.split('.txt')[0] + '_dict' + '.pickle'

    try:
        if os.path.exists(filetoread):
            with open(filetoread, 'rb') as f:
                districtdict = pk.load(f)
        else:
            # 抓取所有地区
            district = []
            try:
                WebDriverWait(driver, 20).until(
                    lambda driver: driver.find_elements_by_xpath(
                        "//a[contains(@href, '/xiaoqu/') and contains(@class, 'CLICKDATA') ]"))
            finally:
                select = driver.find_elements_by_xpath(
                    "//a[contains(@href, '/xiaoqu/') and contains(@class, 'CLICKDATA') ]")
            for link in select:
                value = link.get_attribute('href')
                districtvalue = value.split('/')[-2]
                district.append(districtvalue)
            print('所有地区的链接抓取成功，一共有%s个地区' % len(district))

            # 抓取所有地区下的区域
            districtdict = {}
            for subweb in district:
                web_outcome = 'https://' + province + '.ke.com/xiaoqu/' + subweb + '/'
                try:
                    driver.get(web_outcome)
                    try:
                        WebDriverWait(driver, 20).until(
                            lambda driver: driver.find_elements_by_xpath("//div[@data-role='ershoufang']/div[2]/a"))
                    finally:
                        select = driver.find_elements_by_xpath("//div[@data-role='ershoufang']/div[2]/a")
                    for link in select:
                        value = link.get_attribute('href')
                        subdistrictvalue = value.split('/')[-2]
                        districtdict[subdistrictvalue] = {'havedone':0,'page':-1}  # havedone为0表示还没有爬完该区域的数据
                                                                                # page表示要上次爬完的页码
                    print('%s地区下的分区抓取成功' % subweb)
                except:
                    continue
            print('一共有%s个分区' % len(districtdict.keys()))

            with open(filetoread, 'wb') as f:
                pk.dump(districtdict, f, protocol=2)

        with open(filetowrite,'a+') as f:

            # 抓取每个子区域下的小区信息
            for subweb in districtdict.keys():

                if districtdict[subweb]['havedone'] == 0:
                    pagestart = districtdict[subweb]['page']
                    print('现在开始抓取%s的小区列表信息'% subweb)
                    web_outcome = 'https://' + province + '.ke.com/xiaoqu/' + subweb + '/'
                    driver.get(web_outcome)
                    try:
                        select1 = driver.find_elements_by_xpath("//div[@class='page-box house-lst-page-box']/a")[-1]
                        value_while = select1.text
                    except:
                        value_while = 1
                    if value_while != '下一页':
                        for i in list(range(int(value_while)))[(pagestart + 1):]:
                            subweb_outcome = web_outcome + 'pg' + str(1 + i) + '/'
                            driver.get(subweb_outcome)
                            try:
                                WebDriverWait(driver, 10).until(
                                    lambda driver: driver.find_elements_by_xpath("//ul[@class='listContent']/li"))
                            except:
                                continue
                            select_all = driver.find_elements_by_xpath("//ul[@class='listContent']/li")
                            for iselect in select_all:
                                info = []
                                select = iselect.find_element_by_xpath("./div[@class = 'info']/div[@class = 'title']/a")
                                info.append(select.get_attribute('href').split('/')[-2])
                                info.append(select.get_attribute('textContent'))

                                select = iselect.find_element_by_xpath("./div[@class = 'info']/div[@class = 'houseInfo']/a[1]")
                                info.append(select.text)
                                try:
                                    select_ul = iselect.find_element_by_xpath("./div[@class = 'info']/div[@class = 'houseInfo']/a[2]")
                                    info.append(select_ul.text)
                                except:
                                    info.append(str(0))
                                select = iselect.find_element_by_xpath("./div[@class='xiaoquListItemRight']/"
                                                                       "div[@class='xiaoquListItemSellCount']/a[1]/span")
                                info.append(select.get_attribute('textContent'))
                                try:
                                    f.write(' '.join([str(subinfo) for subinfo in info]))
                                except:
                                    f.write(
                                        ' '.join([str(subinfo) for subinfo in info]).encode("gbk", "replace").decode(
                                            'gbk', 'ignore'))
                                f.write('\n')
                            districtdict[subweb]['page'] = i
                        districtdict[subweb]['havedone'] = 1

                    else:
                        i = 0
                        subweb_outcome = web_outcome + 'pg' + str(2 + pagestart) + '/'
                        driver.get(subweb_outcome)
                        while value_while == '下一页':

                            select1 = driver.find_elements_by_xpath("//div[@class='page-box house-lst-page-box']/a")[-1]
                            value_while = select1.text
                            sub = select1.get_attribute('href')
                            i = pagestart + 1 + i

                            try:
                                WebDriverWait(driver, 10).until(
                                    lambda driver: driver.find_elements_by_xpath("//ul[@class='listContent']/li"))
                            except:
                                continue
                            select_all = driver.find_elements_by_xpath("//ul[@class='listContent']/li")
                            for iselect in select_all:
                                info = []
                                select = iselect.find_element_by_xpath("./div[@class = 'info']/div[@class = 'title']/a")
                                info.append(select.get_attribute('href').split('/')[-2])
                                info.append(select.get_attribute('textContent'))

                                select = iselect.find_element_by_xpath("./div[@class = 'info']/div[@class = 'houseInfo']/a[1]")
                                info.append(select.text)
                                try:
                                    select_ul = iselect.find_element_by_xpath("./div[@class = 'info']/div[@class = 'houseInfo']/a[2]")
                                    info.append(select_ul.text)
                                except:
                                    info.append(str(0))
                                select = iselect.find_element_by_xpath("./div[@class='xiaoquListItemRight']/"
                                                                       "div[@class='xiaoquListItemSellCount']/a[1]/span")
                                info.append(select.get_attribute('textContent'))

                                f.write(' '.join([str(subinfo) for subinfo in info]))
                                f.write('\n')
                            districtdict[subweb]['page'] = i
                            driver.get(sub)
                        districtdict[subweb]['havedone'] = 1

    finally:
        with open(filetoread, 'wb') as f:
            pk.dump(districtdict, f, protocol=2)

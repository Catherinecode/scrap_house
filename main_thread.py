import os
import sys
os.chdir('I:\part_work\链家')
sys.path.append('I:\part_work\链家\code')

import os
path = r'I:\part_work\链家\code'
for dirpath,dirnames,filenames in os.walk(path):
    print(dirpath,dirnames,filenames)



from houseinfo_nothread import houseinfo
from houseinfo_thread import houseinfo_2_thread
from houseinfo_thread import houseinfo_3_thread
from houseinfo_thread import houseinfo_4_thread
from houseinfo_thread import houseinfo_5_thread
from houseinfo_thread import houseinfo_6_thread

# 得到community_list信息
# web_outcome：要抓取的网页
# filetowrite：要写入的文件名
driverpath = "E:\chrom\chromedriver_win32\chromedriver.exe"
province = 'bj'  # ShangHai
filetowrite = 'community_list_' + province + '.txt'
houseinfo.community_list_func(driverpath,province,filetowrite)

# 得到community_detail信息
# filetoread：要读取的小区的列表信息
# filetoread：小区的详细信息要写入的文件
driverpath = "E:\chrom\chromedriver_win32\chromedriver.exe"
province = 'bj'
filetoread = 'community_list_' + province + '.txt'
filetowrite = 'community_detail_'+ province + '.txt'
threadnum = 3
houseinfo_2_thread.community_all_func(driverpath,filetoread,filetowrite,province,threadnum)

# 得到community_detail信息
# filetoread：要读取的小区的列表信息
# filetoread：小区的详细信息要写入的文件
driverpath = "E:\chrom\chromedriver_win32\chromedriver.exe"
province = 'bj'
filetoread = 'community_list_' + province + '.txt'
filetowrite = 'resale_list_' + province + '.txt'
threadnum = 1
houseinfo_3_thread.resale_list_func(driverpath,filetoread,filetowrite,province,threadnum)


# 得到小区的二手房信息resale_detail和特征信息resale_feature
driverpath = "E:\chrom\chromedriver_win32\chromedriver.exe"
province = 'bj'
filetoread = 'resale_list_' + province + '.txt'
filetowrite1 = 'resale_detail_' + province + '.txt'
filetowrite2 = 'resale_feature_'+ province + '.txt'
threadnum = 3
houseinfo_4_thread.resale_detail_func(driverpath,filetoread,filetowrite1,filetowrite2,province,threadnum)


# 得到小区的租房信息rental_list
driverpath = "E:\chrom\chromedriver_win32\chromedriver.exe"
province = 'bj'
filetoread = 'community_list_' + province + '.txt'
filetowrite = 'rental_list_' + province + '.txt'
threadnum = 3
houseinfo_5_thread.rental_list_func(driverpath,filetoread,filetowrite,province,threadnum)

# 得到小区的租房信息的详细信息
driverpath = "E:\chrom\chromedriver_win32\chromedriver.exe"
province = 'bj'
filetoread = 'rental_list_' + province + '.txt'
filetowrite = 'rental_detail_' + province + '.txt'
threadnum = 3
houseinfo_6_thread.rentail_detail_func(driverpath,filetoread,filetowrite,province,threadnum)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as options
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
from pandas import DataFrame
import csv
import time

#虛擬瀏覽器設定
#禁止廣告業面
options = options()
prefs = {
    'profile.default_content_setting_values' :
        {
        'notifications' : 2
         }
}
options.add_experimental_option('prefs',prefs)

options.add_argument("--headless") #不開啟瀏覽器，於背景執行
options.add_argument('blink-settings=imagesEnabled=false') #不加載圖片
options.add_argument("--disable-javascript") # 禁用JavaScript



headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
column_list = ['date','time','team_home','team_away','total','over','under']
print('盤口爬蟲開始執行...')




''' 爬取網頁總連結

for year in range(2010,2020):
    print('{}年總網頁搜尋中'.format(year))
    url = 'https://www.oddsportal.com/baseball/usa/mlb-{}/results/#/page/1/'.format(year)
    driver = webdriver.Chrome("./chromedriver.exe", options=options)
    driver.implicitly_wait(10)
    html = driver.get(url)
    html_data = driver.page_source
    driver.close()
    soup = BeautifulSoup(html_data, 'html.parser')
    sel_page_total = int(soup.select('div[id="pagination"] a')[-1]['href'].split('/')[2])
    odds_url_list = []
    for a in range (1,sel_page_total+1):
        try:
            url = 'https://www.oddsportal.com/baseball/usa/mlb-{}/results/#/page/{}/'.format(year, a)
            driver = webdriver.Chrome("./chromedriver.exe", options=options)
            driver.implicitly_wait(10)
            html = driver.get(url)
            print('第{}頁連結爬取中...'.format(a))
            sleep(5)
            html_data = driver.page_source
            driver.quit()
            soup = BeautifulSoup(html_data, 'html.parser')
            sel_url = soup.select('td[class="name table-participant"] a')
            for i in sel_url:
                half_odds = i['href']
                odds_url_list.append("https://www.oddsportal.com" + half_odds + "#over-under;3")
            print('第{}頁搜尋完成'.format(a))
        except:
            break
    url_list = pd.DataFrame(odds_url_list)
    url_list.to_csv(f"Season_%s_url_list .csv" % year, encoding='utf_8_sig')
    print('{}年網頁連結搜尋完成'.format(year))
    print('連結搜尋完成，season {} 共'.format(year) + str(len(odds_url_list)) + '筆網頁資料')

'''



# 爬取內文
for year in range (2017,2009,-1):
    start0 = time.time()
    games_detail = []
    odds_list = []
    odds_list1 = pd.read_csv('Season_{}_url_list .csv'.format(year), encoding='utf-8',index_col=0).values.tolist()
    error_list = []
    error_code = []
    nan_list = []
    error_list2 = []
    error_code2 = []
    # pd.valuse.tolist 輸出為[[url]] 多寫迴圈拆開
    for i in odds_list1:
        for j in i:
            odds_list.append (j)

    for n in odds_list:
        start1 = time.time()
        try:
            driver = webdriver.Chrome("./chromedriver.exe", options=options)
            driver.implicitly_wait(30)
            html = driver.get(n)
            #sleep(5)
            html_data = driver.page_source
            soup = BeautifulSoup(html_data, 'html.parser')
            tables = pd.read_html(html_data)
            data = DataFrame(tables[0])
            team = soup.select('div[id="col-content"] h1')[0].text
            date_all = soup.select('div[id="col-content"] p')[0].text
            team_home = team.split(' - ')[0]
            team_away = team.split(' - ')[1]
            date_day = date_all.split(', ')[1]
            date_time = date_all.split(', ')[2]
            total = data.loc[0, 'Total']
            over_odds = data.loc[0, 'Over']
            under_odds = data.loc[0, 'Under']

            if (float(over_odds) > 2 or float(over_odds) <= 1.8) and len(over_odds) > 1 :
                try:
                    data2 = DataFrame(tables[1])
                    over_odds2 = data2.loc[0, 'Over']
                    under_odds2 = data2.loc[0, 'Under']
                    total2 = data2.loc[0, 'Total']
                    games_detail.append([date_day, date_time, team_home, team_away, total2, over_odds2, under_odds2])
                    print(date_day, date_time, team_home, team_away, total2, over_odds2, under_odds2)
                except:
                    games_detail.append([date_day, date_time, team_home, team_away, total, over_odds, under_odds])
                    print(date_day, date_time, team_home, team_away, total, over_odds, under_odds)
            elif len(over_odds) < 1  :
                nan_list.append(n)
            else:
                games_detail.append([date_day, date_time, team_home, team_away, total, over_odds, under_odds])
                print(date_day, date_time, team_home, team_away, total, over_odds, under_odds)
            print('當前爬蟲進度'+ str(len(games_detail)/len(odds_list)*100) + '%...')

        except Exception as e:
            print(e)
            print(n+'網頁異常請確認')
            error_list.append(n)
            error_code.append(e)
            continue
        finally:
            print('虛擬瀏覽器已關閉')
            driver.quit()
        end1 = time.time()
        print('第%s筆網頁完成，共耗時%0.2f秒'%((len(games_detail)+len(error_list)),end1-start1))


    end0=time.time()
    print('%s賽季爬蟲完成，共%s筆網頁，耗時%0.2f秒' % (year,(len(games_detail) + len(error_list)), end0 - start0))
    print('共' + str(len(error_list)) + '筆網頁異常')
    print('共' + str(len(nan_list)) + '筆網頁賠率空值')
    print('error_list網頁爬蟲開始執行')

    start3 = time.time()
    for error_url in error_list:
        start4 = time.time()
        try:
            driver = webdriver.Chrome("./chromedriver.exe", options=options)
            driver.implicitly_wait(30)
            html = driver.get('error_url')
            # sleep(5)
            html_data = driver.page_source
            soup = BeautifulSoup(html_data, 'html.parser')
            total = soup.select('div[id="odds-data-table"] a ')[0].text.split('Under ')[1]
            under_odds = soup.select('span[class="avg chunk-odd nowrp"] a ')[0].text
            over_odds = soup.select('span[class="avg chunk-odd nowrp"] a ')[1].text
            team = soup.select('div[id="col-content"] h1')[0].text
            date_all = soup.select('div[id="col-content"] p')[0].text
            team_home = team.split(' - ')[0]
            team_away = team.split(' - ')[1]
            date_day = date_all.split(', ')[1]
            date_time = date_all.split(', ')[2]

            if (float(over_odds) > 2 or float(over_odds) <= 1.8 )and len(over_odds) > 1:
                try:
                    over_odds2 = soup.select('span[class="avg chunk-odd nowrp"] a ')[3].text
                    under_odds2 = soup.select('span[class="avg chunk-odd nowrp"] a ')[2].text
                    total2 = soup.select('div[id="odds-data-table"] a ')[4].text.split('Under ')[1]

                    if float(over_odds2) > 2 or float(over_odds2) <= 1.8 :
                        try:
                            over_odds3 = soup.select('span[class="avg chunk-odd nowrp"] a ')[5].text
                            under_odds3 = soup.select('span[class="avg chunk-odd nowrp"] a ')[4].text
                            total3 = soup.select('div[id="odds-data-table"] a ')[8].text.split('Under ')[1]
                            games_detail.append(
                                [date_day, date_time, team_home, team_away, total3, over_odds3, under_odds3])
                            print([date_day, date_time, team_home, team_away, total3, over_odds3, under_odds3])
                        except:
                            games_detail.append(
                                [date_day, date_time, team_home, team_away, total2, over_odds2, under_odds2])
                            print([date_day, date_time, team_home, team_away, total2, over_odds2, under_odds2])
                    else:
                        games_detail.append(
                            [date_day, date_time, team_home, team_away, total2, over_odds2, under_odds2])
                        print([date_day, date_time, team_home, team_away, total2, over_odds2, under_odds2])
                except:
                    games_detail.append([date_day, date_time, team_home, team_away, total, over_odds, under_odds])
                    print(date_day, date_time, team_home, team_away, total, over_odds, under_odds)

            elif len(over_odds) < 1:
                nan_list.append(error_url)
            else:
                games_detail.append([date_day, date_time, team_home, team_away, total, over_odds, under_odds])
                print(date_day, date_time, team_home, team_away, total, over_odds, under_odds)

        except Exception as e:
            print(e)
            print(error_url + '網頁異常請確認')
            error_list2.append(error_url)
            error_code2.append(e)
            continue
        finally:
            print('虛擬瀏覽器已關閉')
            driver.quit()
        end4 = time.time()
        print('網頁爬蟲完成，共耗時%0.2f秒' % (end4 - start4))

    end3 = time.time()
    print('%s賽季爬蟲完成，共%s筆網頁，耗時%0.2f秒' % (year, (len(games_detail) + len(error_list) + len(error_list2)), end3 - start3))
    print('共' + str(len(error_list2)) + '筆網頁異常')
    print('共' + str(len(nan_list)) + '筆網頁賠率空值')

    data = pd.DataFrame(games_detail,columns=column_list)
    data.to_csv(f"Season_%s_data.csv"%year, encoding='utf_8_sig')

    error_csv = pd.DataFrame(error_list2)
    error_csv.to_csv(f"Season_%s_error_list.csv" % year, encoding='utf_8_sig')

    error_code_csv = pd.DataFrame(error_code2)
    error_code_csv.to_csv(f"Season_%s_error_code.csv" % year, encoding='utf_8_sig')

    nan_csv = pd.DataFrame(nan_list)
    nan_csv.to_csv(f"Season_%s_nan_list.csv" % year, encoding='utf_8_sig')

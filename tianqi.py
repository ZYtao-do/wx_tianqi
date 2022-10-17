'''
天气：{{weather.DATA}} 温度：{{temperature.DATA}} 湿度：{{humidity.DATA}} 风度：{{wind.DATA}} 空气质量：{{airquality.DATA}} 距离她的生日还有 {{brithday_left.DATA}}天 {{eng.DATA}} {{chinese.DATA}} {{words.DATA}}
'''
from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
import sxtwl

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
user_id1 = os.environ["USER_ID1"]
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
    url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
    res = requests.get(url).json()
    current_hour = datetime.now().hour

    if current_hour <= 12:
        weather = res['data']['list'][0]  # 今天
        data = "今日风的属性属于" + weather['wind'] + "\n再重复一次哦，今日最低气温只有" + weather['low'] + "℃，注意你的温度控制，OK？"
        
    elif current_hour > 12:
        weather0 = res['data']['list'][0]
        weather = res['data']['list'][1]  # 明天
        weather1 = res['data']['list'][2]  # 后天
        diffence = weather['low'] - weather0['low']
        if(difference > 0):
            data = "明较今高了" + difference + "℃\n" +
                   "最低气温是" + weather['low'] + "哦，虽然高了一些，但还是注意保暖哦" 
        else:
            data = "明较今低了" + difference + "℃\n" +
                   "最低气温只有" + weather['low'] + "哦，裹紧你的小棉袄" 

    return weather['airQuality'], weather['weather'], weather['humidity'], weather['wind'], \
           weather['low'], weather['high'], data


def get_birthday():
    if date.today().month > 6:
        day = sxtwl.fromLunar(date.today().year + 1, 6, 23)
        birthday = str(day.getSolarMonth()) + "-" + str(day.getSolarDay())
        next = datetime.strptime(str(date.today().year + 1) + "-" + birthday, "%Y-%m-%d")
    else:
        day = sxtwl.fromLunar(date.today().year, 6, 23)
        birthday = str(day.getSolarMonth()) + "-" + str(day.getSolarDay())
        next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")

    birthday_text = "公历：%d年%d月%d日" % (day.getSolarYear(), day.getSolarMonth(), day.getSolarDay())
    print(birthday_text)

    # print(next)
    # print(today)
    # if next < datetime.now():
    #     next = next.replace(year=next.year + 1)

    return (next - today).days


def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


def get_jsyyh():
    url = "http://open.iciba.com/dsapi/"
    word = requests.get(url)
    content = word.json()["content"]
    note = word.json()["note"]
    return content, note


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
airquality, wea, humidity, wind, low, high, w_data = get_weather()
tem = str(low) + "~" + str(high) + " ℃"
print(tem)
eng, chinese = get_jsyyh()
birthday_left = str(get_birthday())
data = {"airquality": {"value": airquality}, "weather": {"value": wea},
        "temperature": {"value": tem, "color": get_random_color()}, "humidity": {"value": humidity},
        "wind": {"value": wind}, "birthday": {"value": birthday_left, "color": get_random_color()},
        "eng": {"value": eng, "color": get_random_color()}, "chinese": {"value": chinese},
        "words": {"value": get_words(), "color": get_random_color()}, "w_data": {"value": w_data, "color": get_random_color()}}

print(data)
res = wm.send_template(user_id, template_id, data)
res = wm.send_template(user_id1, template_id, data)
print(res)

import cv2
import datetime

width = 15
height = 13

monthDict = {
    9:(36,253),
    10:(169,253),
    11:(303,253),
    12:(437,253),
    1:(36,377), 
    2:(169,377),
    3:(303,377),
    4:(436,367),
    5:(36,502),
    6:(169,502)
}

def resetCalendar():
    img = cv2.imread("backup.png")
    cv2.imwrite("calendar.png", img)


def markCalendar(month,weekmonth,weekday):
    month = monthDict[month]#datetime.datetime.now().month]
    weekmonth = weekmonth-1

    x = month[0]+((width+2)*weekday)
    y = month[1]+((height+2)*weekmonth)
    img = cv2.imread("calendar.png")
    cv2.rectangle(img,(x,y),(x+width,y+height),(0,0,255),-1)
    cv2.imwrite("calendar.png", img)

import pytz
tz = pytz.timezone("America/Los_Angeles")


def monthMap(m):
    return ((m + 3) % 12) + 2

def weekOfMonth(date):
    first_day_of_month = date.replace(day=1)
    adjusted_day = date.day + first_day_of_month.weekday()
    return (adjusted_day - 1) // 7 + 1

now = datetime.datetime.now(tz)
month = monthMap(now.month)

week = weekOfMonth(now.date())
day = now.weekday()+1
markCalendar(now.month,week,day)


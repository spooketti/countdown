import cv2

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
    4:(436,377),
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



import requests, io, zipfile,pandas,os
import redis
from datetime import datetime
from threading import Timer


def download():
    date=get_date()
    url='https://www.bseindia.com/download/BhavCopy/Equity/EQ'+date+'_CSV.ZIP'
    try:
        response=requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        get_data()
        return False
    except requests.exceptions.RequestException as err:
        print('could not get zip file')
        get_data()
        return False

    try:
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        zip_file.extractall()
    except Exception as e:
        print('error during retrieving & parsing the zipfile',e)
        get_data()
        return False

    parse_status=parse_csv(date)
    print('parsing status',parse_status)
    get_data()   #self loop will execute infinitely

    return parse_status

def parse_csv(date):
    pd=pandas.read_csv('EQ'+date+'.csv',usecols=["SC_CODE","SC_NAME","OPEN","HIGH","LOW","CLOSE"])
    os.remove('EQ'+date+'.csv')

    pd['GAIN']=pd['CLOSE']-pd['OPEN']
    pd=pd.sort_values(by=['GAIN'],ascending=0)
    pd['GAIN']=pd['GAIN'].round(2)


    #database = redis.StrictRedis(host='localhost', port=6379, db=0)
    database = redis.StrictRedis(host='pub-redis-18398.dal-05.1.sl.garantiadata.com', port=18398,
                                 password='Enter your password', db=0)
    database.flushall()

    for row in pd.itertuples():
        database.sadd(row.SC_NAME.strip(),
                      dict(SC_CODE=row.SC_CODE, OPEN=row.OPEN, HIGH=row.HIGH, LOW=row.LOW, CLOSE=row.CLOSE,GAIN=row.GAIN))
       
    for row in pd.head(10).itertuples():
        database.rpush('top10',
                       dict(SC_NAME=row.SC_NAME.strip(), SC_CODE=row.SC_CODE, OPEN=row.OPEN, HIGH=row.HIGH, LOW=row.LOW,
                            CLOSE=row.CLOSE,GAIN=row.GAIN))
    return True


def get_date():
    x = str(datetime.today())

    date_string=x[8:10]+x[5:7]+x[2:4]  #get date in ddmmyy format


    return date_string




def get_data():

    x = datetime.today()
    y = x.replace(day=x.day + 1, hour=16, minute=0, second=0, microsecond=0)
    delta_t = y - x
    secs = delta_t.seconds + 1
    print(secs)

    t = Timer(secs,download) #run periodically
    t.start()


    return





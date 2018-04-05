import cherrypy,os
import redis,ast
from mako.template import Template
import json


from bhavcopy import download ,get_data


class BhavCopyServer(object):
    def __init__(self):
        #self.database = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.database = redis.StrictRedis(host='pub-redis-18398.dal-05.1.sl.garantiadata.com', port=18398,
                                     password='Enter your password', db=0)


    @cherrypy.expose
    def index(self):
        top10_list = self.database.lrange(name='top10', start=0, end=9)
        response_list=[]
        for row in top10_list:
            dict = ast.literal_eval(row.decode())
            response_list.append(dict)



        return Template(filename='index.html').render(data=response_list)

    @cherrypy.expose

    def search(self,**params):
        input_str = params['search']


        response=self.database.smembers(input_str.encode())
        try:
            str = response.pop().decode()
            a = ast.literal_eval(str)
            response_dict=dict(SC_CODE=a['SC_CODE'],SC_NAME=input_str,OPEN=a['OPEN'],HIGH=a['HIGH'],
                               LOW=a['LOW'],CLOSE=a['CLOSE'],GAIN=a['GAIN'])
        except:
            print('enter correct name')
            raise cherrypy.HTTPError(404, "Could not find a track with that URI.")

        return json.dumps(response_dict)


if __name__ == '__main__':
    config = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        'global': {
            'server.socket_host': str(os.getenv('VCAP_APP_HOST', '0.0.0.0')),
            'server.socket_port': int(os.getenv('PORT', '8080')),
        },

    }

    #download()
    get_data()

    cherrypy.quickstart(BhavCopyServer(),config=config)

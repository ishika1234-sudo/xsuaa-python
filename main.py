import os
from flask import Flask,request,redirect,url_for,render_template
from cfenv import AppEnv
import hdbcli
from hdbcli import dbapi
from test import request_refresh_and_access_token,get_user_info_using_access_token
from tabulate import tabulate

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
templates = os.path.join(BASE_DIR,"templates")
temp_file = templates + "/tabulate.html"

app = Flask(__name__)
env = AppEnv()
hana_service = 'hana'
hana = env.get_service(label=hana_service)


# print('services', env.services)
# uaa_service = env.get_service(name='myuaa')
# security_context = xssec.create_security_context(uaa_service)
# print('uaa service',uaa_service, security_context)

@app.route('/createtable/',methods=['GET'])
def createtable():
    try:
        conn = dbapi.connect(address=hana.credentials['host'],
                             port=int(hana.credentials['port']),
                             user=hana.credentials['user'],
                             password=hana.credentials['password'],
                             encrypt='true',
                             sslTrustStore=hana.credentials['certificate'])
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE USER_OBJECT1 (C2 VARCHAR(255),C3 VARCHAR(255),C4 VARCHAR(255), C5 VARCHAR(255))")
        cursor.close()
        return 'TABLE CREATED'
    except Exception as e:
        return 'Error: {}'.format(e)


@app.route('/')
def hello():
    try:
        if hana is None:
            return "Can't connect to HANA service '{}' ? check service name?".format(hana_service)
        else:
            conn = dbapi.connect(address=hana.credentials['host'],
                                 port=int(hana.credentials['port']),
                                 user=hana.credentials['user'],
                                 password=hana.credentials['password'],
                                 encrypt='true',
                                 sslTrustStore=hana.credentials['certificate'])

            cursor = conn.cursor()
            cursor.execute("select CURRENT_UTCTIMESTAMP from DUMMY")
            ro = cursor.fetchone()
            cursor.execute('SELECT CURRENT_USER FROM DUMMY')
            techUser = cursor.fetchone()['CURRENT_USER']
            cursor.execute('SELECT SESSION_CONTEXT(\'APPLICATIONUSER\') "APPLICATION_USER" FROM "DUMMY"')
            appUser = cursor.fetchone()['APPLICATION_USER']
            # print('fetchall', cursor.fetchall())
            cursor.execute("SELECT TABLE_NAME FROM SYS.M_TABLES")
            tables = cursor.fetchall()
            # print("tables", cursor.fetchall())

            # html output
            output = '''
                    <h1>Welcome to SAP HANA!</h1>
                    <p>Technical User: %s</p>
                    <p>Application User: %s</p>
                    <p>Current time is:  %s</p>
                    <p>tables:  %s</p>
                    ''' % (techUser,appUser,str(ro["CURRENT_UTCTIMESTAMP"]),str(tables))

            cursor.close()
            conn.close()
            return output
    except hdbcli.dbapi.Error as e:
        return 'something went wrong {}'.format(e)
    except Exception as e:
        return 'Error: {}'.format(e)


# used to read incoming POST, PUT, DELETE request args
def getRequestParams(data):
    params = {}
    req = data.decode('utf-8')[1:-1].split(',')
    for param in req:
        temp = param.split(':')
        params[temp[0].strip()[1:-1]] = temp[1].strip()[1:-1]

    return params


user_email = ''
user_first_name = ''
user_last_name = ''


@app.route("/home/")
def home():
    return render_template('index2.html')


@app.route("/login/")
def login():
    try:
        # redirects to request uri
        request_uri = "https://lti.authentication.eu10.hana.ondemand.com/oauth/authorize?client_id=sb-authcode-newapp!t1686&response_type=code"
        return redirect(request_uri)
    except Exception as e:
        return 'Error: {}'.format(e)


@app.route("/login/callback")
def callback():
    try:
        # Get authorization code sent back to you
        code = request.args.get("code")
        print('code is',code)
        request_access_token = request_refresh_and_access_token(code)
        if request_access_token['status'] == 200:
            get_user_information = get_user_info_using_access_token(request_access_token['access_token'],
                                                                    request_access_token['id_token'])
            if get_user_information['status'] == 200:
                # return redirect(url_for('addProduct', user = get_user_information['user_info']['email']))
                global user_email,user_last_name,user_first_name
                user_email = get_user_information['user_info']['email']
                user_first_name = get_user_information['user_info']['first_name']
                user_last_name = get_user_information['user_info']['last_name']
                # return 'WELCOME {}'.format(user_email)
                # return render_template('index2.html')
                return redirect("https://webrouter.cfapps.eu10.hana.ondemand.com/home/")
            else:
                return 'could not fetch user info'
        else:
            return 'something went wrong in requesting access token'
    except Exception as e:
        return 'Error: {}'.format(e)


# adds product to database if a valid post request is received
@app.route('/addProduct/',methods=['GET','POST'])
def addProduct():
    try:
        if request.method == 'POST':
            # check if the post request has the file part
            f = request.files['file']
            print('filename is=---->',f.filename,f)

        # establish db connection
        # createtable()
        conn = dbapi.connect(address=hana.credentials['host'],
                             port=int(hana.credentials['port']),
                             user=hana.credentials['user'],
                             password=hana.credentials['password'],
                             encrypt='true',
                             sslTrustStore=hana.credentials['certificate'])
        cursor = conn.cursor()
        sql = 'INSERT INTO USER_OBJECT1 (C2, C3, C4, C5) VALUES (?, ?, ?, ?)'
        cursor = conn.cursor()
        # get parameters from post request
        # params = getRequestParams(request.data)
        # call stored procedure to add product
        in_params = (user_first_name,user_last_name,user_email,f.filename,None)
        print('in_params',in_params)
        cursor.execute(sql,in_params)
        cursor.close()
        return "inserted successfully {}".format(in_params)
        # user = request.args.get("user")
        # return user_email
    except hdbcli.dbapi.Error as e:
        return 'something went wrong {}'.format(e)
    # except Exception as e:
    # return 'Error: {}'.format(e)


# view product from database if a valid get request is received
@app.route('/viewProduct/',methods=['GET'])
def viewProduct():
    try:
        table = [['FIRST NAME','LAST NAME','EMAIL','FILE']]
        conn = dbapi.connect(address=hana.credentials['host'],
                             port=int(hana.credentials['port']),
                             user=hana.credentials['user'],
                             password=hana.credentials['password'],
                             encrypt='true',
                             sslTrustStore=hana.credentials['certificate'])
        cursor = conn.cursor()
        sql = 'SELECT * FROM USER_OBJECT1'
        cursor = conn.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()
        print("Total number of rows in table: ",cursor.rowcount)
        print("\nPrinting each row",records)
        for row in records:
            table.append(list(row))
            print('row is',list(row))
            # print("first name = ",row[0])
            # print("last name = ",row[1])
            # print("email  = ",row[2])
            # print('file = ', row[3])

        # return str(records)
        final_table = tabulate(table,headers='firstrow',tablefmt='html')
        print(final_table)
        templ_file = open(temp_file,"w")
        templ_file.write(final_table)
        templ_file.close()
        return render_template('tabulate.html')
    except hdbcli.dbapi.Error as e:
        return 'something went wrong {}'.format(e)
    except Exception as e:
        return 'Error: {}'.format(e)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=int(os.getenv("PORT",5000)))

from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import jwt
import hashlib
import datetime
import subprocess
from flask.json.provider import JSONProvider
import json
from bson import ObjectId
import sys

app = Flask(__name__)

####################################################
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)
####################################################


# 위에 정의되 custom encoder 를 사용하게끔 설정한다.
app.json = CustomJSONProvider(app)



# secret key
secret_key = 'jungbae'

# mongo db
# client = MongoClient('localhost', 27017)
# db = client.bdground

client = MongoClient('mongodb://anuhyun:dksdn@3.36.103.219',27017)
db = client.dbground

# CONTANTS
SURVICE_TITLE = "BAEDALGROUNDS"
LOGO_URL = './images/logo.png'

# 메인 페이지
@app.route('/')
def deliveryBoardPage():
  return render_template('main.html', service_title=SURVICE_TITLE, image =LOGO_URL)

# 로그인
@app.route('/login')
def loginPage():
  return render_template('login.html', service_title=SURVICE_TITLE, image =LOGO_URL)

@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    
    print(id_receive)
    
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result :  ## if result:
  
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'})

@app.route('/signIn')
def signInPage():
  return render_template('signIn.html', service_title=SURVICE_TITLE, image=LOGO_URL)

@app.route('/api/signIn',methods = ['POST'])
def api_signIn():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']
    
    print(id_receive, pw_receive, name_receive)
    #existing = db.bdground.find_one({'id':id_receive})
    # if existing:
    #   print('중복되었습니다,')
    #   return jsonify({'result': 'fail', 'msg': '아이디가 중복되었습니다.'})
      
  
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'name': name_receive})

    return jsonify({'result': 'success'})

#중복확인 api
@app.route('/api/signIn/confirm',methods = ['POST'])
def api_confirm():
    id_receive = request.form['id_give']
    result = db.user.find_one({'id': id_receive})
    if result:
      return jsonify({'result': 'fail', 'msg': '아이디가 중복되었습니다.'})
    else:
      return jsonify({'result': 'success'})
      
    
    
  



#main
@app.route('/api/isAuth', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, secret_key, algorithms=['HS256'])
        userinfo = db.user.find_one({'id': payload['id']})
        return jsonify({'result': 'success', 'name': userinfo['name']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

# ###클ㄹ이언트 쪽에서 data ={}
# @app.route('/api/category',methods=['GET'])
# def api_category():
#   #id_receive = request.args.get('userid')
#   category=['중식','양식','한식','패스트푸드','분식','카페&디저트','학식','기타']
#   return jsonify({'result':'success', 'category':category})
  
###클라이언트 쪽에서 data={} 줘도댐
@app.route('/api/foodTable',methods=['GET'])
def get_data():
    current_date = datetime.today().strftime('%Y-%m-%d')
    data = db.dormitory_menu.find_one({'date': current_date})
    ###try except로 바꿀지 고민
    if data:
        return jsonify({'result':'success', 'data':data})
    else:
        subprocess.run(['python', 'dormitory_menu.py'])      
        get_data() 
        
###클이언트 쪽에서 data ={'id_give':userid}
@app.route('/api/userInfo',methods=['GET'])
def api_userInfo():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, secret_key, algorithms=['HS256'])
        userinfo = db.user.find_one({'id': payload['id']})
        return jsonify({'result': 'success', 'name': userinfo['name'] ,'id':userinfo['id']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '유저 정보가 존재하지 않습니다.'})
    

    

  
if __name__ == '__main__':  
  app.run('0.0.0.0',port=5001,debug=True)
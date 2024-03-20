from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import jwt
import hashlib
import datetime
import requests

app = Flask(__name__)

# secret key
secret_key = 'jungbae'

# mongo db
client = MongoClient('localhost', 27017)
db = client.bdground

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
    
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result :  ## if result:
  
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)
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
    
#새 카드 등록
# 기대하는 프론트 메커니즘
# 제목,내용,마감시간,오픈채팅을 입력받고 태그는 처음에 0같은 쓰레기값으로 저장되어있다가 각 태그별 button에 onclick으로
# 연결해서 클릭한 태그 문자열 그대로 태그값으로 입력
# 백에서는 토큰으로 유저아이디를 조회해서 이름을 찾아내고, 프론트에서 입력된 데이터와 함께 몽고db cards 도큐먼트에 저장
# 기본적으로 현재인원은 1로 시작하게 함
@app.route('/api/post_card', methods=['POST'])
def post_card():
    token_receive = request.cookies.get('mytoken')
    title = str(request.form['title'])
    content = str(request.form['content'])
    thumbnail_url = str(request.form['thumbnail_url'])
    time_limit = str(request.form['time_limit'])
    openchat_url = str(request.form['openchat_url'])
    category = str(request.form['category'])
    try:
        payload = jwt.decode(token_receive, secret_key, algorithms=['HS256'])
        userinfo = db.user.find_one({'id': payload['id']})
        master_user_id= userinfo['id']
        master_user_name= userinfo['name']
        join_user=[]
        join_user.append(master_user_id)
        card_data={'master_user_id':master_user_id,'master_user_name':master_user_name,'title':title,'content':content,'thumbnail_url':thumbnail_url,'time_limit':time_limit,'category':category,'openchat_url':openchat_url, 'join_user':join_user}
        db.cards.insert_one(card_data)
        return jsonify({'result': 'success', 'msg': '카드 등록완료!'})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})



# 데이터베이스로부터 master_user_id,join_user를 제외한 데이터를 받아서 넘겨주며 조회중인 사용자가 포함되어있는지 여부를 나타내는 is_join이 추가되어있습니다
@app.route('/api/show_card')
def show_cards():
  token_receive = request.cookies.get('mytoken')
  payload = jwt.decode(token_receive, secret_key, algorithms=['HS256'])
  user_id= payload['id']
  cards_data=list(db.cards.find({}, {"master_user_id": 0}))
  sending_data=[]
  for card_data in cards_data:
    card_data['_id']=str(card_data['_id'])
    member_count=len(card_data['join_user'])
    card_data["member_count":str(member_count)]
    if user_id in card_data['join_user']:
        del card_data['join_user']
        card_data['is_join']=True
    else:
       del card_data['join_user']
       card_data['is_join']=False
    sending_data.append(card_data)
  return jsonify(sending_data)

# 프론트로부터 _id(문자열)값을 받아 해당하는 모임에 이용자를 참가자로 추가합니다 
@app.route('/api/add_join_user', methods=['POST'])
def add_join_user():
  try:
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, secret_key, algorithms=['HS256'])
    user_id= payload['id']
    card_id = str(request.form['_id'])
    obj_card_id=ObjectId(card_id)
    db.cards.update_one({'_id':obj_card_id},{'$push':{'join_user':user_id}})
    return "참가원 추가 성공"
  except jwt.ExpiredSignatureError:
      return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
  except jwt.exceptions.DecodeError:
      return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})
  
# 프론트로부터 _id(문자열)값을 받아 해당하는 모임의 참가자 명단에서 이용자를 제거합니다 
@app.route('/api/remove_join_user', methods=['POST'])
def remove_join_user():
  try:
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, secret_key, algorithms=['HS256'])
    user_id= payload['id']
    card_id = str(request.form['_id'])
    obj_card_id=ObjectId(card_id)
    db.cards.update_one({'_id':obj_card_id},{'$pull':{'join_user':user_id}})
    return "참가원 제거 성공"
  except jwt.ExpiredSignatureError:
      return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
  except jwt.exceptions.DecodeError:
      return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

# 프론트로부터 _id(문자열)값을 받아 파티장인지 확인 후 해당카드를 제거합니다 
@app.route('/api/remove_card', methods=['POST'])
def remove_card():
  try:
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, secret_key, algorithms=['HS256'])
    user_id= payload['id']
    card_id = str(request.form['_id'])
    obj_card_id=ObjectId(card_id)
    if db.cards.find_one({'_id':obj_card_id})['master_user_id']==user_id:
      db.cards.delete_one({'_id':obj_card_id})
      return "카드 제거 성공"
    else:
      return "카드제거는 파티장만 할 수 있습니다"
  except jwt.ExpiredSignatureError:
      return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
  except jwt.exceptions.DecodeError:
      return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


if __name__ == '__main__':  
  app.run('0.0.0.0',port=5001,debug=True)
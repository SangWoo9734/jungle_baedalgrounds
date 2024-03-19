from flask import Flask, render_template
app = Flask(__name__)

LOGO_URL = './images/logo.png'

# 메인 페이지
@app.route('/')
def deliveryBoardPage():
  return render_template('main.html')

# 로그인
@app.route('/login')
def loginPage():
  return render_template('login.html', image =LOGO_URL)

@app.route('/signIn')
def signInPage():
  return render_template('signIn.html', image=LOGO_URL)

if __name__ == '__main__':  
  app.run('0.0.0.0',port=5000,debug=True)
from flask import Flask, render_template, url_for, redirect,request, session
import pandas as pd
import numpy as np
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import hashlib
import urllib.request
import urllib.parse
import json
import base64
from pprint import pprint
import os
import random


client_id = "2002946997"
# Channel Secret
client_secret = "5b1dd1ebf7658140c8847c153a5ec619"
# Callback URL
redirect_uri = 'https%3A%2F%2Fnyuma-rensen.onrender.com%2Fcallback'
redirect_uri_de = 'https://nyuma-rensen.onrender.com/callback'
# LINE エンドポイント
authorization_url = 'https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id='
token_url = 'https://api.line.me/oauth2/v2.1/token'
user_info_url = 'https://api.line.me/oauth2/v2.1/userinfo'

app = Flask(__name__)
app.secret_key = 'session_key'

REQUEST_URL = 'https://script.google.com/macros/s/AKfycbyHlkHBRUmI4j03uSS_7mbbNt0u7y5d3hPMop1v1T4QZHVOr4UKLpb4_F-bLwEswWo7fw/exec'
REQUEST_Mercari = 'https://script.google.com/macros/s/AKfycbwmcBrElODPv3E5OyBPqe9M1OHvXNxYlIgg1-VyQ9HXahjQabx8urrIoOqH-sakhR-D/exec'

REQUEST_URL_nyuma = 'https://script.google.com/macros/s/AKfycbwD361e3YumKhbNepF_aQuL4dJyHoagtx0Gs3z4KBQDY1y9zUl7r1JuMzaa-q2TYLpC/exec'
REQUEST_Mercari_nyuma = 'https://script.google.com/macros/s/AKfycbyA-U2FVOiNfEMZxFRunEYGUgOevKheeUHa4zfcrTn8Zdu1Q2y3JZRqM9hBSDyxN4vkqQ/exec'
dongdong_user_id="U3f25ef0ddbebaaf049cea6af51d3c7c0"
dongdong_user_name="咚咚♏️♏️"

@app.route("/login")
def login():
    # ステート生成
    state = hashlib.sha256(os.urandom(10)).hexdigest()
    session['state'] = state
    redirect_u=authorization_url+client_id+"&redirect_uri="+redirect_uri+"&state="+state+"&scope=profile%20openid" 
    # 認可リクエスト
    return redirect(redirect_u)


# 認可リクエスト受信 → トークンリクエスト → ユーザープロフィールリクエスト
@app.route("/callback")
def callback():
    # 2. ユーザー認証/同意を行い、認可レスポンスを受け取る。
    # 認可コードを受け取る:https://developers.line.biz/ja/docs/line-login/integrate-line-login-v2/#receiving-the-authorization-code
    state = request.args.get('state')
    if state != session['state']:
        print("invalid_redirect")
    code = request.args.get('code')
    # 3. 認可レスポンスを使ってトークンリクエストを行う。
    # ウェブアプリでアクセストークンを取得する:https://developers.line.biz/ja/docs/line-login/integrate-line-login-v2/#get-access-token
    body = urllib.parse.urlencode({
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri_de,
        'grant_type': 'authorization_code'
    }).encode('utf-8')
    req, res = '', ''
    req = urllib.request.Request(token_url)
    with urllib.request.urlopen(req, data=body) as f:
        res = f.read()
    access_token = json.loads(res)['access_token']
    # 4. 取得したアクセストークンを使用してユーザープロフィールを取得する。
    # ユーザープロフィールを取得する:https://developers.line.biz/ja/docs/line-login/managing-users/#get-profile
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    req = urllib.request.Request(user_info_url, headers=headers, method='GET')
    with urllib.request.urlopen(req) as f:
        res = f.read()
    user_json=json.loads(res)   
    user_id=user_json['sub']
    user_name=user_json["name"]
    
    try:
    # ここに例外が発生する可能性のあるコードを書く
        picture_url=user_json["picture"]
    except KeyError as e:
        # 例外が発生した場合の処理を書く
        picture_url="https://profile.line-scdn.net/"
    picture_url=picture_url.replace("https://profile.line-scdn.net/", "picture_url")
    
    redirect_url="/index?user_id="+user_id+"&user_name="+user_name+"&picture_url="+picture_url

    # print(user_id)
    # print(user_name)
    return redirect(redirect_url)

@app.route('/index') 
def index():
    picture_url = request.args.get('picture_url')
    picture_url=picture_url.replace( "picture_url","https://profile.line-scdn.net/")
    user_id = request.args.get('user_id')
    user_name = request.args.get('user_name')     
    return render_template("index.html",user_id=user_id,user_name=user_name,picture_url=picture_url)


@app.route('/net') 
def net():

    user_id = request.args.get('user_id')
    user_name = request.args.get('user_name')     
    return render_template("net.html",user_id=user_id,user_name=user_name)

@app.route('/mercari') 
def mercari():

    user_id = request.args.get('user_id')
    user_name = request.args.get('user_name')     
    return render_template("mercari.html",user_id=user_id,user_name=user_name)

@app.route('/order', methods=['POST']) 
def order():
    data = request.form  # フォームフィールドの名前に合わせて変更
    count=request.form["inputCount"]
    user_id=request.form["user_id"]
    user_name=request.form["user_name"]
    option=request.form["option"]
    

    unique_num = random.randint(100000, 999999)
    unique_num = str(unique_num)+user_id
    print(unique_num)
    data_dict = data.to_dict()
    for i in range(1, int(count)+1):
        val = 'val'+ str(i)
        url = 'myURL'+ str(i)
        pic = 'pic'+ str(i)
        type= 'type'+ str(i)
        # キーが一致する値を取得
        url = data_dict[url]
        val = data_dict[val]
        pic = data_dict[pic]
        type = data_dict[type]

        # 辞書を作成


        data = {
            "user_id": dongdong_user_id,
            "user_name": dongdong_user_name,
            "buy_user_name": user_name,
            "url": url,
            "val": val,
            "pic": pic,
            "type": type,
            "option":option,
            "unique_num":unique_num,
            }
        print(data)
        response = requests.post(REQUEST_URL, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        response = requests.post(REQUEST_URL_nyuma, data=json.dumps(data), headers={'Content-Type': 'application/json'})

    return f'{user_name}様 收到您的訂單'

@app.route('/order_mercari', methods=['POST']) 
def order_mercari():
    data = request.form  # フォームフィールドの名前に合わせて変更
    user_id=request.form["user_id"]
    user_name=request.form["user_name"]
    url=request.form["url"]
    val=request.form["val"]
    option=request.form["option"]
    # 辞書を作成
    data = {
        "user_id": dongdong_user_id,
        "user_name": dongdong_user_name,
        "buy_user_name": user_name,
        "url": url,
        "val": val,
        "option":option,
        }
    response = requests.post(REQUEST_Mercari, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    response = requests.post(REQUEST_Mercari_nyuma, data=json.dumps(data), headers={'Content-Type': 'application/json'})

    return f'{user_name}様 收到您的訂單'
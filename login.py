# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 08:33:25 2023

@author: 86159
"""
import requests
import json

import hashlib
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5

# 密码登录类
class DbackupLogin:
    # 获取公钥
    def __getPublicKey(self):
        url = "http://192.168.3.118/d2/r/v2/server/public_key"
        params = {"Content-Type":"application/json"}
        publicKey = requests.get(url=url, params=params).json()
        return publicKey
    
    # 获取signature
    def __getSignature(self): 
        url2 = "http://192.168.3.118/d2/r/v2/host/challenge"
        params2 = {"Content-Type":"application/json"}
        sessionChange = json.loads(requests.get(url=url2, params=params2).text)
        # 对返回参数进行运算 得到signature，算法在文档
        tpstr = sessionChange['challenge'] + self.__noEncodePassword
        signature = hashlib.sha256(tpstr.encode('utf-8')).hexdigest() + sessionChange['challenge']
        return signature
    
    # 密码加密
    def encode_content(self, noEncodeStr):
        a = bytes(noEncodeStr, encoding="utf8")
        rsakey = RSA.importKey(self.publicKey)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(a))
        encodeStr = str(cipher_text, encoding='utf-8')
        return encodeStr
    
    # 登录
    def dbackupd_login(self):
        #持久会话
        sess = requests.Session()
        #提交用户登录
        postUrl = 'http://192.168.3.118/d2/r/v2/user/logon'
        data =  {
            "password": self.encodePassword,
            "username": self.userName,
            "remember": False,
            "signature": self.signature,
            "agree_statement": True
        }
        r = sess.post(postUrl, json=data)
        # 存储返回的cookie 和 csrf
        cookie = requests.utils.dict_from_cookiejar(r.cookies)
        token = r.headers['X-CSRF-Token']
        return [sess, cookie, token]
    
    def __init__(self, userName, userPassword):
        self.userName = userName
        self.__noEncodePassword = userPassword
        self.publicKey = self.__getPublicKey()
        self.signature = self.__getSignature()
        self.encodePassword = self.encode_content(self.__noEncodePassword)


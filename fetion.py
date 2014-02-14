#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
本程序作者：bopo
版权所有，仿冒不就
'''
import cookielib
import urllib
import urllib2
import re
import os


class Fetion(object):

    _uids      = {}
    _mobile    = None
    _cookie    = None
    _password  = None
    _csrfToten = None
    _cookiejar = 'cookies.txt'

    def __init__(self, mobile, password):
        if (mobile == None or password == None):
            return

        self._cookie = cookielib.MozillaCookieJar(self._cookiejar)

        if os.path.isfile(self._cookiejar) == False:
            self._cookie.save()

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cookie))
        urllib2.install_opener(opener)

        self._mobile   = mobile
        self._password = password
        self._login()

    def __del__(self):
        return self._logout()

    def _login(self):
        uri    = '/huc/user/space/login.do?m=submit&fr=space'
        data   = {'mobilenum': self._mobile, 'password': urllib.quote(self._password)}
        result = self.request(uri, data)
        result = self.request('/im/login/cklogin.action')
        return result

    def _logout(self):
        return self.request('/im/index/logoutsubmit.action')

    def send(self, mobile, message):
        if (message == None):
            return None

        if (mobile == self._mobile):
            return self._toMyself(message)

        uid = self._getUid(mobile)

        if uid == None:
            return None

        return self._toUid(uid, message)

    def _getUid(self, mobile):
        if (self._uids.get(mobile) == None):
            uri     = '/im/index/searchOtherInfoList.action'
            result  = self.request(uri, {'searchText': mobile})
            pattern = re.compile("toinputMsg\.action\?touserid=(\d+)", re.S)
            matches = pattern.search(result).groups()
            self._uids[mobile] = matches[0]

        return self._uids[mobile]

    def _getCsrfToken(self, uid):
        if (self._csrfToten == None):
            uri     = '/im/chat/toinputMsg.action?touserid=%s' % uid
            result  = self.request(uri, '')
            pattern = re.compile('name="csrfToken".*?value="(.*?)"')
            matches = pattern.search(result).groups()

            self._csrfToten = matches[0]

        return self._csrfToten

    def _toUid(self, uid, message):
        uri       = '/im/chat/sendMsg.action?touserid=%s' % uid
        csrfToken = self._getCsrfToken(uid)
        result    = self.request(uri, {'msg': message, 'csrfToken': csrfToken})
        return result

    def _toMyself(self, message):
        return self.request('/im/user/sendMsgToMyselfs.action', {'msg': message})

    def request(self, uri, data=None):
        getway = 'http://f.10086.cn%s' % uri

        if data != None:
            data = urllib.urlencode(data).strip()

        self._cookie.load(self._cookiejar)
        request = urllib2.Request(getway, data)
        request.add_header('Content-Type', "application/x-www-form-urlencoded")
        result = urllib2.urlopen(request).read()
        self._cookie.save()

        return result

if __name__ == '__main__':
    message = "Python test sms."
    fetion  = Fetion('<mobile>', '<password>')
    fetion.send('<to_mobile>', message)

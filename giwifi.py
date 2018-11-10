import os
import re
import time
import json
import argparse
import requests
from getpass import getpass
from urllib.parse import urlparse, parse_qs

SCRIPT_VERSION = "1.0.3.2"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.25 Safari/537.36',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh-TW;q=0.8,zh;q=0.6,en;q=0.4,ja;q=0.2',
    'cache-control': 'max-age=0'
}

PARSER = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
    description='GiWiFi认证登录脚本', 
    epilog='(c) 2018 journey.ad')
PARSER.add_argument('-g', '--gateway', type=str, help='网关IP')
PARSER.add_argument('-u', '--username', type=str, help='用户名')
PARSER.add_argument('-p', '--password', type=str, help='密码')
PARSER.add_argument('-q', '--quit', action='store_true', help='登出')
PARSER.add_argument('-d', '--daemon', action='store_true', help='在后台守护运行')
PARSER.add_argument('-v', '--verbose', action='store_true', help='额外输出一些技术性信息')
PARSER.add_argument('-V', '--version', action='version', 
        version='giwifi-auth-helper {}'.format(SCRIPT_VERSION))

CONFIG = PARSER.parse_args()

CONFIG.gateway = "172.16.1.2"       #填入网关
CONFIG.username = "123456"     #填入账号
CONFIG.password = "654321"      #填入密码

def main():
    logcat('正在获取网关信息…')

    try:
        authUrl = requests.get('http://%s:8062/redirect' % (CONFIG.gateway), timeout=5).url
        authParmas = {k: v[0] for k, v in parse_qs(urlparse(authUrl).query).items()}

        loginPage = requests.get('http://login.gwifi.com.cn/cmps/admin.php/api/login/?' + urlparse(authUrl).query, headers=HEADERS, timeout=5).text

        pagetime = re.search(r'name="page_time" value="(.*?)"', loginPage).group(1)
        sign = re.search(r'name="sign" value="(.*?)"', loginPage).group(1)

    except requests.exceptions.ConnectionError:
        logcat('连接失败，请检查网关地址是否正确')
        return

    except requests.exceptions.Timeout:
        logcat('连接超时，可能已超出上网区间')
        return

    except AttributeError:
        logcat('解析失败，可能网关设备重启或系统已更新')
        return

    authState = getAuthState(authParmas, sign)

    if CONFIG.quit:
        logout(authParmas)

    if not authState:
        return

    else:
        if authState['auth_state'] == 2:
            printStatus(authParmas, authState)
            logcat('你已登录，无需再次登录')
        else:
            data = {
                'access_type': authState['access_type'],
                'acsign': authState['sign'],
                'btype': 'pc',
                'client_mac': authState['client_mac'],
                'contact_phone': '400-038-5858',
                'devicemode': '',
                'gw_address': authParmas['gw_address'],
                'gw_id': authParmas['gw_id'],
                'gw_port': authParmas['gw_port'],
                'lastaccessurl': '',
                'logout_reason': authState['logout_reason'],
                'mac': authParmas['mac'],
                'name': CONFIG.username,
                'online_time': authState['online_time'],
                'page_time': pagetime,
                'password': CONFIG.password,
                'sign': sign,
                'station_cloud': 'login.gwifi.com.cn',
                'station_sn': authState['station_sn'],
                'suggest_phone': '400-038-5858',
                'url': 'http://www.baidu.com',
                'user_agent': '',
            }

            if CONFIG.verbose:
                logcat(data)

            result = login(data)
            if result['status']:
                authState = getAuthState(authParmas, sign)
                printStatus(authParmas, authState)

                if authState['auth_state'] == 2:
                    logcat('认证成功')
                else:
                    logcat('认证失败')
            else:
                logcat('认证失败，提示信息：%s' % (result['info']))

def login(data):
    logcat('正在尝试认证…')

    try:
        resp = json.loads(requests.post('http://login.gwifi.com.cn/cmps/admin.php/api/loginaction', data=data, timeout=5).text)
        result = {
            'status': False,
            'info': None
        }

        if CONFIG.verbose:
            logcat(resp)

        if 'wifidog/auth' in resp['info']:
            requests.get(resp['info'])
            result['status'] = True
        else:
            result['info'] = resp['info']

    except requests.exceptions.Timeout:
        logcat('连接超时，可能已超出上网区间')
        
    finally:
        return result

def getAuthState(authParmas, sign):     #获取认证状态
    try:
        params = {
            'ip': authParmas['ip'],
            'mac': authParmas['mac'],
            'sign': sign,
            'callback': ''
        }
    
        resp = json.loads(requests.get('http://%s:%s/wifidog/get_auth_state' % (authParmas['gw_address'], authParmas['gw_port']), params=params, timeout=5).text[1:-1])
            
    except KeyError:
        logcat('所需参数不存在')
        return False

    except requests.exceptions.Timeout:
        logcat('连接超时，可能已超出上网区间')
        return False

    if CONFIG.verbose:
        logcat(resp)

    if resp['resultCode'] == 0:
        return json.loads(resp['data'])
    else:
        return False

def printStatus(authParmas, authState):     #打印认证信息
    if not CONFIG.verbose:
        clear()

    print(
'''--------------------------------------------
SSID:             %s
AP MAC:           %s
GateWay:          %s
IP:               %s
MAC:              %s
Station SN:       %s
Logged:           %s
--------------------------------------------'''
    % (
            authParmas['gw_id'],
            authParmas['apmac'],
            authParmas['gw_address'],
            authParmas['ip'],
            authParmas['mac'],
            authState['station_sn'],
            'yes' if(authState['auth_state'] == 2) else 'no'
        )
    )

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def logcat(msg, level='I'):
    print('%s %s: %s' % (time.ctime().split(' ')[-2], level, msg))

main()

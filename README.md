# Giwifi
校园网自动认证

### Padavan使用方法

1、先使用ssh登陆路由器   
  
2、安装opkg  
```
opkg.sh
```
3、安装python3   
```
opkg install python3   
```
4、安装pip3
```
opkg install python3-pip
```
5、安装依赖库**requests**
```
pip3 install requests
```
6、下载giwifi.py源码
```
wget http://mgh234/giwifi.py
```
7、修改账号配置  
输入`vi giwifi.py`在第34和35行修改成自己的账号和密码，然后保存  
  
8、配置路由器  
打开Padavan管理界面，再依次打开<kbd>自定义设置</kbd>---><kbd>脚本</kbd>---><kbd>自定义脚本0(功能配置)</kbd>  
在最后填入以下内容：
```
python3 /opt/home/admin/giwifi.py
```
9、设置定时重启  
依次打开<kbd>系统管理</kbd>---><kbd>系统设置</kbd>---><kbd>定时重启</kbd>进行设置  
这时路由器在启动时就会自动进行认证了

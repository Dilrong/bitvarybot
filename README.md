# 개요

## 배경
[파이썬을 이용한 비트코인 자동매매](https://wikidocs.net/21889)
위 봇을 개인적으로 사용하기 위해서 개량

# 내용
## 환경
Python 3.9
## 실행방법
1. `pip install -r requirements.txt`
2. `key.txt` 아래와 같이 생성
```
user access key
user secret key
```
3. `python3 bot.py`

## 오류해결
### bs4 오류
```
ERROR: Could not find a version that satisfies the requirement python3-bs4 (from -r requirements.txt (line 7)) (from versions: none)
ERROR: No matching distribution found for python3-bs4 (from -r requirements.txt (line 7))
```
**해결방법**

### WebSocket
```
ModuleNotFoundError: No module named 'websockets'
```
**해결방법** 
`pip install websocket_client`

### SyntaxError
```
SyntaxError: Non-ASCII character '\xec' in file trader.py on line 17, but no encoding declared; see http://python.org/dev/peps/pep-0263/ for details
```
**해결방법**
trader.py에 주석 추가 
`# -*- coding: utf-8 -*-`
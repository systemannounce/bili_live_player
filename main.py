# 获取哔哩哔哩直播的真实流媒体地址，默认获取直播间提供的最高画质
# qn=150高清
# qn=250超清
# qn=400蓝光
# qn=10000原画
from typing import Union

import requests
import webbrowser
import os


class BiliBili:

    def __init__(self, rid):
        """
        有些地址无法在PotPlayer播放，建议换个播放器试试
        Args:
            rid:
        """
        rid = rid
        self.header = {  # 要获取原画请自行填写cookie
            'User-Agent': 'Mozilla/5.0 (iPod; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                          'like Gecko) CriOS/87.0.4280.163 Mobile/15E148 Safari/604.1',
            'Cookie': FileManager.temp_file('cookie.txt')
        }
        # 先获取直播状态和真实房间号
        r_url = 'https://api.live.bilibili.com/room/v1/Room/room_init'
        param = {
            'id': rid
        }
        with requests.Session() as self.s:
            res = self.s.get(r_url, headers=self.header, params=param).json()
        if res['msg'] == '直播间不存在':
            raise Exception(f'bilibili {rid} {res["msg"]}')
        live_status = res['data']['live_status']
        if live_status != 1:
            raise Exception(f'bilibili {rid} 未开播')
        self.real_room_id = res['data']['room_id']

    def get_real_url(self, current_qn: int = 10000) -> dict:
        url = 'https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo'
        param = {
            'room_id': self.real_room_id,
            'protocol': '0,1',
            'format': '0,1,2',
            'codec': '0,1',
            'qn': current_qn,
            'platform': 'h5',
            'ptype': 8,
        }
        res = self.s.get(url, headers=self.header, params=param).json()
        stream_info = res['data']['playurl_info']['playurl']['stream']
        qn_max = 0

        for data in stream_info:
            accept_qn = data['format'][0]['codec'][0]['accept_qn']
            for qn in accept_qn:
                qn_max = qn if qn > qn_max else qn_max
        if qn_max != current_qn:
            param['qn'] = qn_max
            res = self.s.get(url, headers=self.header, params=param).json()
            stream_info = res['data']['playurl_info']['playurl']['stream']

        stream_urls = {}
        # flv流无法播放，暂修改成获取hls格式的流，
        for data in stream_info:
            format_name = data['format'][0]['format_name']
            if format_name == 'ts':
                base_url = data['format'][-1]['codec'][0]['base_url']
                url_info = data['format'][-1]['codec'][0]['url_info']
                for i, info in enumerate(url_info):
                    host = info['host']
                    extra = info['extra']
                    stream_urls[f'线路{i + 1}'] = f'{host}{base_url}{extra}'
                break
        return stream_urls


class FileManager:
    def __init__(self, *args, **kwargs):
        raise TypeError('Banned Instantiate')

    @staticmethod
    def temp_file(cookie_file):
        if not os.path.exists(cookie_file):
            print('没有检测到cookie文件,已经自动创建，画质将受到影响。')
            with open(cookie_file, 'w') as f:
                f.write('')
        with open(cookie_file, 'r', encoding='utf-8') as fp:
            cookie = fp.read()
            if cookie == '':
                print('cookie文件为空，画质将受到影响。')
            return cookie

    @staticmethod
    def room_list(room_file):
        lines = []
        if not os.path.exists(room_file):
            with open(room_file, 'w', encoding='utf-8') as fp:
                fp.write('')
                return ''
        else:
            with open(room_file, 'r', encoding='utf-8') as fp:
                for line in fp.readlines():
                    lines.append(line.strip())
                return lines


def get_real_url(rid: str):
    try:
        bilibili = BiliBili(rid)
        return bilibili.get_real_url()
    except Exception as e:
        print('Exception：', e)
        return False


def open_potplayer(room_id: str) -> Union[bool, str]:
    stream = get_real_url(room_id)
    if stream:
        print(f'一共有{len(stream)}个源')
        choose = input('请问要选哪个，默认第一个')
        if choose == '':
            choose = 1
        if int(choose) > len(stream) or int(choose) <= 0:
            print('请重新选择')
            return False
    else:
        print('请重新选择')
        return False
    webbrowser.open('potplayer://{}'.format(stream['线路{}'.format(str(choose))]))
    return True


class MainFunction:
    def __init__(self, func: str):
        if int(func) == 1:
            self.enter_id()
        elif int(func) == 2:
            self.exist_id()

    def enter_id(self):
        re_choose = True
        while re_choose:
            re_choose = False
            r = input('请输入bilibili房间号:')
            status = open_potplayer(r)
            if not status:
                re_choose = True

    def exist_id(self):
        room_list = FileManager.room_list('room.txt')
        print(room_list)


if __name__ == '__main__':  # 以后再整房间号保存和快速读取，说不定会搞个GUI。弹幕暂时不想研究，太难了。
    select_f = input()
    func = MainFunction(select_f)


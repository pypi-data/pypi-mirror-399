import time
import math
from lxml import etree
from zlib import decompress  # 解压
import requests

class IqiyiFetcher():
    """爱奇艺弹幕抓取器"""
    MAX_DURATION = 7200  # 2小时，单位: 秒


    def __init__(self, url:str,proxy:str=''):
        super().__init__()
        self.url = url
        self.proxy=proxy
        self.proxies = {
"http": self.proxy,
"https": self.proxy,
} if proxy else None
        
        self.albumId=''
    

    def extract_video_id(self):
        """从URL中提取tvid"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Referer": getattr(self, "url", ""),
            }
            ts = int(time.time() * 1000)
            url = f"https://www.iqiyi.com/prelw/player/lw/lwplay/accelerator.js?format=json&timestamp={ts}"
            resp = requests.get(url, headers=headers, timeout=8,proxies=self.proxies)
            resp.raise_for_status()
            data = resp.json()
            tvid = str(data.get("tvid", ""))
            self.albumId = str(data.get("albumId", ""))

            if not tvid.isdigit():
                return ""
            return tvid
        except Exception:
            return ""

    def get_duration(self, tvid):
        """获取视频时长，异常时返回0"""
        url = f"https://pcw-api.iqiyi.com/video/video/baseinfo/{tvid}?t={int(time.time())}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            resp = requests.get(url, headers=headers, timeout=8,proxies=self.proxies)
            resp.raise_for_status()
            data = resp.json()
            duration = int(data.get("data", {}).get("durationSec", 0))
            nickName=data.get("data", {}).get("user", {}).get('nickName','')
            if nickName=='微剧场':
                print('检测到iqiyi微剧场,需要你使用浏览器网络抓包过滤‘prelw/tvg/v2/lw/base_info’，将其url复制出来重新执行获取弹幕命令')
            if duration > 0:
                return duration
            return 0
        except Exception:
            return 0  # 网络异常时返回0

    def fetch_danmaku_segment(self, tvid, part):
        """获取单段弹幕数据"""
        try:
            if not tvid or len(tvid) < 4:
                return []
            xx = tvid[-4:-2]
            yy = tvid[-2:]
            # print(tvid)
            headers = {"User-Agent": "Mozilla/5.0"}
            url = f"https://cmts.iqiyi.com/bullet/{xx}/{yy}/{tvid}_300_{part}.z"
            resp = requests.get(url,headers=headers, timeout=8,proxies=self.proxies)
            # print(resp.status_code)
            
            if resp.status_code != 200 or not resp.content:
                # print(url)
                return []
            try:
                raw = decompress(resp.content).decode('utf-8')
                # with open(f'{tvid}_{part}.xml','w',encoding='utf-8') as f:
                #     f.write(raw)
            except Exception:
                return []
            try:
                html = etree.HTML(bytes(raw, 'utf-8'))
            except Exception:
                return []

            ul = html.xpath('/html/body/danmu/data/entry/list/bulletinfo')
            danmakus=[]

            for i in ul:
                contentid = ''.join(i.xpath('./contentid/text()'))
                content = ''.join(i.xpath('./content/text()'))
                showTime = ''.join(i.xpath('./showtime/text()'))
                likeCount = ''.join(i.xpath('./likecount/text()'))
                
                if likeCount and likeCount !='0':
                    content+=' ♡ '+likeCount

                try:
                    time_offset = float(showTime)*1000
                except Exception:
                    time_offset = 0
                try:
                    val = int(i.xpath('./position/text()'))
                    if val == 0:
                        mode = 1
                    else:
                        mode = 5
                except Exception:
                    mode = 1
                try:
                    font_size_val = int(i.xpath('./font/text()'))
                    font_size = {
                        14: 25,
                        20: 30,
                        30: 36,
                        0: 20,
                        2: 18,
                    }.get(font_size_val, 25)
                except Exception:
                    font_size = 25
                try:
                    color_raw = i.xpath('./color/text()')
                    if not isinstance(color_raw, str):
                        color_raw = str(color_raw)
                    color = int(color_raw.strip("#"), 16)
                except Exception:
                    color = 0xFFFFFF
                danmakus.append({
                        "time_offset": time_offset,
                        "mode": mode,
                        "font_size": font_size,
                        "color": color,
                        "timestamp": int(contentid),
                        "content": content
                    })
            return danmakus
        except Exception:
            return []
        
    def get_video_info(self):
        """
        获取视频信息，返回字典，至少包含 'title' 键
        """
        try:
            tvid = self.extract_video_id()
            if not tvid:
                return {"title": "弹幕"}
            
            info_url = f"https://mesh.if.iqiyi.com/player/lw/video/playervideoinfo?id={tvid}&locale=cn_s"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(info_url, headers=headers, timeout=8,proxies=self.proxies)
            resp.raise_for_status()
            data = resp.json().get("data", {})
            # print(data)

            # 视频标题优先使用 vn（集标题），没有则用 an（剧名）
            title = data.get("vn") or data.get("an") or "弹幕"
            return {"title": title}
        except Exception:
            return {"title": "弹幕"}

    def run(self,start_second:int=None,end_second:int=None,progress_callback:object=None):
        """执行抓取任务"""
        try:
            title=self.get_video_info().get('title','')
            tvid = self.extract_video_id()
            start=1
            if start_second:
                start=start_second//300+1
            if not end_second:
                if not tvid:
                    print("无法获取 tvid")
                    return
                duration = self.get_duration(tvid)
            else:
                duration=end_second

            if not isinstance(duration, (int, float)) or duration <= 0:
                print("无法获取视频时长，默认抓取2小时弹幕")
                duration = self.MAX_DURATION

            total_parts = max(1, math.ceil(duration / 300))
            all_danmakus = []
            # print(start,total_parts)
            for part in range(start, total_parts+1):
                part_data = self.fetch_danmaku_segment(tvid, part)
                if isinstance(part_data, list):
                    all_danmakus.extend(part_data)
                
                if progress_callback:
                    progress_callback(part,total_parts)
            return all_danmakus,duration,title
        except Exception as e:
            raise f"爱奇艺弹幕抓取出错: {str(e)}"

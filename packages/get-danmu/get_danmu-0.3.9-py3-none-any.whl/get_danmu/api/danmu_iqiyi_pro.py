import hashlib
import time
import math
from lxml import etree
from zlib import decompress  # 解压
import requests
from get_danmu.utils import danmu_iqiyi_pb2
import brotli

class IqiyiFetcher():
    """爱奇艺弹幕抓取器"""
    MAX_DURATION = 7200  # 2小时，单位: 秒
    BARRAGE_REQUEST_INTERVAL_TIME = 60  # 弹幕分片时间间隔（秒，根据实际值调整）
    BARRAGE_SALT = "cbzuw1259a"          # 固定盐值
    BARRAGE_CDN_DOMAIN = "https://cmts.iqiyi.com/bullet"  # 弹幕CDN主域名


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
            # if nickName=='微剧场':
            #     print('检测到iqiyi微剧场,需要你使用浏览器网络抓包过滤‘prelw/tvg/v2/lw/base_info’，将其url复制出来重新执行获取弹幕命令')
            if duration > 0:
                return duration
            return 0
        except Exception:
            return 0  # 网络异常时返回0

    def fetch_danmaku_segment(self, tvid, part):
        """获取单段弹幕数据"""
        tvid=str(tvid)
        # print(type(tvid),tvid)
        try:
            if not tvid or len(tvid) < 4:
                return []
            xx = tvid[-4:-2]
            yy = tvid[-2:]
            # print(xx)
            headers = {"User-Agent": "Mozilla/5.0"}
            url = self.__build_danmu_url(tvid=tvid,index=part)
            # print(url)
            resp = requests.get(url,headers=headers, timeout=8,proxies=self.proxies)
            
            if resp.status_code != 200 or not resp.content:
                return []
            try:
                raw = brotli.decompress(bytearray(resp.content))
                danmu = danmu_iqiyi_pb2.Danmu()
                danmu.ParseFromString(raw)
            except Exception:
                return []

            danmakus=[]
            for entry in danmu.entry:
                for bulletInfo in entry.bulletInfo:
                    contentid = 1
                    content = bulletInfo.content
                    showTime = bulletInfo.showTime
                    likeCount = bulletInfo.likeCount 
                    
                    if likeCount and likeCount !='0':
                        content+=' ♡ '+likeCount

                    try:
                        time_offset = float(showTime)*1000
                    except Exception:
                        time_offset = 0
                    try:
                        val = int(bulletInfo.contentType)
                        if val == 0:
                            mode = 1
                        else:
                            mode = 5
                    except Exception:
                        mode = 1
                    try:
                        font_size_val = int(bulletInfo.font)
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
                        color_raw = bulletInfo.color
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
        

    def get_video_info_short_video(self):
        """
        获取短视频信息，返回列表
        """
        try:
            vid_ls=[]
            title_ls=[]
            season=1
            headers = {"User-Agent": "Mozilla/5.0"}
            html=requests.get(self.url,timeout=10, headers=headers,proxies=self.proxies)
            if html.status_code != 200:
                print("未获取到剧集数据！")
                return None,None,None,None
            data=html.json()
            blocks=None
            for i in data['data']['template']['tabs'][0]['blocks']:
                if i.get('bk_title','')=='选集':
                    blocks=i
                    break
            if not blocks:
                return None,None,None,None
            for i in blocks['data']['data']:
                if type(i['videos'])==dict:
                    season=i['order']
                    for j in i['videos']['feature_paged'].keys():
                        for k in i['videos']['feature_paged'][j]:
                            # print(k['title'],k['qipu_id'])
                            try:
                                if '预告' in k.get('subtitle',''):
                                    continue
                                title_ls.append(k['title'])
                                vid_ls.append(k['qipu_id'])
                                # print(k['title'],k['qipu_id'])
                            except:
                                pass
            return [(f"{i}", f"{i}") for i in title_ls],vid_ls,title_ls,season
        except Exception:
            return None,None,None,None

    def run(self,start_second:int=None,end_second:int=None,progress_callback:object=None):
        """执行抓取任务"""
        try:
            title=self.get_video_info().get('title','')
            tvid = self.extract_video_id()
            start=1
            if start_second:
                start=start_second//60+1
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

            total_parts = max(1, math.ceil(duration / 60))
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
        
    def run_short_video(self,tvid:str=None,start_second:int=None,end_second:int=None,progress_callback:object=None):
        # try:
            # tvid = self.extract_video_id()
            start=1
            if start_second:
                start=start_second//60+1
            if not end_second:
                if not tvid:
                    print("无法获取 tvid")
                    return
                duration = self.get_duration(tvid)
            else:
                duration=end_second

            if not isinstance(duration, (int, float)) or duration <= 0:
                print("无法获取视频时长，默认抓取10分钟弹幕")#短剧不长如果获取不到时长则最多获取十分钟
                duration = 10*60

            total_parts = max(1, math.ceil(duration / 60))
            all_danmakus = []
            # print(start,total_parts,tvid)
            for part in range(start, total_parts+1):
                part_data = self.fetch_danmaku_segment(tvid, part)
                if isinstance(part_data, list):
                    all_danmakus.extend(part_data)
                
                if progress_callback:
                    progress_callback(part,total_parts)
            return all_danmakus,duration
        # except Exception as e:
        #     raise f"爱奇艺微短剧弹幕抓取出错: {str(e)}"
    
    def __build_danmu_url(self,tvid: str, index: int) -> str:
        """
        构建爱奇艺弹幕请求URL
        :param tvid: 视频唯一标识（字符串/数字均可）
        :param index: 弹幕分片索引（整数）
        :return: 完整的弹幕请求URL
        """
        # 步骤1：TVID补零处理（拼接"0000"）
        tvid_str = str(tvid)
        S = "0000" + tvid_str
        # 步骤2：拼接加密字符串并计算MD5（取后8位）
        # 格式：tvid_时间间隔_索引_固定盐值
        encrypt_str = f"{tvid_str}_{self.BARRAGE_REQUEST_INTERVAL_TIME}_{index}{self.BARRAGE_SALT}"
        # MD5加密（UTF-8编码）
        md5_result = hashlib.md5(encrypt_str.encode("utf-8")).hexdigest()
        # 取MD5结果后8位作为校验码
        check_code = md5_result[-8:]

        # 步骤3：拼接文件名（含校验码，.br为Brotli压缩格式）
        filename = f"{tvid_str}_{self.BARRAGE_REQUEST_INTERVAL_TIME}_{index}_{check_code}.br"

        # 步骤4：拆分TVID后4位为两级目录（后4位拆分为 前2位 + 后2位）
        last_4_digits = S[-4:] if len(S) >= 4 else S.ljust(4, "0")
        dir1 = last_4_digits[:2]  # 后4位的前2位
        dir2 = last_4_digits[2:]  # 后4位的后2位
        final_url = f"{self.BARRAGE_CDN_DOMAIN}/{dir1}/{dir2}/{filename}"
        return final_url

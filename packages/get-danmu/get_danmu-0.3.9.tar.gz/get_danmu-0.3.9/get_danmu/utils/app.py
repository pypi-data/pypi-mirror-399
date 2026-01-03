from pathlib import Path
from flask import Flask, request, Response, redirect, make_response, render_template, session, abort,url_for
from datetime import datetime, timedelta  # 补充timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import os, time, csv, ujson, re, requests
from get_danmu.api.danmu_bilibili import BilibiliFetcher
from get_danmu.api.danmu_iqiyi import IqiyiFetcher
from get_danmu.api.danmu_mgtv import MgtvFetcher
from get_danmu.api.danmu_tx import TencentFetcher
from get_danmu.config import ConfigManager

# 初始化 SQLAlchemy（先不绑定 app，后续动态关联）
db = SQLAlchemy()

config_manager = ConfigManager()

# 登录配置（写死用户名密码）
# USER_CREDENTIALS = {
#     "admin": "0192023a7bbd73250516f069df18b500",
#     "user": "user456"
# }

# 登录验证装饰器（新增）
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            if request.path.startswith('/api/'):
                return fast_json({"error": "请先登录"}, 401)
            return redirect('/login')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper
redirect302=None

# 定义数据模型（与原逻辑一致）
class AnimeEpisode(db.Model):
    __tablename__ = 'anime_episodes'
    
    id = db.Column(db.Integer, primary_key=True)
    episodeId = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True)
    animeId = db.Column(db.Integer, nullable=True)
    animeTitle = db.Column(db.String(255), nullable=False)
    episodeTitle = db.Column(db.String(255), nullable=True)
    startDate = db.Column(db.DateTime, default=datetime.now, nullable=False)
    file = db.Column(db.String(255))
    fileName = db.Column(db.String(255), nullable=False, index=True)
    imageUrl = db.Column(db.String(512), nullable=True)
    api = db.Column(db.String(20), nullable=True)
    api_info = db.Column(db.JSON, nullable=True)
    updateTime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

# 自定义快速JSON响应函数（原逻辑保留）
def fast_json(data, status_code=200):
    try:
        json_str = ujson.dumps(data, ensure_ascii=False)
        response = Response(
            json_str,
            status=status_code,
            mimetype='application/json; charset=utf-8'
        )
        response.headers['Cache-Control'] = 'public, max-age=60'
        return response
    except Exception as e:
        return Response(
            ujson.dumps({"error": f"序列化失败: {str(e)}"}),
            status=500,
            mimetype='application/json'
        )



# 路由注册函数（将路由绑定到指定 app）
def register_routes(app):
    #主页，也是帮助页面
    @app.route('/')
    def index():
        return render_template('index.html')
        
    # 评论查询接口
    @app.route("/api/v2/comment/<episodeId>", methods=["GET"])
    def get_comments(episodeId):
        # 保持原有实现...
        starttime = time.time()
        try:
            episode = AnimeEpisode.query.with_entities(AnimeEpisode.file)\
                        .filter_by(episodeId=episodeId).first()
            
            if not episode or not episode.file or not os.path.exists(episode.file):
                if redirect302:
                        return redirect(redirect302+f'api/v2/comment/{episodeId}')
                return fast_json({"count": 0, "comments": []})
            
            comments = []
            file_path = episode.file
            
            with open(file_path, 'r', encoding='utf-8-sig', buffering=65536) as f:
                reader = csv.DictReader(f)
                
                field_set = set(reader.fieldnames or [])
                if not {'cid', 'p', 'm'}.issubset(field_set):
                    missing = {'cid', 'p', 'm'} - field_set
                    return fast_json({
                        "count": 0,
                        "comments": [],
                        "error": f"CSV缺少字段: {missing}"
                    })
                
                for row in reader:
                    try:
                        comments.append({
                            'cid': int(row['cid']),
                            'p': row['p'].strip(),
                            'm': row['m'].strip()
                        })
                    except (ValueError, TypeError, KeyError):
                        continue
            count = len(comments)
            print(f"数据量: {count}, 耗时: {time.time() - starttime:.4f}秒")
            
            return fast_json({
                "count": count,
                "comments": comments
            })
            
        except Exception as e:
            return fast_json({
                "count": 0,
                "comments": [],
                "error": f"服务器错误: {str(e)}"
            })

    # 文件名匹配接口（修复原代码缩进错误）
    @app.route("/api/v2/match", methods=["POST"])
    def match_file():
        try:
            # print(f"当前数据库地址: {app.config['SQLALCHEMY_DATABASE_URI']}")
            data = request.get_json()
            
            if not data or "fileName" not in data:
                return fast_json({
                    "errorCode": 2,
                    "success": True,
                    "errorMessage": "请求缺少fileName参数",
                    "isMatched": False,
                    "matches": []
                })
            
            file_name = data["fileName"].replace(' ','%')
            print(f"匹配文件名: {file_name}")
            
            matches = AnimeEpisode.query.filter(
                AnimeEpisode.fileName.like(f'%{file_name}%')
            ).with_entities(
                AnimeEpisode.episodeId, AnimeEpisode.animeId, 
                AnimeEpisode.animeTitle, AnimeEpisode.episodeTitle,
                AnimeEpisode.imageUrl, AnimeEpisode.api, AnimeEpisode.api_info,AnimeEpisode.fileName
            ).order_by(
                AnimeEpisode.fileName
            ).all()
            print(f"匹配结果数量: {len(matches)}")
            pattern = r'(S)(\d+)(E)'
            match = re.search(pattern, file_name)
            
            if not matches:
                if redirect302:
                    file_name = data["fileName"]
                    chinese_nums = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                    '十一', '十二', '十三', '十四', '十五', '十六', '十七',
                    '十八', '十九', '二十']
                    if match:
                        s_part, num_str, e_part = match.groups()
                        num = int(num_str)
                        chinese_num = chinese_nums[num-1]
                        # 构造新的部分：原S数字E部分 + 插入的"第X季"
                        new_part = f'第{chinese_num}季 {s_part}{num_str}{e_part}'
                        data["fileName"]=re.sub(pattern, new_part, file_name)
                        html=requests.post(redirect302+f'api/v2/match',json=data,timeout=5)
                        if html.status_code==200:
                            d=html.json()
                            # print(d)
                            matches=d.get('matches',[])
                            if len(matches)>=1:
                                print(f"已从备份服务器中匹配到结果,数量: {len(matches)}")
                                animeTitle=matches[0].get('animeTitle')
                                episodeTitle=matches[0].get('episodeTitle')
                                if '(' in animeTitle:
                                    animeTitle=animeTitle.split('(')[0]
                                if '【' in animeTitle:
                                    animeTitle=animeTitle.split('【')[0]

                                episodeTitle=process_episode_title(episodeTitle)
                                matches[0]['animeTitle']=animeTitle
                                matches[0]['episodeTitle']=episodeTitle

                            return fast_json({
                    "errorCode": 0,
                    "success": True,
                    "errorMessage": "",
                    "isMatched": True,
                    "matches": matches
                })
                    
                    else:
                        return make_response(redirect(redirect302+f'api/v2/match'),307)
                    

                return fast_json({
                    "errorCode": 1,
                    "success": True,
                    "errorMessage": "未找到匹配的文件",
                    "isMatched": False,
                    "matches": []
                })
            
            match_items = [{
                "episodeId": item[0],
                "animeId": item[1],
                "animeTitle": f"{item[2]}-第{match.groups()[1]}部" if match else item[2],
                "episodeTitle": item[3] if item[3] else "电影",
                "type": "tvseries",
                "imageUrl": item[4],
                "api": item[5],
                "api_info": item[6]
            } for item in matches]

            return fast_json({
                "errorCode": 0,
                "success": True,
                "errorMessage": "",
                "isMatched": True,
                "matches": match_items
            })
        
        except Exception as e:
            return fast_json({
                "errorCode": 500,
                "success": False,
                "errorMessage": f"服务器错误: {str(e)}",
                "isMatched": False,
                "matches": []
            })
    # 动漫搜索接口
    @app.route("/api/v2/search/anime", methods=["GET"])
    def search_anime():
        # try:
            keyword = request.args.get('keyword', '').strip()
            redirect_keywords=keyword
            
            if not keyword:
                return fast_json({
                    "errorCode": 1,
                    "success": False,
                    "errorMessage": "请提供搜索关键词",
                    "animes": []
                })
            
            # 关键修复：将中文季数转换为S+数字格式（如"第六季"→"S6"）
            # 1. 定义中文数字到阿拉伯数字的映射
            chinese_num_map = {
                '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
                '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15
                # 可根据实际需求扩展更多数字
            }
            
            # 2. 正则匹配中文季数（如"第X季"）并替换
            def replace_chinese_season(match):
                chinese_num = match.group(1)  # 提取"第X季"中的X
                num = chinese_num_map.get(chinese_num, None)
                return f"S{num}" if num else match.group(0)  # 替换为S+数字，未匹配则保留原内容
            
            # 匹配"第X季"格式，其中X是中文数字
            keyword = re.sub(r'第([一二三四五六七八九十]+)季', replace_chinese_season, keyword)
            
            # 处理空格为通配符（原逻辑保留）
            keyword = keyword.replace(' ', '%')
            
            # 后续数据库查询及处理逻辑保持不变...
            query = AnimeEpisode.query.filter(
                AnimeEpisode.fileName.like(f'%{keyword}%')
            ).with_entities(
                AnimeEpisode.animeId, AnimeEpisode.animeTitle,
                AnimeEpisode.imageUrl, AnimeEpisode.startDate,
                AnimeEpisode.fileName
            ).order_by(
                AnimeEpisode.fileName
            ).all()
            
            if not query:
                if redirect302:
                        html=requests.get(redirect302+f"api/v2/search/anime?keyword={redirect_keywords}",timeout=3)
                        if html.status_code==200:
                            return fast_json(html.json())
                        # return redirect()
                return fast_json({
                    "errorCode": 0,
                    "success": True,
                    "errorMessage": "未找到匹配结果",
                    "animes": []
                })
            
            # 2. 核心逻辑：按「E分割后的基础名称（含季标识）」去重，合并集数
            animes_result = []  # 最终结果列表
            existing_bangumi_ids = set()  # 用于快速判断bangumiId是否已存在（去重）
            
            for item in query:
                animeId, animeTitle, imageUrl, startDate, fileName = item
                
                # 2.1 按"E"分割fileName，提取「基础名称+季标识」（如"爱人错过 S1E1"→"爱人错过 S1"）
                # split("E")[-2] 取E前面的部分（避免fileName含多个E的情况）
                split_by_E = fileName.split("E")
                if len(split_by_E) >= 2:
                    # 有E分隔（含集数）：取E前面的部分作为基础（如"S1E1"→"S1"）
                    base_with_season = split_by_E[-2].strip()
                else:
                    # 无E分隔（无明确集数）：直接用原fileName作为基础
                    base_with_season = fileName.strip()
                
                # 2.2 提取季标识（S+数字，如"S1"）和中文季数（如"S1"→"第1季"）
                # 遍历split后的单词，找包含"S"且后面跟数字的部分（如"爱人错过 S1"→"S1"）
                season_tag = ""  # 季标识（如"S1"）
                chinese_season = ""  # 中文季数（如"第1季"）
                for part in base_with_season.split():
                    if part.startswith(("S", "s")) and len(part) > 1 and part[1:].isdigit():
                        season_tag = part.upper()  # 统一转为大写（s1→S1）
                        season_num = part[1:]  # 提取数字（如"S1"→"1"）
                        chinese_season = f"第{season_num}季"  # 转为中文季数
                        break  # 找到第一个季标识即可（避免多个S的情况）
                
                # 2.3 生成bangumiId（核心去重键：基础名称+季标识）
                # 若有季标识，bangumiId=基础名称+季标识（如"爱人错过 S1"）
                # 若无季标识，bangumiId=基础名称（如"爱人错过"）
                bangumi_id = base_with_season if season_tag else base_with_season
                
                # 2.4 处理去重：若bangumiId已存在，仅累加集数；否则新增记录
                if bangumi_id in existing_bangumi_ids:
                    # 已存在：找到对应记录，集数+1
                    for result_item in animes_result:
                        if result_item["bangumiId"] == bangumi_id:
                            result_item["episodeCount"] += 1
                            result_item["startDate"] = startDate.strftime("%Y-%m-%d")
                            if imageUrl:
                                result_item["imageUrl"]=imageUrl
                            break
                else:
                    # 不存在：新增记录
                    # 处理开播时间（转为字符串，无则为空）
                    start_date_str = startDate.strftime("%Y-%m-%d") if startDate else ""
                    # 处理标题：原标题+中文季数（如"爱人错过"+"第1季"→"爱人错过 第1季"）
                    final_title = f"{animeTitle.strip()} {chinese_season}".strip()
                    # 处理海报图：优先用当前记录的imageUrl，无则为空
                    final_image_url = imageUrl.strip() if imageUrl else ""
                    
                    new_item = {
                        "animeId": animeId or 0,  # 无animeId时用0兜底
                        "bangumiId": bangumi_id,  # 核心：去重的键（如"爱人错过 S1"）
                        "animeTitle": final_title,  # 带中文季数的标题（如"爱人错过 第1季"）
                        "type": "tvseries",
                        "typeDescription": chinese_season or "无明确季数,可能是电影",  # 季数描述
                        "imageUrl": final_image_url,
                        "startDate": start_date_str,
                        "episodeCount": 1,  # 初始集数为1（当前记录算1集）
                        "rating": 0,
                        "isFavorited": True
                    }
                    
                    animes_result.append(new_item)
                    existing_bangumi_ids.add(bangumi_id)  # 加入去重集合
            
            # 3. （可选）按季数排序（如"S1"→"S2"→"S3"，避免乱序）
            def sort_by_season_num(item):
                # 从bangumiId中提取季数数字（如"S1"→1，无则0）
                for part in item["bangumiId"].split():
                    if part.startswith("S") and part[1:].isdigit():
                        return int(part[1:])
                return 0
            if redirect302 and len(animes_result)<=1:
                data=requests.get(redirect302+f'api/v2/search/anime?keyword={keyword}',timeout=3)
                if data.status_code==200:
                    data_json=data.json()
                    data_animes=data_json.get('animes',None)
                    if data_animes:
                        animes_result.extend(data_animes)
                        if data_animes[0]["type"]!='电影':
                            animes_result[0]['bangumiId']+=f'-{data_animes[0]["bangumiId"]}'
                            if animes_result[0]['episodeCount']<data_animes[0]['episodeCount']:
                                animes_result[0]['episodeCount']=data_animes[0]['episodeCount']
                            if (not animes_result[0]['imageUrl']) and data_animes[0]['imageUrl']:
                                animes_result[0]['imageUrl']=data_animes[0]['imageUrl']
                        
            # animes_result.sort(key=sort_by_season_num)
            
            # 4. 返回结果
            return fast_json({
                "errorCode": 0,
                "success": True,
                "errorMessage": "",
                "animes": animes_result,
                "totalSeasons": len(animes_result)  # 新增：返回总季数，便于前端展示
            })
            
    # 剧集搜索接口
    @app.route("/api/v2/bangumi/<keyword>", methods=["GET"])
    def search_bangumi(keyword):
        if redirect302:
            bangumiId=None
            if '-' in keyword:
                keyword,bangumiId=keyword.split('-')
        
        # 调整查询，包含fileName字段
        query = AnimeEpisode.query.filter(
                AnimeEpisode.fileName.like(f'%{keyword}%')
            ).with_entities(
                AnimeEpisode.episodeId, 
                AnimeEpisode.episodeTitle, 
                AnimeEpisode.animeTitle,
                AnimeEpisode.fileName  # 新增fileName用于提取season和episode信息
            ).order_by(
                func.cast(
                    func.substr(AnimeEpisode.episodeTitle, 2, func.length(AnimeEpisode.episodeTitle) - 2),
                    db.Integer
                )
            ).all()
        
        if not query:
            if redirect302:
                return redirect(redirect302+f'api/v2/bangumi/{keyword}')

        # 处理查询结果，提取seasonId和episodeNumber
        episodes = []
        for item in query:
            episode_id, episode_title, anime_title, file_name = item
            
            # 初始化默认值
            season_id = "1"  # 默认第一季
            episode_number = ""
            
            # 从fileName中提取seasonId (S后面的数字)和episodeNumber (E后面的数字)
            if file_name:
                # 提取Sx部分 (如S1, S2)
                s_match = re.search(r'S(\d+)', file_name, re.IGNORECASE)
                if s_match:
                    season_id = s_match.group(1)  # 获取S后面的数字
                
                # 提取Exx部分 (如E1, E23)
                e_match = re.search(r'E(\d+)', file_name, re.IGNORECASE)
                if e_match:
                    episode_number = e_match.group(1)  # 获取E后面的数字
            
            # 构建单集数据
            episodes.append({
                "seasonId": season_id,
                "episodeId": episode_id,
                "episodeTitle": episode_title if episode_title else anime_title,
                "episodeNumber": episode_number
            })

            if redirect302:
                if bangumiId:
                    data=requests.get(redirect302+f'api/v2/bangumi/{bangumiId}',timeout=3)
                    if data.status_code==200:
                        data_json=data.json()
                        episodes=merge_and_process(data_json['bangumi'].get('episodes'),episodes)
 

        # 返回修改后的JSON结构
        return fast_json({
            "errorCode": 0,
            "success": True,
            "errorMessage": "error",
            "bangumi": {
                "episodes": episodes
            }
        })
     # 新增登录路由
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            data_user,data_pwd=config_manager.get_user_path()

            if username == data_user and data_pwd == password:
                session['username'] = username
                session.permanent = True
                app.permanent_session_lifetime = timedelta(hours=2)
                return redirect('/admin')
            return render_template('login.html', error="用户名或密码错误")
        if 'username' in session:
            return redirect('/admin')
        return render_template('login.html', error="")

    # 新增退出路由
    @app.route('/logout')
    def logout():
        session.pop('username', None)
        return redirect('/login')

    # 管理页路由
    @app.route('/admin')
    @login_required
    def admin_index():
        return render_template('admin.html', username=session.get('username'))

    # CRUD API接口
    # 1. 获取所有数据（分页）
    @app.route('/api/admin/episodes', methods=['GET'])
    @login_required
    def get_all_episodes():
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        keyword = request.args.get('keyword', '').strip()
        
        query = AnimeEpisode.query.order_by(AnimeEpisode.id.desc())  # 按id排序
        if keyword:
            keyword = f'%{keyword}%'
            query = query.filter(
                db.or_(
                    AnimeEpisode.fileName.like(keyword),
                    AnimeEpisode.animeTitle.like(keyword)
                )
            )
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        episodes = [{
            'id': item.id,  # 使用id作为主键标识
            'animeTitle': item.animeTitle,
            'episodeTitle': item.episodeTitle,
            'fileName': item.fileName,
            'updateTime': item.updateTime.strftime('%Y-%m-%d %H:%M:%S') if item.updateTime else '',
            'file': item.file
        } for item in pagination.items]
        return fast_json({
            'data': episodes,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        })
    
    @app.route('/api/admin/episodes/<int:id>', methods=['GET'])
    @login_required
    def get_episode(id):  # 参数名改为id
        episode = AnimeEpisode.query.get(id)  # 使用id查询
        if not episode:
            return fast_json({'error': '记录不存在'}, 404)
        
        return fast_json({
            'id': episode.id,  # 返回id
            'animeTitle': episode.animeTitle,
            'episodeTitle': episode.episodeTitle,
            'fileName': episode.fileName,
            'startDate': episode.startDate.strftime('%Y-%m-%d'),
            'file': episode.file,
            'imageUrl': episode.imageUrl,
            'api': episode.api,
            'api_info': episode.api_info
        })

    # 2. 新增数据
    @app.route('/api/admin/episodes', methods=['POST'])
    @login_required
    def add_episode():
        data = request.get_json()
        if not data.get('fileName') or not data.get('file'):
            return fast_json({'error': '文件名和URL为必填项'}, 400)
        
        try:
            # 自动识别逻辑
            file_name = data.get('fileName')
            url = data.get('file')
            anime_title = ""
            episode_title = ""

            name=file_name.split('E')
            if len(name)>1:
                episode_title = f"第{name[-1]}集"
            anime_title=file_name.split()[0]

            if 'v.qq.com' in url:
                danmu_api=TencentFetcher(url=url)
                api='腾讯视频'
            elif 'bilibili.com' in url:
                print("警告:获取BiliBili时需要指定有效的Cookie路径,以获取更多弹幕")
                danmu_api=BilibiliFetcher(url=url)
                api='BiliBili'
            elif 'mgtv.com' in url:
                danmu_api=MgtvFetcher(url=url)
                api='芒果TV'
            elif 'iqiyi.com' in url:
                danmu_api=IqiyiFetcher(url=url)
                api='爱奇艺'
            else:
                print("警告:无法更新的接口")
                return fast_json({'error': '新增失败：无法更新的接口'})
            
            
            save_file_path = str(Path(config_manager.get_db_path()+'/danmu_data/'+file_name+'.csv'))


            danmu_data,duration,title = danmu_api.run()
            save_as_csv(save_file_path, danmu_data)

            query = AnimeEpisode.query.order_by(AnimeEpisode.id.desc()).first()


            new_episode = AnimeEpisode(
                animeTitle=anime_title or file_name,
                episodeTitle=episode_title or file_name,
                fileName=file_name,
                file=save_file_path,
                startDate=datetime.now(),
                updateTime=datetime.now(),
                episodeId=query.episodeId+1,
                animeId=query.episodeId+1,
                api_info={'id':url,"start_time": 0,"end_time": 0},
                api=api
            )
            db.session.add(new_episode)
            db.session.commit()


            return fast_json({'success': True, 'message': '新增成功','msg':len(danmu_data)})
        except Exception as e:
            db.session.rollback()
            print(str(e))
            return fast_json({'error': f'新增失败：{str(e)}'}, 500)

    @app.route('/api/admin/episodes/<int:id>', methods=['PUT'])
    @login_required
    def update_episode(id):
        data = request.get_json()
        episode = AnimeEpisode.query.get(id)
        if not episode:
            return fast_json({'error': '记录不存在'}, 404)
        
        try:
            # 更新字段
            episode.fileName = data.get('fileName', episode.fileName)
            episode.animeTitle = data.get('animeTitle', episode.animeTitle)
            episode.episodeTitle = data.get('episodeTitle', episode.episodeTitle)
            episode.api_info = data.get('api_info', episode.api_info)
            episode.imageUrl = data.get('imageUrl', episode.imageUrl)

            db.session.commit()
            return fast_json({'success': True, 'message': '更新成功'})
        except Exception as e:
            db.session.rollback()
            return fast_json({'error': f'更新失败：{str(e)}'}, 500)

    # 4. 删除数据
    @app.route('/api/admin/episodes/<int:id>', methods=['DELETE'])
    @login_required
    def delete_episode(id):
        episode = AnimeEpisode.query.get(id)
        if not episode:
            return fast_json({'error': '记录不存在'}, 404)
        
        if os.path.exists(episode.file):
            try:
                os.remove(episode.file)
            except PermissionError:
                print("❌ 权限不足,本地文件删除失败")
                return fast_json({'error': '权限不足,本地文件删除失败'}, 404)
            except OSError as e:
                print(f"❌ 本地文件删除失败：{e}（文件路径：{episode.file}）")
                return fast_json({'error': '本地文件删除失败'}, 404)
            
        db.session.delete(episode)
        db.session.commit()
        return fast_json({'success': True})
    
    @app.route('/api/admin/episodes/update/<int:id>', methods=['GET'])
    @login_required
    def update_file_episode(id):
        episode = AnimeEpisode.query.get(id)
        if not episode:
            return fast_json({'error': '记录不存在'}, 404)
        
        # db.session.delete(episode)
        if not episode.api_info:
            return fast_json({'error': '数据库源信息有问题无法更新'}, 404)

        url=episode.api_info.get('id',"")
        save_file_path=episode.file
               

        if 'v.qq.com' in url:
            danmu_api=TencentFetcher(url=url)
        elif 'bilibili.com' in url:
            print("警告:获取BiliBili时需要指定有效的Cookie路径,以获取更多弹幕")
            danmu_api=BilibiliFetcher(url=url)
        elif 'mgtv.com' in url:
            danmu_api=MgtvFetcher(url=url)
        elif 'iqiyi.com' in url:
            danmu_api=IqiyiFetcher(url=url)
        else:
            print("警告:无法更新的接口")
            return fast_json({'success': False})
        
        
        danmu_data,duration,title = danmu_api.run()

        save_as_csv(save_file_path, danmu_data)
        episode.updateTime=datetime.now()

        db.session.commit()

        return fast_json({'success': True,'msg':len(danmu_data)})


def save_as_csv( file_path, danmu_data):
    """将弹幕数据保存为CSV格式"""
    id=1
    with open(file_path, 'w', encoding='utf-8-sig') as f:
        # 写入表头
        f.write("cid,p,m\n")
        # 写入数据
        for item in danmu_data:
            time_offset=item["time_offset"]/1000
            f.write(f"""{id},"{time_offset:.3f},{item['mode']},{item['color']},[get-danmu]{id}",{item['content']}\n""")
            id+=1

def process_episode_title(title: str) -> str:
    """处理单集标题，提取#包裹内容并标准化"""
    match = re.search(r'#(.*?)#', title)
    if not match:
        return title  # 无#包裹时返回原标题
    
    content = match.group(1).strip()
    # 检查是否包含“第xx集”或“第xx话”
    if re.search(r'第\d+[集话]', content):
        return content
    # 否则转换为“第xx集”（假设content是数字）
    if content.isdigit():
        return f"第{content}集"
    return content  # 非数字情况保留原始内容

def merge_and_process(list1, list2):
    """合并两个列表，以list2数据优先去重，再处理标题"""
    # 1. 构建去重字典：以episodeNumber（整数）为键，list2元素优先
    unique_episodes = {}
    # 先加list1的元素（后续list2同编号会覆盖它）
    for ep in list1:
        try:
            ep_num = int(ep['episodeNumber'])
        except (ValueError, KeyError):
            continue  # 跳过无效数据
        unique_episodes[ep_num] = ep  # 暂存list1的元素
    
    # 再加list2的元素（覆盖list1中同编号的元素，实现list2优先）
    for ep in list2:
        try:
            ep_num = int(ep['episodeNumber'])
        except (ValueError, KeyError):
            continue  # 跳过无效数据
        unique_episodes[ep_num] = ep  # 用list2的元素覆盖
    
    # 2. 处理标题并转换为列表（按episodeNumber排序，可选）
    processed = []
    for ep in unique_episodes.values():
        # 复制原字典并替换处理后的标题
        new_ep = ep.copy()
        new_ep['episodeTitle'] = process_episode_title(ep['episodeTitle'])
        processed.append(new_ep)
    
    # 3. 按episodeNumber从小到大排序（可选，根据需求决定是否保留）
    processed.sort(key=lambda x: int(x['episodeNumber']))
    return processed



# 对外提供的核心函数：创建 Flask 应用
def create_danmu_app(db_path='sqlite:///danmu_data.db', compress_level=6,redirect_url=None):
    """
    创建弹幕服务 Flask 应用
    
    Args:
        db_path: SQLite 数据库 URI（如 'sqlite:///C:/test/db.db' 或 'sqlite:///:memory:'）
        compress_level: 压缩级别（默认6，若不需要压缩可设为None）
    
    Returns:
        Flask 应用实例
    """
    global redirect302
    if redirect_url:
        redirect302=redirect_url
    # 初始化 Flask 应用
    app = Flask(__name__)

    app.secret_key = 'scabcs*^%$cna8&*&T78a*HX(Hch9accah9HC8ac9acac){/?..#acac'  # 替换为任意随机字符串
    
    # 配置应用
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path  # 自定义数据库地址
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭不必要的修改跟踪
    if compress_level is not None:
        app.config['COMPRESS_LEVEL'] = compress_level  # 压缩配置（可选）
    
    # 初始化数据库（绑定 app）
    db.init_app(app)
    
    # 注册所有路由
    register_routes(app)

    
    # 创建数据库表（确保表存在）
    with app.app_context():
        db.create_all()
    return app


# 保留独立运行能力（直接运行该文件时生效）
if __name__ == "__main__":
    # 默认配置：数据库在当前目录，端口80
    app = create_danmu_app(
        db_path='sqlite:///danmu_data.db',  # 默认数据库地址
        compress_level=6
    )
    app.run(host="0.0.0.0", port=80, debug=True, threaded=True)



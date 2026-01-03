import argparse
import getpass
import os
from pathlib import Path
import sys
import winreg
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from . import __version__
from .core import DanmuGetter,DanmuWebServer
from .config import ConfigManager
from .utils.danmu_updata import DanmuDataManager
from .utils.update import check_and_add_updatetime_field

# 初始化Rich控制台
console = Console()

def show_help(parser):
    """显示美化的帮助信息"""
    title = Text("get-danmu", style="bold magenta")
    title.append(f" v{__version__}", style="green")
    
    console.print(title)
    console.print("获取弹幕工具，支持多种参数配置\n", style="italic")
    
    # 参数表格
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("参数", style="bold")
    table.add_column("说明")
    
    # 位置参数
    table.add_row("url", "目标视频的URL链接（可选）")
    
    # 通用参数
    table.add_row("-h, --help", "显示帮助信息")
    table.add_row("-v, --version", "显示版本信息")
    table.add_row("--clear", "清理所有配置")
    
    # 网络参数
    table.add_row("--proxy", "设置代理服务器（例如 http://localhost:8080），不带参数则清理代理")
    table.add_row("--cookie", "读取cookie文件的路径")
    
    # 时间参数
    table.add_row("--start", "开始时间，格式为 分钟.秒 或 分钟:秒（例如 10:30 或 5.45）")
    table.add_row("--end", "结束时间，格式为 分钟.秒 或 分钟:秒")
    table.add_row("--resettime, -R", "重置时间参数（仅与--start同时可用）")
    
    # 输出参数
    table.add_row("--type", "设置输出数据类型，支持 csv 和 xml，默认是 csv")
    table.add_row("--savepath, -s", "设置保存位置，默认是当前目录")

    # 弹幕数据服务器参数
    table.add_row("--runserver [端口]", "启动Web弹幕服务（单独使用），默认端口80")
    table.add_row("--db 路径", "设置SQLite数据库文件路径（会保存到配置）")
    table.add_row("--redirect 路径", "设置备选弹幕服务器url，当本地没有数据时会自动重定向到备选服务器（会保存到配置）")
    table.add_row("-S", "启用弹幕数据双保存：文件+SQLite数据库(CSV格式)")
    table.add_row("--data", "进入数据库管理")
    table.add_row("--user", "创建Web管理的管理员账号")
    table.add_row("--update", "处理低版本升级到高版本遗留的数据字段不匹配问题")
    
    console.print(table)
    
    # 示例
    console.print("\n[bold]示例:[/bold]")
    examples = [
        "get-danmu",  # 交互输入URL
        "get-danmu https://example.com/video",
        "get-danmu https://example.com/video --start 10:10 --end 30:20",
        "get-danmu https://example.com/video --type xml -s ./output",
        "get-danmu --proxy http://localhost:8080",
        "get-danmu --proxy  # 清理代理配置",
        "get-danmu --clear  # 清理所有配置"
    ]
    for example in examples:
        console.print(f"  {example}", style="green")

def parse_time(time_str):
    """
    将时间字符串（分钟.秒 或 分钟:秒）转换为总秒数
    返回: 总秒数（整数）或None
    """
    # 严格检查输入类型
    if not isinstance(time_str, str):
        raise TypeError(f"时间参数必须是字符串，实际得到: {type(time_str).__name__}")
    
    # 移除可能的空白字符
    time_str = time_str.strip()
    
    if not time_str:
        return None
        
    # 支持 . 或 : 作为分隔符
    if '.' in time_str:
        parts = time_str.split('.', 1)
    elif ':' in time_str:
        parts = time_str.split(':', 1)
    else:
        raise ValueError(f"无效的时间格式: {time_str}，请使用 分钟.秒 或 分钟:秒")
    
    # 验证部分数量
    if len(parts) < 1 or len(parts) > 2:
        raise ValueError(f"时间格式错误: {time_str}，请使用 分钟.秒 或 分钟:秒")
    
    try:
        # 解析分钟部分
        minutes = int(parts[0])
        if minutes < 0:
            raise ValueError("分钟不能为负数")
        
        # 解析秒部分（如果存在）
        seconds = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        if seconds < 0 or seconds >= 60:
            raise ValueError("秒必须在0-59之间")
            
        return minutes * 60 + seconds
    except ValueError as e:
        raise ValueError(f"时间格式错误: {time_str}，{str(e)}")

def show_config_summary(args, proxy, url, db_path):
    """显示当前配置摘要"""
    table = Table(title="配置摘要", title_style="bold green")
    table.add_column("项目", style="cyan")
    table.add_column("值")
    
    table.add_row("URL", url or "未提供")
    table.add_row("代理", proxy or "未设置")
    table.add_row("输出类型", args.type)
    table.add_row("保存路径", args.savepath or "当前目录")
    table.add_row("Cookie文件", args.cookie or "未设置")
    # 新增数据库相关显示
    table.add_row("数据库路径", db_path or "未配置（使用--db设置）")
    table.add_row("数据库保存模式", "启用" if args.S else "禁用")
    
    # 处理时间参数，增加错误捕获
    start_seconds = None
    start_display = "未设置"
    if args.start:
        try:
            start_seconds = parse_time(args.start)
            start_display = f"{args.start} ({start_seconds}秒)"
        except (ValueError, TypeError) as e:
            start_display = f"[red]{args.start} (错误: {str(e)})[/red]"
    
    end_seconds = None
    end_display = "未设置"
    if args.end:
        try:
            end_seconds = parse_time(args.end)
            end_display = f"{args.end} ({end_seconds}秒)"
        except (ValueError, TypeError) as e:
            end_display = f"[red]{args.end} (错误: {str(e)})[/red]"
    
    table.add_row("开始时间", start_display)
    table.add_row("结束时间", end_display)
    table.add_row("重置时间", "是" if args.resettime else "否")
    
    console.print(table)
    
    # 如果时间解析有错误，返回False
    return start_seconds is not None or not args.start, end_seconds is not None or not args.end

def main():
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        prog='get-danmu',
        description='获取弹幕工具',
        add_help=False  # 禁用默认帮助，使用自定义帮助
    )
    
    # 位置参数：URL链接
    parser.add_argument(
        'url', 
        nargs='?',  # 可选参数
        help='目标视频的URL链接'
    )
    
    # 可选参数
    parser.add_argument(
        '-v', '--version', 
        action='version', 
        version=f'%(prog)s {__version__}'
    )
    
    parser.add_argument(
        '--proxy', 
        nargs='?',  # 允许不带参数
        const='__clear__',  # 当--proxy不带参数时使用此值
        help='设置代理服务器，例如 http://localhost:8080，不带参数则清理代理'
    )
    
    parser.add_argument(
        '--start', 
        help='开始时间，格式为 分钟.秒 或 分钟:秒'
    )
    
    parser.add_argument(
        '--end', 
        help='结束时间，格式为 分钟.秒 或 分钟:秒'
    )
    
    parser.add_argument(
        '--resettime', '-R', 
        action='store_true', 
        help='重置时间参数（仅与--start同时可用）'
    )
    
    parser.add_argument(
        '--type', 
        default='csv', 
        help='设置输出数据类型，支持 csv 和 xml，默认是 csv'
    )
    
    parser.add_argument(
        '--savepath', '-s', 
        help='设置保存位置，默认是当前目录'
    )
    
    parser.add_argument(
        '--cookie', 
        help='读取cookie文件的路径'
    )
    
    parser.add_argument(
        '--clear', 
        action='store_true', 
        help='清理所有配置'
    )

    parser.add_argument(
        '--data', 
        action='store_true', 
        help='进入数据库管理'
    )

    parser.add_argument(
        '--user', 
        action='store_true', 
        help='创建Web管理员账号'
    )

    parser.add_argument(
        '--update', 
        action='store_true', 
        help='处理高低版本数据库字段问题'
    )
    
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help='显示帮助信息'
    )
    parser.add_argument(
        '--runserver',
        nargs='?',
        const=80,
        type=int,
        help='启动Web弹幕服务（单独使用），默认端口80'
    )
    parser.add_argument(
        '--db',
        nargs='?',  # 允许不带参数
        const='__clear__',  # 当--db不带参数时使用此值
        help='设置SQLite数据库文件路径，会保存到配置'
    )
    parser.add_argument(
        '--redirect',
        nargs='?',  # 允许不带参数
        const='__clear__',  # 当--redirect不带参数时使用此值
        help='设置备选弹幕服务器url，会保存到配置'
    )
    parser.add_argument(
        '-S',
        action='store_true',
        help='启用弹幕数据双保存：文件+SQLite数据库'
    )
    
    # 解析参数
    try:
        args = parser.parse_args()
    except Exception as e:
        console.print(Panel(
            f"参数解析错误: {str(e)}",
            border_style="red"
        ))
        return
    


    # 显示帮助信息
    if args.help:
        show_help(parser)
        return
    
    
    
    # 验证-R参数只能与--start同时使用
    if args.resettime and not args.start:
        console.print(Panel(
            "错误: -R/--resettime 只能与 --start 同时使用", 
            border_style="red"
        ))
        return
    
    
    
    # 验证输出类型只能是csv或xml
    if args.type.lower() not in ['csv', 'xml']:
        console.print(Panel(
            f"错误: 不支持的输出类型 '{args.type}'，仅支持 csv 和 xml", 
            border_style="red"
        ))
        return
    args.type = args.type.lower()  # 统一转为小写
    
    # 初始化配置管理器
    config_manager = ConfigManager()


    # 创建管理员账号
    if args.user:
        username = input("请输入用户名: ")
        password = getpass.getpass("请输入密码: ")
        password_two = getpass.getpass("请确认密码: ")
        if password != password_two:
            console.print(Panel(
                        "错误: 两次的密码不一致", 
                        border_style="red"
                    ))
            return
        config_manager.save_user_data(username,password)
        console.print(Panel(
                f"管理员信息已保存:{username}", 
                border_style="green"
            ))
        return
    
    if args.update:
        db_path=config_manager.get_db_path()
        if not db_path:
            console.print(Panel(
                        "错误: 未使用过弹幕数据库无需检查更新", 
                        border_style="red"
                    ))
            return
        db_path=db_path+'/danmu_data.db'
        result=check_and_add_updatetime_field(db_path)
        if result:
            console.print(Panel(
                f"数据库已升级成功", 
                border_style="green"
            ))
        else:
            console.print(Panel(
                        "操作失败", 
                        border_style="red"
                    ))
        return
    
    # 处理清理所有配置
    if args.clear:
        config_manager.clear_all_config()
        console.print(Panel(
            "所有配置已清理", 
            border_style="green"
        ))
        # 如果只是清理配置，不继续执行其他操作
        if not args.url and not args.proxy:
            return
    
    # 处理代理设置
    proxy = None
    if args.proxy is not None:
        # 处理代理清理
        if args.proxy == '__clear__' or args.proxy.strip() == '':
            config_manager.clear_proxy()
            console.print(Panel(
                "代理配置已清理", 
                border_style="green"
            ))
        else:
            # 设置新代理
            config_manager.save_proxy(args.proxy)
            console.print(Panel(
                f"代理已保存: {args.proxy}", 
                border_style="green"
            ))
            proxy = args.proxy
        if not args.url:
            return
    else:
        # 获取保存的代理
        proxy = config_manager.get_proxy()
        # 检测windows下是否使用了系统代理
        if sys.platform.startswith('win'):
            if winreg.QueryValueEx(winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER,
                                                        r'Software\Microsoft\Windows\CurrentVersion\Internet Settings', 0, winreg.KEY_ALL_ACCESS), "ProxyEnable")[0] == 1:
                    ip, port = winreg.QueryValueEx(winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER,
                                                        r'Software\Microsoft\Windows\CurrentVersion\Internet Settings', 0, winreg.KEY_ALL_ACCESS), "ProxyServer")[0].split(":")
                    console.print(f"[blue]提示: 检测到系统使用了代理，代理IP:[red]{ip}[/red]代理端口:[red]{port}[/red][/blue]")
                    if Confirm.ask("是否使用该代理?", default=False):
                        proxy=f'http://{ip}:{port}'
                        console.print(f"[green]设置成功[/green],[red]仅本次操作有效[/red]")

    # 处理数据库路径配置
    if args.db:
        # 处理数据库清理
        if args.db == '__clear__' or args.db.strip() == '':
            config_manager.clear_db_path()
            console.print(Panel(
                "数据库配置已清理", 
                border_style="green"
            ))
        else:
            # 设置新数据库配置
            config_manager.save_db_path(args.db)
            console.print(Panel(f"SQLite数据库路径已保存: {args.db}", border_style="green"))
        return
    
    # 处理备选弹幕服务器配置
    if args.redirect:
        # 处理备选弹幕服务器清理
        if args.redirect == '__clear__' or args.redirect.strip() == '':
            config_manager.clear_redirect_path()
            console.print(Panel(
                "备选弹幕服务器地址配置已清理", 
                border_style="green"
            ))
        else:
            # 设置备选弹幕服务器配置
            config_manager.save_redirect_path(args.redirect)
            console.print(Panel(f"备选弹幕服务器已保存: {args.redirect}", border_style="green"))
        return

    # Web服务模式（单独使用，不执行弹幕获取）
    if args.runserver is not None:
        # 验证端口有效性
        port = args.runserver
        if not (0 < port <= 65535):
            console.print(Panel(f"无效端口号: {port}（需在1-65535之间）", border_style="red"))
            return
                
        
        # try:
        db_path = config_manager.get_db_path()
        if not db_path:
            console.print(Panel("请使用get-danmu --db path 指定数据库存放位置后再运行服务器", border_style="red"))
            return
        redirect_url = config_manager.get_redirect_path()
        # 启动Web服务
        console.print(Panel(f"正在启动Web弹幕服务...\n端口: {port}\n数据库存放位置:{db_path if db_path else '未配置'}\n备选弹幕服务器地址:{redirect_url if redirect_url else '未配置'}", border_style="blue"))
        web_server = DanmuWebServer(port=port, db_path=db_path,redirect_url=redirect_url)
        web_server.run()  # 实际Flask逻辑由用户实现
        # except Exception as e:
        #     console.print(Panel(f"Web服务启动失败: {str(e)}", border_style="red"))
        return
    
    # 数据库管理
    if args.data:
        db_path = config_manager.get_db_path()
        try:
            if not os.path.exists(db_path):
                os.makedirs(db_path)
        except:
            console.print(f"[red]错误: 请使用get-danmu --db path 指定数据库存放位置后再运行方可保存至数据库[/red]")
            return 
        db_path=str(Path(db_path)).replace("\\", "/")
        # 拼接数据库文件完整路径
        custom_db_path = db_path+ '/danmu_data.db'

        manager = DanmuDataManager(db_path=custom_db_path,
                                   proxy=proxy,
                                   resettime=True if args.resettime else False,
                                   cookie_path=args.cookie)
        manager.run()
        return
    

    # 处理URL参数 - 支持交互输入
    url = args.url
    # 如果没有提供URL且不是只执行清理等操作，则交互获取URL
    if not url and not (args.proxy is not None or args.clear):
        console.print(Panel("请输入目标视频的URL链接（直接回车退出）", border_style="blue"))
        try:
            url = input("> ").strip()
            # 如果用户仍然输入空，则退出程序
            if not url:
                console.print(Panel("未输入URL，程序退出", border_style="yellow"))
                return
        except (KeyboardInterrupt, EOFError):
            console.print("\n" + "[red]程序已取消[/red]")
            return
    
    # 如果提供了URL，创建DanmuGetter实例并处理
    if url:
        # try:
            # 显示配置摘要并检查时间参数是否有效
            # 显示配置摘要
            db_path = config_manager.get_db_path()
            start_valid, end_valid = show_config_summary(args, proxy, url,db_path)
            
            # 如果时间参数无效，不继续执行
            if not (start_valid and end_valid):
                console.print(Panel(
                    "时间参数格式错误，请检查并重试",
                    border_style="red"
                ))
                return
            
            # 解析时间参数为秒（已在show_config_summary中验证过，这里直接解析）
            start_seconds = parse_time(args.start) if args.start else None
            end_seconds = parse_time(args.end) if args.end else None
            
            # 创建弹幕获取器实例
            danmu_getter = DanmuGetter(
                url=url,
                proxy=proxy,
                cookie_path=args.cookie,
                resettime=True if args.resettime else False,
                save_to_db=args.S,
                db_path=db_path
            )
            
            # 设置时间范围（秒）
            if start_seconds or end_seconds:
                danmu_getter.set_time_range(start_seconds, end_seconds)
            
            # 设置数据类型
            danmu_getter.set_data_type(args.type)
            
            # 设置保存路径
            if args.savepath:
                danmu_getter.set_save_path(args.savepath)
            
            # 执行获取弹幕
            console.print("\n[bold cyan]开始获取弹幕...[/bold cyan]")
            result = danmu_getter.run()
            
            # 显示成功信息
            console.print(Panel(
                f"成功获取 {result['count']} 条弹幕\n保存路径: {result['save_path']}",
                title="操作完成",
                border_style="green"
            ))
            
        # except Exception as e:
        #     console.print(Panel(
        #         f"错误: {str(e)}",
        #         border_style="red"
        #     ))
        #     exit(1)

if __name__ == "__main__":
    main()

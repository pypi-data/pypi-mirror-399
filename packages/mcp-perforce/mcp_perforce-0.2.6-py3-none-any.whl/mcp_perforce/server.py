import asyncio
import os
import json
import re
import base64
import requests
import argparse
import subprocess
from bs4 import BeautifulSoup

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

# Store notes as a simple key-value dict to demonstrate state management
notes: dict[str, str] = {}

# 全局API会话
api_session = None
# 全局配置文件路径
config_file_path = "p4config.json"

server = Server("mcp_perforce")

# 解析命令行参数
def parse_arguments():
    parser = argparse.ArgumentParser(description='Perforce服务工具')
    parser.add_argument('--p4config', '-c', type=str, help='p4config.json配置文件的路径', default="p4config.json")
    return parser.parse_args()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="get-changelist-files-catalog",
            description="Get the files catalog in a changelist",
            inputSchema={
                "type": "object",
                "properties": {"changelist_id": {"type": "integer"}},    
                "required": ["changelist_id"],
            },
        ),
        types.Tool(
            name="get-file-details",
            description="Get the details of a file in a changelist",
            inputSchema={
                "type": "object",
                "properties": {"action": {"type": "string"}, "file_path": {"type": "string"}, "revision": {"type": "integer"}, "changelist_id": {"type": "integer"}},
                "required": ["action", "file_path", "revision", "changelist_id"],
            },
        ),
        types.Tool(
            name="get-changelist-diff-native",
            description="使用P4原生命令获取CL中的变更文件列表和文件差异。先用p4 describe获取文件列表，再用p4 diff2获取每个文件的差异",
            inputSchema={
                "type": "object",
                "properties": {
                    "changelist_id": {
                        "type": "integer",
                        "description": "Perforce变更列表ID(CL号)"
                    }
                },
                "required": ["changelist_id"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    处理工具执行请求。
    目前 cursor 只支持简单工具的调用 无法处理资源修改等其他功能
    """
    if name == "get-changelist-files-catalog":
        res = await get_changelist_files_catalog(arguments.get("changelist_id"))
        return [types.TextContent(type="text", text=res)]
    elif name == "get-file-details":
        res = await get_file_details(arguments.get("action"), arguments.get("file_path"), arguments.get("revision"), arguments.get("changelist_id"))
        return [types.TextContent(type="text", text=res)]
    elif name == "get-changelist-diff-native":
        res = await get_changelist_diff_native(arguments.get("changelist_id"))
        return [types.TextContent(type="text", text=res)]
    else:
        raise ValueError(f"Unknown tool: {name}")

# 获取变更列表文件目录
async def get_changelist_files_catalog(changelist_id: int) -> str:
    """
    获取变更列表文件目录
    """
    try:
        # 检查Swarm配置
        if not SWARM_USERNAME or not SWARM_PASSWORD:
            return f"错误: 未配置Swarm用户名或密码，请在配置文件 {config_file_path} 中添加swarm_username和swarm_password"
        
        if not SWARM_BASE_URL or not SWARM_API_URL:
            return f"错误: 未配置Swarm URL，请在配置文件 {config_file_path} 中添加swarm_base_url和swarm_api_url"
        
        # 获取变更列表文件
        files_data = get_changelist_files(api_session, changelist_id)
        if not files_data:
            return f"错误: 无法获取变更列表 {changelist_id} 的文件列表"
        
        # 提取文件列表
        files = files_data.get('files', [])
        root = files_data.get('root', '')
        
        # 格式化输出
        skip_ext_str = ', '.join([f'*{ext}' for ext in SKIP_FILE_EXTENSIONS])
        formatted_info = f"""
变更列表: {changelist_id}
根路径: {root}

受影响的文件(已忽略二进制文件, {skip_ext_str}):
"""
        
        # 添加文件列表
        for file_info in files:
            file_path = file_info.get('depotFile', '')
            action = file_info.get('action', '')
            revision = file_info.get('rev', '')
            file_type = file_info.get('type','')

            if file_type == 'binary' or should_skip_file(file_path):
                continue
            formatted_info += f"- {action} {file_path}#{revision}\n"
        
        return formatted_info
    
    except Exception as e:
        error_msg = f"获取变更列表文件目录时出错: {str(e)}"
        print(error_msg)
        return error_msg

# 获取每个文件的详细信息
async def get_file_details(action: str, file_path: str, revision: int, changelist_id: int) -> str:
    """
    获取每个文件的详细信息
    """
    formatted_info = ""
    # 对于删除的文件，不获取差异
    if action == 'delete':
        formatted_info += f"\n==== {file_path}#{revision} (已删除) ====\n\n"
    # 对于新增的文件，获取文件完整内容
    elif action == 'add':
        file_content_data = get_file_complete_content(api_session, file_path, changelist_id)
        formatted_info += f"\n==== {file_path}#{revision} (新增文件) ====\n\n"
        formatted_info += analysis_diff_data(file_content_data, file_path)
    else:
        # 对于编辑的文件，获取文件差异
        diff_data = get_file_diff(api_session, file_path, revision, changelist_id)
        if not diff_data:
            diff_data = get_file_diff_with_previous_version(api_session, file_path, revision, changelist_id)
        if not diff_data:
            formatted_info += f"\n==== {file_path}#{revision} (无法获取文件差异信息) ====\n\n"
        else:
            # 分析差异
            analysis = analyze_file_changes(diff_data)
            formatted_info += analysis_diff_data(analysis, file_path)

    return formatted_info


# 使用P4原生命令获取CL差异
async def get_changelist_diff_native(changelist_id: int) -> str:
    """
    使用P4原生命令获取CL中的变更文件列表和文件差异
    1. p4 describe -s -S <CL号> 获取变更文件列表
    2. p4 diff2 <文件路径> <文件路径>@=<CL号> 遍历文件列表查看差异
    """
    try:
        formatted_info = f"变更列表: {changelist_id}\n"
        formatted_info += "=" * 60 + "\n\n"
        
        # 1. 使用 p4 describe -s -S 获取shelved CL的文件列表
        describe_cmd = ["p4", "describe", "-s", "-S", str(changelist_id)]
        
        describe_result = subprocess.run(
            describe_cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if describe_result.returncode != 0:
            return f"错误: p4 describe 命令执行失败\n{describe_result.stderr}"
        
        describe_output = describe_result.stdout
        formatted_info += f"【CL描述信息】\n{describe_output}\n"
        formatted_info += "=" * 60 + "\n\n"
        
        # 解析文件列表 - 从 p4 describe 输出中提取文件路径
        # 输出格式类似:
        # ... //depot/path/file.go#1 edit
        # ... //depot/path/file2.go#2 add
        files = []
        lines = describe_output.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('... '):
                # 提取文件路径和操作类型
                # 格式: ... //depot/path/file.go#1 edit
                parts = line[4:].split('#')
                if len(parts) >= 2:
                    file_path = parts[0]
                    # 提取版本号和操作类型
                    rest = parts[1].split(' ')
                    revision = rest[0] if rest else ''
                    action = rest[1] if len(rest) > 1 else ''
                    files.append({
                        'path': file_path,
                        'revision': revision,
                        'action': action
                    })
        
        if not files:
            formatted_info += "未找到变更文件\n"
            return formatted_info
        
        formatted_info += f"【变更文件列表】共 {len(files)} 个文件\n"
        for f in files:
            formatted_info += f"  - {f['action']} {f['path']}#{f['revision']}\n"
        formatted_info += "\n" + "=" * 60 + "\n\n"
        
        # 2. 遍历文件列表，使用 p4 diff2 获取每个文件的差异
        formatted_info += "【文件差异详情】\n\n"
        
        for file_info in files:
            file_path = file_info['path']
            action = file_info['action']
            revision = file_info['revision']
            
            # 跳过配置的文件扩展名
            if should_skip_file(file_path):
                formatted_info += f"---- {file_path} (已跳过: 不需要审查的文件类型) ----\n\n"
                continue
            
            formatted_info += f"---- {file_path}#{revision} ({action}) ----\n"
            
            if action == 'delete':
                formatted_info += "  [文件已删除]\n\n"
                continue
            elif action == 'add':
                # 对于新增文件，使用 p4 print 获取文件内容
                print_cmd = ["p4", "print", "-q", f"{file_path}@={changelist_id}"]
                
                print_result = subprocess.run(
                    print_cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                if print_result.returncode == 0:
                    content = print_result.stdout
                    # 检查是否是二进制文件
                    if '\x00' in content or is_binary_content(content):
                        formatted_info += "  [二进制文件]\n\n"
                    else:
                        lines = content.split('\n')
                        formatted_info += f"  [新增文件，共 {len(lines)} 行]\n"
                        # 显示文件内容（限制行数避免输出过长）
                        max_lines = 500
                        if len(lines) > max_lines:
                            formatted_info += f"  (仅显示前 {max_lines} 行)\n"
                            for i, line in enumerate(lines[:max_lines]):
                                formatted_info += f"  + {line}\n"
                            formatted_info += f"  ... 省略 {len(lines) - max_lines} 行 ...\n"
                        else:
                            for line in lines:
                                formatted_info += f"  + {line}\n"
                else:
                    formatted_info += f"  [获取文件内容失败: {print_result.stderr}]\n"
                formatted_info += "\n"
                continue
            
            # 对于编辑的文件，使用 p4 diff2 获取差异
            # p4 diff2 <文件路径> <文件路径>@=<CL号>
            diff2_cmd = ["p4", "diff2", file_path, f"{file_path}@={changelist_id}"]
            
            diff2_result = subprocess.run(
                diff2_cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if diff2_result.returncode == 0 or diff2_result.stdout:
                diff_output = diff2_result.stdout
                if not diff_output.strip():
                    formatted_info += "  [无差异]\n"
                elif '(binary)' in diff_output.lower() or 'binary' in diff_output.lower():
                    formatted_info += "  [二进制文件]\n"
                else:
                    # 解析并格式化差异输出
                    formatted_info += format_diff2_output(diff_output)
            else:
                formatted_info += f"  [获取差异失败: {diff2_result.stderr}]\n"
            
            formatted_info += "\n"
        
        return formatted_info
        
    except Exception as e:
        error_msg = f"获取CL差异时出错: {str(e)}"
        return error_msg


def is_binary_content(content: str) -> bool:
    """检查内容是否为二进制"""
    # 检查是否包含大量非打印字符
    non_printable = sum(1 for c in content[:1000] if ord(c) < 32 and c not in '\n\r\t')
    return non_printable > len(content[:1000]) * 0.1


def should_skip_file(file_path: str) -> bool:
    """检查文件是否应该被跳过"""
    for ext in SKIP_FILE_EXTENSIONS:
        if file_path.endswith(ext):
            return True
    return False


def format_diff2_output(diff_output: str) -> str:
    """格式化 p4 diff2 的输出"""
    formatted = ""
    lines = diff_output.split('\n')
    
    for line in lines:
        if line.startswith('==== '):
            # 文件头信息
            formatted += f"  {line}\n"
        elif line.startswith('>'):
            # 新增的行
            formatted += f"  + {line[1:].strip()}\n"
        elif line.startswith('<'):
            # 删除的行
            formatted += f"  - {line[1:].strip()}\n"
        elif line.startswith('---'):
            # 分隔符
            formatted += f"  {line}\n"
        elif re.match(r'^\d+[acd]\d+', line):
            # 差异位置信息 (如: 10a11, 5c6, 8d9)
            formatted += f"  [{line}]\n"
        elif re.match(r'^\d+,\d+[acd]\d+', line):
            # 差异位置信息 (如: 10,12a15)
            formatted += f"  [{line}]\n"
        elif line.strip():
            formatted += f"  {line}\n"
    
    return formatted


# Swarm相关常量
SWARM_BASE_URL = None  # 默认为None，从配置文件中读取
SWARM_API_URL = None   # 默认为None，从配置文件中读取
SWARM_USERNAME = None
SWARM_PASSWORD = None

# 跳过的文件扩展名列表（默认值）
SKIP_FILE_EXTENSIONS = ['.pb.go', '.cs']

# 从配置文件读取P4配置
def read_p4_config_file(config_file_path):
    try:
        if not os.path.exists(config_file_path):
            print(f"配置文件不存在: {config_file_path}")
            return None
        
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return {
            'swarm_username': config.get('swarm_username'),
            'swarm_password': config.get('swarm_password'),
            'swarm_base_url': config.get('swarm_base_url'),
            'swarm_api_url': config.get('swarm_api_url'),
            'skip_file_extensions': config.get('skip_file_extensions')
        }
    except Exception as e:
        print(f"读取配置文件出错: {str(e)}")
        return None

# 初始化默认配置
def init_default_config():
    global SWARM_USERNAME, SWARM_PASSWORD, SWARM_BASE_URL, SWARM_API_URL, SKIP_FILE_EXTENSIONS
    
    # 从配置文件获取配置
    global config_file_path
    if os.path.exists(config_file_path):
        file_config = read_p4_config_file(config_file_path)
        if file_config:
            SWARM_USERNAME = file_config.get('swarm_username')
            SWARM_PASSWORD = file_config.get('swarm_password')
            SWARM_BASE_URL = file_config.get('swarm_base_url')
            SWARM_API_URL = file_config.get('swarm_api_url')
            # 读取跳过的文件扩展名配置
            skip_extensions = file_config.get('skip_file_extensions')
            if skip_extensions and isinstance(skip_extensions, list):
                SKIP_FILE_EXTENSIONS = skip_extensions
            
            # 检查必要的Swarm配置是否存在
            if not SWARM_BASE_URL:
                print("警告: 未设置Swarm基础URL，请在配置文件中添加swarm_base_url")
            if not SWARM_API_URL:
                print("警告: 未设置Swarm API URL，请在配置文件中添加swarm_api_url")
    else:
        print(f"警告: 配置文件 {config_file_path} 不存在")
        print("请创建配置文件，并包含以下内容:")
        print("""
{
  "swarm_username": "your_swarm_username",
  "swarm_password": "your_swarm_password",
  "swarm_base_url": "https://your_swarm_server",
  "swarm_api_url": "https://your_swarm_server/api/v10"
}
        """)

# 模拟浏览器登录获取cookie
def browser_login(username=None, password=None, base_url=None):
    """
    模拟浏览器登录P4Swarm，获取会话cookie
    
    Args:
        username: Swarm用户名
        password: Swarm密码
        base_url: Swarm基础URL
        
    Returns:
        requests.Session对象，包含登录后的cookie
    """
    # 使用全局配置或传入的参数
    username = username or SWARM_USERNAME
    password = password or SWARM_PASSWORD
    base_url = base_url or SWARM_BASE_URL
    
    if not username or not password:
        print("错误: 未提供Swarm用户名或密码")
        return None
    
    if not base_url:
        print(f"错误: 未提供Swarm基础URL，请在配置文件 {config_file_path} 中添加swarm_base_url")
        return None
    
    print(f"尝试模拟浏览器登录 {base_url}...")
    
    # 创建一个会话对象，用于保持cookie
    session = requests.Session()
    
    # 设置User-Agent头，模拟浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    # 访问登录页面获取CSRF令牌
    try:
        print("访问登录页面...")
        login_url = "{}/login".format(base_url)
        response = session.get(login_url, headers=headers)
        
        if response.status_code != 200:
            print("访问登录页面失败，状态码: {}".format(response.status_code))
            return None
        
        # 解析HTML获取CSRF令牌
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = None
        
        # 查找CSRF令牌，通常在表单的隐藏输入字段中
        csrf_input = soup.find('input', {'name': 'csrf'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
        
        if not csrf_token:
            # 尝试从JavaScript中提取
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'csrf' in script.string:
                    match = re.search(r'csrf["\']?\s*:\s*["\']([^"\']+)["\']', script.string)
                    if match:
                        csrf_token = match.group(1)
                        break
        
        if not csrf_token:
            print("无法找到CSRF令牌")
            # 尝试继续，有些网站可能不需要CSRF令牌
        else:
            print("找到CSRF令牌: {}...".format(csrf_token[:10]))
        
        # 准备登录数据
        login_data = {
            'user': username,
            'password': password,
        }
        
        if csrf_token:
            login_data['csrf'] = csrf_token
        
        # 提交登录表单
        print("提交登录表单...")
        login_response = session.post(login_url, data=login_data, headers=headers, allow_redirects=True)
        
        # 检查登录是否成功
        if login_response.status_code == 200 or login_response.status_code == 302:
            # 检查是否有重定向到登录成功页面
            if 'dashboard' in login_response.url or 'home' in login_response.url:
                print("登录成功！")
            else:
                # 检查页面内容是否有登录成功的迹象
                if 'logout' in login_response.text.lower() or 'sign out' in login_response.text.lower():
                    print("登录成功！")
                else:
                    print("登录可能失败，请检查响应内容")
                    print("响应URL: {}".format(login_response.url))
                    # 打印部分响应内容以便调试
                    print("响应内容片段: {}...".format(login_response.text[:500]))
        else:
            print("登录失败，状态码: {}".format(login_response.status_code))
            return None
        
        # 打印cookie信息
        print("获取到的Cookie:")
        for cookie in session.cookies:
            print("  {}: {}".format(cookie.name, cookie.value))
        
        return session
        
    except Exception as e:
        print("模拟浏览器登录过程中发生错误: {}".format(e))
        return None

# 使用cookie创建API客户端
def create_api_client_with_cookies(session, api_url=None):
    """
    使用cookie创建API客户端
    
    Args:
        session: 包含cookie的会话对象
        api_url: Swarm API URL
        
    Returns:
        requests.Session对象，用于API调用
    """
    api_url = api_url or SWARM_API_URL
    
    if not api_url:
        print(f"错误: 未提供Swarm API URL，请在配置文件 {config_file_path} 中添加swarm_api_url")
        return None
    
    try:
        # 创建一个新的请求会话，复制cookie
        api_session = requests.Session()
        api_session.cookies.update(session.cookies)
        
        # 测试API访问
        print("使用cookie测试API访问...")
        version_url = f"{api_url}/version"
        response = api_session.get(version_url)
        
        if response.status_code == 200:
            print(f"API访问成功！版本信息: {response.text}")
            return api_session
        else:
            print(f"API访问失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"创建API客户端时发生错误: {e}")
        return None

# 获取指定changelist的文件列表
def get_changelist_files(api_session, changelist_id, api_url=None):
    """
    获取指定changelist的文件列表
    
    Args:
        api_session: API会话对象
        changelist_id: 变更列表ID
        api_url: Swarm API URL
        
    Returns:
        包含文件列表的字典
    """
    api_url = api_url or SWARM_API_URL
    
    try:
        print(f"获取changelist {changelist_id}的文件列表...")
        
        # 构建API URL
        files_url = f"{api_url}/reviews/{changelist_id}/files"
        
        # 发送请求
        response = api_session.get(files_url)
        
        if response.status_code == 200:
            # 解析JSON响应
            data = response.json()
            
            # 检查是否有错误
            if data.get('error') is not None:
                print(f"获取文件列表失败，错误: {data.get('error')}")
                return None
            
            # 提取文件列表
            result = data.get('data', {})
            files = result.get('files', [])
            root = result.get('root', '')
            
            print(f"成功获取changelist {changelist_id}的文件列表，共{len(files)}个文件")
            print(f"文件根路径: {root}")
            
            return {
                'root': root,
                'files': files
            }
        else:
            print(f"获取文件列表失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
            
    except Exception as e:
        print(f"获取changelist文件列表时发生错误: {e}")
        return None

# 获取文件差异信息
def get_file_diff(api_session, depot_file, revision, changelist_id, api_url=None):
    try:
        api_url = api_url or SWARM_API_URL
        
        if not api_url:
            print(f"错误: 未提供Swarm API URL，请在配置文件 {config_file_path} 中添加swarm_api_url")
            return None
            
        print("获取文件 {} 在changelist {}中的差异...".format(depot_file, changelist_id))
        
        # 将文件路径编码为URL安全的Base64
        file_path_base64 = base64.urlsafe_b64encode(depot_file.encode('utf-8')).decode('utf-8')
        
        # 构建API URL - 获取当前版本与前一个版本的差异
        # 注意：这里假设文件版本号是从文件路径中提取的，格式如 //depot/path/file.txt#3
        current_rev = revision
        try:
            prev_rev = str(int(current_rev) - 1)
        except ValueError:
            prev_rev = "1"  # 如果无法解析版本号，默认使用版本1
        
        
        # 构建差异URL
        diff_url = "{}/files/{}/diff?from=%23{}&to=%40%3D{}".format(
            api_url, file_path_base64, current_rev, changelist_id
        )
        
        # 发送请求
        response = api_session.get(diff_url)
        
        if response.status_code == 200:
            # 解析JSON响应
            data = response.json()
            
            # 检查是否有错误
            if data.get('error') is not None:
                print("获取文件差异失败，错误: {}".format(data.get('error')))
                return None
            
            # 提取差异信息
            diff_data = data.get('data', {})
            
            return diff_data
        else:
            print("获取文件差异失败，状态码: {}".format(response.status_code))
            print("响应内容: {}".format(response.text))
            return None
            
    except Exception as e:
        print("获取文件差异时发生错误: {}".format(e))
        return None

# 获取文件差异信息
def get_file_diff_with_previous_version(api_session, depot_file, revision, changelist_id, api_url=None):
    try:
        api_url = api_url or SWARM_API_URL
        
        if not api_url:
            print(f"错误: 未提供Swarm API URL，请在配置文件 {config_file_path} 中添加swarm_api_url")
            return None
            
        print("获取文件 {} 在changelist {}中的差异...".format(depot_file, changelist_id))
        
        # 将文件路径编码为URL安全的Base64
        file_path_base64 = base64.urlsafe_b64encode(depot_file.encode('utf-8')).decode('utf-8')
        
        # 构建API URL - 获取当前版本与前一个版本的差异
        # 注意：这里假设文件版本号是从文件路径中提取的，格式如 //depot/path/file.txt#3
        current_rev = revision
        try:
            prev_rev = str(int(current_rev) - 1)
        except ValueError:
            prev_rev = "1"  # 如果无法解析版本号，默认使用版本1
        
        
        # 构建差异URL
        diff_url = "{}/files/{}/diff?from=%23{}&to=%23{}".format(
            api_url, file_path_base64, prev_rev, current_rev
        )
        
        # 发送请求
        response = api_session.get(diff_url)
        
        if response.status_code == 200:
            # 解析JSON响应
            data = response.json()
            
            # 检查是否有错误
            if data.get('error') is not None:
                print("获取文件差异失败，错误: {}".format(data.get('error')))
                return None
            
            # 提取差异信息
            diff_data = data.get('data', {})
            
            return diff_data
        else:
            print("获取文件差异失败，状态码: {}".format(response.status_code))
            print("响应内容: {}".format(response.text))
            return None
            
    except Exception as e:
        print("获取文件差异时发生错误: {}".format(e))
        return None


# 获取文件完整内容
def get_file_complete_content(api_session, depot_file, changelist_id, api_url=None):
    try:
        api_url = api_url or SWARM_BASE_URL
        
        if not api_url:
            print(f"错误: 未提供Swarm基础URL，请在配置文件 {config_file_path} 中添加swarm_base_url")
            return None
            
        print(f"获取文件 {depot_file} 的完整内容...")
        
        # 构建API URL
        complete_url = "{}/view/{}?v=%40%3D{}".format(
            api_url, depot_file, changelist_id
        )

        # 发送请求
        response = api_session.get(complete_url)
        
        if response.status_code == 200:
            # 解析text/plain响应
            data = response.text
            # 获取文件内容的行数
            diffs = data.split('\n')
            line_count = len(diffs)
            print(f"文件 {depot_file} 共有 {line_count} 行内容")
            
            return {
                'is_same': False,
                'is_binary': False,
                'is_new': True,
                'summary': {
                    'adds': line_count
                },
                'diffs': diffs
            }
        else:
            return f"获取文件完整内容失败，URL: {complete_url} 状态码: {response.status_code}"
    except Exception as e:
        return f"获取文件完整内容时发生错误: URL: {complete_url} 错误信息: {e}"

# 分析文件差异
def analyze_file_changes(diff_data):
    """分析文件差异数据，提取有用的信息"""
    if not diff_data:
        return {
            'is_same': True,
            'is_binary': False,
            'is_new': False,
            'summary': {
                'adds': 0,
                'deletes': 0,
                'updates': 0
            },
            'diffs': []
        }
    
    # 提取差异摘要
    summary = diff_data.get('summary', {})
    is_same = diff_data.get('isSame', False)
    is_binary = diff_data.get('isBinary', False)
    is_new = diff_data.get('isNew', False)
    diffs = diff_data.get('diffs', [])
    
    return {
        'is_same': is_same,
        'is_binary': is_binary,
        'is_new': is_new,
        'summary': summary,
        'diffs': diffs
    }

# 分析差异数据
def analysis_diff_data(analysis, file_path) -> str:
    """
    分析文件差异
    """
    formatted_info = ""
    formatted_info += "文件: {}\n".format(file_path)
                
    if analysis['is_binary']:
        formatted_info += "  [二进制文件]\n"
    elif analysis['is_same']:
        formatted_info += "  [文件内容相同]\n"
    elif analysis['is_new']:
            # 写入摘要信息
        summary = analysis['summary']
        formatted_info += "  添加行数: {}\n".format(summary.get('adds', 0))
        formatted_info += "  删除行数: {}\n".format(summary.get('deletes', 0))
        formatted_info += "  修改行数: {}\n".format(summary.get('updates', 0))
        
        # 写入差异详情
        if analysis['diffs']:
            formatted_info += "\n  差异详情:\n"
            for diff in analysis['diffs']:
                formatted_info += "    + {}\n".format(diff)
    else:
        # 写入摘要信息
        summary = analysis['summary']
        formatted_info += "  添加行数: {}\n".format(summary.get('adds', 0))
        formatted_info += "  删除行数: {}\n".format(summary.get('deletes', 0))
        formatted_info += "  修改行数: {}\n".format(summary.get('updates', 0))
        
        # 写入差异详情
        if analysis['diffs']:
            formatted_info += "\n  差异详情:\n"
            for diff in analysis['diffs']:
                formatted_info += "    {}\n".format(diff)
    
    formatted_info += "\n"
    return formatted_info

async def main():
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置配置文件路径
    global config_file_path
    config_file_path = args.p4config
    print(f"使用配置文件: {config_file_path}")
    
    # 初始化默认配置
    init_default_config()
    
    # 登录Swarm
    session = browser_login(SWARM_USERNAME, SWARM_PASSWORD, SWARM_BASE_URL)
    if not session:
        return "错误: 登录Swarm失败"
    
    # 创建API客户端
    global api_session
    api_session = create_api_client_with_cookies(session)
    if not api_session:
        return "错误: 创建API客户端失败"
    

    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
# MCP Perforce 服务器

Perforce的模型上下文协议(MCP)服务器实现

## 功能概述

MCP Perforce服务器提供以下功能：

1. **get-changelist-files-catalog** - 通过Swarm API获取reviews目录中的文件列表
2. **get-file-details** - 通过Swarm API获取目录中每个变更文件的详细内容
3. **get-changelist-diff-native** - 使用P4原生命令获取CL中的变更文件列表和文件差异
   - 使用 `p4 describe -s -S <CL号>` 获取变更文件列表
   - 使用 `p4 diff2 <文件路径> <文件路径>@=<CL号>` 获取每个文件的差异

## 配置说明

cursor MCP 配置说明
```json
{
    "mcpServers": {
      "code review": {
          "command": "uvx",
          "args": [
              "mcp-perforce",
              "--p4config",
              "./path/to/your/p4config.json"
          ]
      }
  }      
}  
```

p4config.json说明

```json
{
  "swarm_username": "your_swarm_username",
  "swarm_password": "your_swarm_password",
  "swarm_base_url": "https://your_swarm_server",
  "swarm_api_url": "https://your_swarm_server/api/v10",
  "skip_file_extensions": [".pb.go", ".cs"]
}
```

### 配置项说明

| 配置项 | 必填 | 说明 |
|--------|------|------|
| swarm_username | 是 | Swarm登录用户名 |
| swarm_password | 是 | Swarm登录密码 |
| swarm_base_url | 是 | Swarm服务器基础URL |
| swarm_api_url | 是 | Swarm API URL |
| skip_file_extensions | 否 | 需要跳过的文件扩展名列表，默认为 `[".pb.go", ".cs"]` |

## 使用说明

cursor agent 模式中输入
```
帮我review一下3280706
```
cursor将自动使用mcp-perforce拉取reviews中的文件列表进行review。

## 更新记录

* 0.2.6 - 新增 `skip_file_extensions` 配置项，支持自定义跳过的文件扩展名
* 0.2.5 - 新增 `get-changelist-diff-native` 工具，支持使用P4原生命令获取CL差异
* 0.2.4 - 修复代码提交后，无法获取reviews中的差异信息的BUG
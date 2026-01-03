"""
FastMCP quickstart example.

Run from the repository root:
    uv run examples/snippets/servers/fastmcp_quickstart.py
"""

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")


@mcp.tool()
def send_wecom_message(
    webhook_url: str,
    content: str,
    msg_type: str = "markdown_v2"
) -> dict:
    """
    发送消息到企业微信群机器人。
    
    通过企业微信 Webhook 发送消息，支持 markdown_v2 和 text 两种格式。
    如果 markdown_v2 格式发送失败，建议切换为 text 格式重试。
    
    Args:
        webhook_url: 企业微信机器人的 Webhook 地址
                     格式: https://...
                     格式: http://...
        content: 要发送的消息内容
                 - markdown_v2 格式: 支持 Markdown 语法，如标题、列表、加粗等
                 - text 格式: 纯文本内容
        
        msg_type: 消息类型，可选值:
                  - "markdown_v2": Markdown 格式（默认），支持丰富的排版
                  - "text": 纯文本格式，兼容性更好
    
    Returns:
        dict: 企业微信 API 返回结果
              - errcode: 0 表示成功，非 0 表示失败
              - errmsg: 错误信息描述
              
    Examples:
        # 发送 Markdown 消息
        send_wecom_message(
            webhook_url="https://...",
            content="## 标题\\n- 列表项1\\n- 列表项2",
            msg_type="markdown_v2"
        )
        
        # 发送纯文本消息
        send_wecom_message(
            webhook_url="https://...",
            content="这是一条纯文本消息",
            msg_type="text"
        )
    
    Notes:
        - 如果 markdown_v2 发送失败（errcode 非 0），建议改用 text 格式重试
        - Webhook URL 中的 key 是机器人的唯一标识，请妥善保管
    """
    import urllib.request
    import json
    
    # 构建请求数据
    if msg_type == "markdown_v2":
        data = {
            "msgtype": "markdown_v2",
            "markdown_v2": {
                "content": content
            }
        }
    else:
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
    
    # 发送请求
    json_data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=json_data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Run with streamable HTTP transport
def main() -> None:
    mcp.run(transport="stdio")

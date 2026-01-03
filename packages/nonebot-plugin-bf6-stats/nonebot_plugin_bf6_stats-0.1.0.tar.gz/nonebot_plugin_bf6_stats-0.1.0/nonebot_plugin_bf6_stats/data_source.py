import httpx
import nonebot
from nonebot.log import logger
from .models import BF6Stats

driver = nonebot.get_driver()

# 全局客户端
_client: httpx.AsyncClient | None = None

@driver.on_startup
async def init_client():
    global _client
    logger.info("正在初始化 Gametools API 客户端...")
    # 设置长一点的超时，防止API响应慢
    _client = httpx.AsyncClient(timeout=20.0, follow_redirects=True)

@driver.on_shutdown
async def close_client():
    global _client
    if _client:
        await _client.aclose()
        _client = None

async def get_client() -> httpx.AsyncClient:
    if _client is None:
        raise RuntimeError("HTTP Client 未初始化")
    return _client

async def get_bf6_stats(player_name: str) -> BF6Stats:
    """
    访问 Gametools API 获取真实战绩
    """
    client = await get_client()
    
    # API 地址 
    url = "https://api.gametools.network/bf6/stats/"
    
    params = {
        "format": "json",      # 强制返回 JSON 格式
        "name": player_name,   # 玩家 ID
        "platform": "pc",      # 平台，目前默认写死 PC，后续可扩展
        "limit": 1             # 限制返回条数
    }

    logger.info(f"正在查询: {url} 参数: {params}")

    try:
        resp = await client.get(url, params=params)
        
        # API 错误处理
        if resp.status_code == 404:
            raise ValueError("UserNotFound")
        elif resp.status_code != 200:
            logger.error(f"API Error: {resp.status_code} - {resp.text}")
            raise RuntimeError(f"API Error {resp.status_code}")

        data = resp.json()
        
        # 这里的 data 就是 API 返回的大字典，直接解包给 Pydantic 模型
        # 模型会自动根据 alias 匹配字段
        return BF6Stats(**data)

    except httpx.RequestError as e:
        logger.error(f"网络请求失败: {e}")
        raise RuntimeError("NetworkError")
    except Exception as e:
        logger.error(f"数据解析失败: {e}")
        raise e
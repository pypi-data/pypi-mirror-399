"""
wtx_weather_mcp mcp for query weather info by geovis-wtx
"""
import requests
from mcp.server.fastmcp import FastMCP
import os

token = os.getenv("WTX_OPEN_API_TOKEN")

if not token:
    raise ValueError("未配置请求秘钥 WTX_OPEN_API_TOKEN! 参考地址: https://open.geovisearth.com/support/document?docId=222&detail=client")

# Create an MCP server
mcp = FastMCP("wtx_weather_mcp",
              json_response=True,
              instructions="wtx_weather_mcp mcp for query weather info by geovis-wtx")

# 全国天气实况（30要素）
@mcp.tool()
def query_real_weather_elem30(area_code: str) -> dict:
    """
查询全国市、区县的天气实况（30要素）: 可获取中国3300+市区县的分钟级天气实况，包含天气现象、实时温度、体感温度、风力风向、相对湿度、海平面气压、降水量（多时间维度统计）、能见度、露点温度、云量、太阳辐射等诸多要素。
调取方式：区域/任意经纬度
数据要素：天气现象、温度、体感温度、小时最高温、小时高温出现时间、24小时变温、24小时变温描述、相对湿度、露点温度、风向角度数值、风向描述、风速、风力、阵风、阵风级别、紫外线级别、紫外线描述、能见度、云量、地面气压、过去24小时变压、过去24小时变压描述、过去3小时变压、过去3小时变压描述、过去1小时降水、过去3小时累计降水、过去6小时累计降水、过去12小时累计降水、过去24小时累计降水、太阳短波辐射
:param area_code: WTX区域代码
:return: 天气信息 JSON 字典
    """
    url = "https://api.open.geovisearth.com/v2/cn/area/professional"
    params = {"token": token, "location": area_code}

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()  # 非 200 会抛异常

    return resp.json()

def main() -> None:
    # mcp.run(transport="streamable-http")
    mcp.run(transport="stdio")

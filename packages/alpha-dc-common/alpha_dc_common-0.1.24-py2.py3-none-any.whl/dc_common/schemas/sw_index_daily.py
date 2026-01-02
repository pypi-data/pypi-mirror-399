"""
申万行业指数日线数据Pydantic模型
"""
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field


class SWIndexDaily(BaseModel):
    """申万行业指数日线数据模型"""

    id: Optional[int] = Field(None, description="主键ID")
    index_code: str = Field(..., description="行业代码")
    trade_date: date = Field(..., description="交易日期")
    name: Optional[str] = Field(None, description="行业名称")
    open: Optional[Decimal] = Field(None, description="开盘点位")
    high: Optional[Decimal] = Field(None, description="最高点位")
    low: Optional[Decimal] = Field(None, description="最低点位")
    close: Optional[Decimal] = Field(None, description="收盘点位")
    change: Optional[Decimal] = Field(None, description="涨跌点位")
    pct_change: Optional[Decimal] = Field(None, description="涨跌幅(%)")
    vol: Optional[int] = Field(None, description="成交量(股)")
    amount: Optional[int] = Field(None, description="成交额(元)")
    pe: Optional[Decimal] = Field(None, description="市盈率")
    pb: Optional[Decimal] = Field(None, description="市净率")
    float_mv: Optional[int] = Field(None, description="流通市值(元)")
    total_mv: Optional[int] = Field(None, description="总市值(元)")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
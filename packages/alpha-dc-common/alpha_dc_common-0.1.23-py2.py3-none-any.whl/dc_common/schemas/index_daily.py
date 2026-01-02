"""
指数日线数据Pydantic模型
"""
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field


class IndexDaily(BaseModel):
    """指数日线数据模型"""

    id: Optional[int] = Field(None, description="主键ID")
    index_code: str = Field(..., description="指数代码")
    trade_date: date = Field(..., description="交易日")
    open: Optional[Decimal] = Field(None, description="开盘点位")
    high: Optional[Decimal] = Field(None, description="最高点位")
    low: Optional[Decimal] = Field(None, description="最低点位")
    close: Optional[Decimal] = Field(None, description="收盘点位")
    pre_close: Optional[Decimal] = Field(None, description="昨日收盘点")
    price_change: Optional[Decimal] = Field(None, description="涨跌点")
    pct_chg: Optional[Decimal] = Field(None, description="涨跌幅(%)")
    vol: Optional[Decimal] = Field(None, description="成交量(手)")
    amount: Optional[Decimal] = Field(None, description="成交额(元)")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
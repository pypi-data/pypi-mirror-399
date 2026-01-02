"""
指数基本信息相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date

class IndexBasicBase(BaseModel):
    index_code: str = Field(..., description="指数代码（小数点前部分）")
    index_full_code: str = Field(..., description="完整TS代码")
    name: Optional[str] = Field(None, description="简称")
    market: Optional[str] = Field(None, description="市场")
    publisher: Optional[str] = Field(None, description="发布方")
    base_date: Optional[date] = Field(None, description="基期")
    base_point: Optional[float] = Field(None, description="基点")
    list_date: Optional[date] = Field(None, description="发布日期")
    enable_margin_analysis: Optional[bool] = Field(False, description="是否启用融资融券分析")
    enable_company_download: Optional[bool] = Field(False, description="是否下载成分股公司列表")

class IndexBasic(IndexBasicBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
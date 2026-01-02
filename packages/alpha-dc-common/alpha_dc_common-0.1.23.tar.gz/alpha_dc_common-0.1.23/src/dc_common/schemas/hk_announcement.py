"""
港股公告数据模式
"""
from datetime import datetime
from typing import Optional
from pydantic import Field, BaseModel


class HKAnnouncement(BaseModel):
    """港股公告数据模式"""

    id: Optional[int] = Field(None, description="主键ID")
    announcement_id: str = Field(..., description="公告唯一标识")
    stock_code: str = Field(..., description="股票代码（逗号分隔）")
    ric_code: str = Field(..., description="RIC代码（逗号分隔）")
    sec_name: Optional[str] = Field(None, description="股票名称（逗号分隔）")
    announcement_title: str = Field(..., description="公告标题")
    announcement_time: datetime = Field(..., description="公告发布时间")
    announcement_type: Optional[str] = Field(None, description="公告类型")
    org_id: Optional[str] = Field(None, description="机构ID")
    adjunct_url: str = Field(..., description="附件URL")
    adjunct_size: Optional[int] = Field(None, description="附件大小（字节）")
    adjunct_type: Optional[str] = Field(None, description="附件类型")
    market_sector: str = Field(..., description="市场板块（HKZB主板/HKCY创业板）")
    is_external_pdf: Optional[bool] = Field(False, description="是否外部PDF")
    critical_announcement: Optional[int] = Field(0, description="是否重要公告")
    created_at: Optional[datetime] = Field(None, description="记录创建时间")
    updated_at: Optional[datetime] = Field(None, description="记录更新时间")

    class Config:
        from_attributes = True
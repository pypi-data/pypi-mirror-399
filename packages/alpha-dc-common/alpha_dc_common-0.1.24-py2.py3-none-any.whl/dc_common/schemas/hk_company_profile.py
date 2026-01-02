"""
港股公司基本信息相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date

class HKCompanyProfileBase(BaseModel):
    stock_code: str = Field(..., description="股票代码")
    ric_code: str = Field(..., description="RIC代码")
    security_name_abbr: str = Field(..., description="股票名称简称")

    # 证券基本信息
    security_type: Optional[str] = Field(None, description="证券类型")
    listing_date: Optional[date] = Field(None, description="上市日期")
    isin_code: Optional[str] = Field(None, description="ISIN代码")
    board: Optional[str] = Field(None, description="板块")
    trade_unit: Optional[int] = Field(None, description="交易单位")
    trade_market: Optional[str] = Field(None, description="交易市场")
    ganggutongbiaodishen: Optional[str] = Field(None, description="港股通深")
    ganggutongbiaodihu: Optional[str] = Field(None, description="港股通沪")
    par_value: Optional[str] = Field(None, description="面值")
    issue_price: Optional[float] = Field(None, description="发行价格")
    issue_num: Optional[int] = Field(None, description="发行数量")
    year_settle_day: Optional[str] = Field(None, description="年结算日")

    # 公司概况信息
    org_name: Optional[str] = Field(None, description="公司名称")
    org_en_abbr: Optional[str] = Field(None, description="公司英文简称")
    belong_industry: Optional[str] = Field(None, description="所属行业")
    found_date: Optional[str] = Field(None, description="成立时间")
    chairman: Optional[str] = Field(None, description="董事长")
    secretary: Optional[str] = Field(None, description="董事会秘书")
    account_firm: Optional[str] = Field(None, description="会计师事务所")
    reg_address: Optional[str] = Field(None, description="注册地址")
    address: Optional[str] = Field(None, description="办公地址")
    emp_num: Optional[int] = Field(None, description="员工人数")
    org_tel: Optional[str] = Field(None, description="公司电话")
    org_fax: Optional[str] = Field(None, description="公司传真")
    org_email: Optional[str] = Field(None, description="公司邮箱")
    org_web: Optional[str] = Field(None, description="公司网站")
    org_profile: Optional[str] = Field(None, description="公司简介")
    reg_place: Optional[str] = Field(None, description="注册地点")

class HKCompanyProfile(HKCompanyProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
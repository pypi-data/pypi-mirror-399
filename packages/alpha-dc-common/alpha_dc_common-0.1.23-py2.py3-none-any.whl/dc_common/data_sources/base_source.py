"""
数据源基类定义
"""
from abc import ABC, abstractmethod
from datetime import datetime, time
from typing import Dict, Any, Optional
import pandas as pd
import logging
from pathlib import Path
from enum import Enum


class DataSourceStatus(Enum):
    """数据源状态"""
    PENDING = "pending"        # 等待中
    READY = "ready"           # 数据就绪
    UPDATING = "updating"     # 更新中
    FAILED = "failed"         # 更新失败
    NOT_NEEDED = "not_needed" # 该日不需要更新


class BaseDataSource(ABC):
    """数据源基类

    每个数据源有独立的调度策略和更新时间
    """

    def __init__(self, data_dir: str, logger: Optional[logging.Logger] = None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)

    @property
    @abstractmethod
    def source_name(self) -> str:
        """数据源唯一标识"""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """显示名称"""
        pass

    @property
    @abstractmethod
    def update_time(self) -> str:
        """
        期望更新时间
        例如: "17:00", "09:30"
        """
        pass

    @property
    def update_delay_days(self) -> int:
        """
        更新延迟天数
        0 = 当天更新
        1 = 次日更新
        """
        return 0

    @property
    def priority(self) -> int:
        """
        优先级（数字越小越优先）
        基础数据优先级高，衍生数据优先级低
        """
        return 100

    @abstractmethod
    def fetch_data(self, trade_date: str) -> pd.DataFrame:
        """
        获取数据

        Args:
            trade_date: 交易日期 (YYYYMMDD)

        Returns:
            数据 DataFrame
        """
        pass

    @abstractmethod
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        验证数据质量

        Returns:
            True=数据有效, False=数据无效
        """
        pass

    def is_ready(self, trade_date: str) -> DataSourceStatus:
        """
        检查数据是否就绪

        Args:
            trade_date: 交易日期

        Returns:
            数据源状态
        """
        # 1. 检查本地是否已有数据
        if self._has_local_data(trade_date):
            return DataSourceStatus.READY

        # 2. 检查是否到了更新时间
        if not self._is_update_time():
            return DataSourceStatus.PENDING

        return DataSourceStatus.READY

    def update(self, trade_date: str) -> Dict[str, Any]:
        """
        更新数据

        Args:
            trade_date: 交易日期

        Returns:
            更新结果字典
        """
        result = {
            'source': self.source_name,
            'trade_date': trade_date,
            'status': 'unknown',
            'rows': 0,
            'message': ''
        }

        try:
            self.logger.info(f"🔄 开始更新 {self.display_name}: {trade_date}")

            # 1. 获取数据
            df = self.fetch_data(trade_date)

            # 2. 验证数据
            if not self.validate_data(df):
                result['status'] = 'failed'
                result['message'] = '数据验证失败'
                return result

            # 3. 保存数据
            self._save_data(df, trade_date)

            result['status'] = 'success'
            result['rows'] = len(df)
            result['message'] = f'成功更新 {len(df)} 条数据'

            self.logger.info(f"✅ {self.display_name} 更新完成: {len(df)} 条")

        except Exception as e:
            result['status'] = 'failed'
            result['message'] = str(e)
            self.logger.error(f"❌ {self.display_name} 更新失败: {e}")

        return result

    def _is_update_time(self) -> bool:
        """检查是否到了更新时间"""
        try:
            hour, minute = map(int, self.update_time.split(':'))
            target_time = time(hour, minute)
            now = datetime.now().time()
            return now >= target_time
        except:
            return True

    def _has_local_data(self, trade_date: str) -> bool:
        """检查本地是否已有数据（子类覆盖）"""
        return False

    def _save_data(self, df: pd.DataFrame, trade_date: str):
        """保存数据（子类实现）"""
        pass

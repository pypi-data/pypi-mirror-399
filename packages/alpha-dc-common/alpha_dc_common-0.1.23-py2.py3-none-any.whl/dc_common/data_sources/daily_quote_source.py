"""
日线行情数据源
"""
import os
import pandas as pd
from pathlib import Path
from typing import Optional
import logging

from .base_source import BaseDataSource, DataSourceStatus


class DailyQuoteSource(BaseDataSource):
    """日线行情数据源

    从 Tushare 获取日线行情数据
    更新时间：每天 17:00
    """

    def __init__(
        self,
        data_dir: str,
        tushare_token: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(data_dir, logger)

        self.token = tushare_token or os.getenv('TUSHARE_TOKEN')
        if not self.token:
            raise ValueError("Tushare token 未配置，请设置 TUSHARE_TOKEN 环境变量")

        # 缓存文件直接存储在 data_dir 下（不再添加 raw 子目录）
        self.cache_file = self.data_dir / 'daily_quotes.parquet'
        self.raw_cache_file = self.data_dir / 'daily_quotes_raw.parquet'

        # 延迟初始化 Tushare（避免导入时立即连接）
        self._pro = None

    @property
    def pro(self):
        """延迟初始化 Tushare Pro API"""
        if self._pro is None:
            import tushare as ts
            ts.set_token(self.token)
            self._pro = ts.pro_api()
        return self._pro

    @property
    def source_name(self) -> str:
        return "daily_quotes"

    @property
    def display_name(self) -> str:
        return "日线行情"

    @property
    def update_time(self) -> str:
        return "17:00"

    @property
    def update_delay_days(self) -> int:
        return 0

    @property
    def priority(self) -> int:
        return 10

    def fetch_data(self, trade_date: str) -> pd.DataFrame:
        """从 Tushare 获取日线数据"""
        self.logger.info(f"从 Tushare 获取 {trade_date} 的日线数据...")

        df = self.pro.daily(
            trade_date=trade_date
        )

        if df.empty:
            self.logger.warning(f"{trade_date} 无数据（可能是非交易日）")
        else:
            self.logger.info(f"获取到 {len(df)} 条数据")

        return df

    def validate_data(self, df: pd.DataFrame) -> bool:
        """验证数据质量"""
        if df.empty:
            return True  # 空数据也是有效的（可能是非交易日）

        required_fields = ['ts_code', 'trade_date', 'close']
        return all(field in df.columns for field in required_fields)

    def _has_local_data(self, trade_date: str) -> bool:
        """检查本地是否已有数据"""
        if not self.raw_cache_file.exists():
            return False

        try:
            df = pd.read_parquet(self.raw_cache_file)
            return trade_date in df['trade_date'].values
        except Exception as e:
            self.logger.warning(f"检查本地数据失败: {e}")
            return False

    def _save_data(self, df: pd.DataFrame, trade_date: str):
        """保存数据（追加模式）"""
        # 确保目录存在
        self.raw_cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        # 保存原始长格式数据
        if self.raw_cache_file.exists():
            existing_df = pd.read_parquet(self.raw_cache_file)

            # 移除旧的同日期数据（如果有）
            existing_df = existing_df[existing_df['trade_date'] != trade_date]

            # 合并数据
            combined_df = pd.concat([existing_df, df], ignore_index=True)

            # 去重（基于 trade_date 和 ts_code，保留后出现的）
            combined_df = combined_df.drop_duplicates(
                subset=['trade_date', 'ts_code'],
                keep='last'
            )
        else:
            combined_df = df

        combined_df.to_parquet(self.raw_cache_file, compression='snappy')
        self.logger.info(f"原始数据已保存: {self.raw_cache_file}")

        # 转换并保存宽表格式（用于因子计算）
        self._save_wide_format(combined_df)

    def _save_wide_format(self, df: pd.DataFrame):
        """转换为宽表格式并保存（增量追加）"""
        if df.empty:
            return

        # 排序
        df = df.sort_values(['trade_date', 'ts_code'])

        # 如果文件已存在，进行增量追加
        if self.cache_file.exists():
            try:
                # 读取已有数据
                existing_df = pd.read_parquet(self.cache_file)

                # 移除与新数据重复的日期
                existing_dates = existing_df['trade_date'].unique()
                new_dates = df['trade_date'].unique()

                # 只保留新数据中没有的旧日期
                dates_to_keep = set(existing_dates) - set(new_dates)
                if dates_to_keep:
                    existing_df = existing_df[existing_df['trade_date'].isin(dates_to_keep)]
                else:
                    existing_df = pd.DataFrame()

                # 合并数据
                if not existing_df.empty:
                    combined_df = pd.concat([existing_df, df], ignore_index=True)
                else:
                    combined_df = df

                # 去重（基于 trade_date 和 ts_code，保留后出现的）
                combined_df = combined_df.drop_duplicates(
                    subset=['trade_date', 'ts_code'],
                    keep='last'
                )

                # 排序
                combined_df = combined_df.sort_values(['trade_date', 'ts_code'])

                # 保存
                combined_df.to_parquet(self.cache_file, compression='snappy', index=False)

                old_len = len(existing_df) if dates_to_keep else 0
                new_len = len(combined_df)
                added_rows = new_len - old_len

                self.logger.info(
                    f"宽表数据已增量更新: {self.cache_file} "
                    f"(原有: {old_len}, 新增: {added_rows}, 总计: {new_len})"
                )
            except Exception as e:
                self.logger.warning(f"增量更新失败: {e}，执行覆盖保存")
                df.to_parquet(self.cache_file, compression='snappy', index=False)
                self.logger.info(f"宽表数据已保存: {self.cache_file}")
        else:
            # 首次保存（先去重）
            df = df.drop_duplicates(subset=['trade_date', 'ts_code'], keep='last')
            df.to_parquet(self.cache_file, compression='snappy', index=False)
            self.logger.info(f"宽表数据已保存: {self.cache_file}")

        self.logger.info(f"数据范围: {df['trade_date'].min()} ~ {df['trade_date'].max()}")
        self.logger.info(f"股票数量: {df['ts_code'].nunique()}")

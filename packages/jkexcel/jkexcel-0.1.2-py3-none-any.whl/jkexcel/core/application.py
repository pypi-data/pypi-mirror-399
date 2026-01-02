import pythoncom
import psutil
import time
from typing import Optional, List, Dict, Any
import logging

from jkexcel.core.excel_driver import ExcelApplicationService
from jkexcel.core.workbook import Workbook
from jkexcel.core.workbooks import Workbooks
from jkexcel.models.config import ExcelConfig
from jkexcel.models.exceptions import ExcelNotRunningError, ExcelCOMError

logger = logging.getLogger(__name__)


class ExcelApp:
    """Excel 应用程序封装类"""

    _instance = None
    _instances = {}  # 多实例管理

    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if kwargs.get('new_instance', False):
            instance_id = time.time()
            instance = super().__new__(cls)
            cls._instances[instance_id] = instance
            return instance
        elif cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config: ExcelConfig = None, new_instance: bool = False):
        """
        初始化 ExcelApp
        Args:
            config: Excel 配置
            new_instance: 是否创建新实例
        """
        if not hasattr(self, '_initialized') or new_instance:
            self._config = config or ExcelConfig()
            self._excel = None
            self._workbooks = None
            self._initialized = False
            self._pid = None

    def __enter__(self):
        """上下文管理器进入"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.quit(force=True)
        return False

    def __repr__(self) -> str:
        status = "运行中" if self.is_running else "已停止"
        return f"<ExcelApp {status} PID={self._pid}>"

    def _cleanup(self):
        """清理资源"""
        if self.is_running:
            try:
                self.quit(force=True)
            except:
                pass

    def start(self, new_app: bool = True, visible: bool = None,
              display_alerts: bool = None,
              screen_updating: bool = None) -> 'ExcelApp':
        """
        启动 Excel

        Args:
            new_app: 是否新建app/workbooks false则附加到已有app
            visible: 是否可见
            display_alerts: 是否显示警报
            screen_updating: 是否更新屏幕

        Returns:
            self
        """
        try:
            pythoncom.CoInitialize()
            # 创建 Excel 实例
            if new_app:
                self._excel = ExcelApplicationService.create_application(excel_type=self._config.driver,
                                                                         throw_exception=True)
            else:
                self._excel = ExcelApplicationService.attach_to_running_application(excel_type=self._config.driver,
                                                                                    throw_exception=True)
            self._pid = self._get_process_id()

            # 应用配置
            if visible is not None:
                self._excel.Visible = visible
            else:
                self._excel.Visible = self._config.visible

            if display_alerts is not None:
                self._excel.DisplayAlerts = display_alerts
            else:
                self._excel.DisplayAlerts = self._config.display_alerts

            if screen_updating is not None:
                self._excel.ScreenUpdating = screen_updating
            else:
                self._excel.ScreenUpdating = self._config.screen_updating

            self._excel.EnableEvents = self._config.enable_events

            # 初始化 Workbooks
            self._workbooks = Workbooks(self._excel.Workbooks, self)
            self._initialized = True

            logger.info(f"Excel 启动成功 (PID: {self._pid})")
            return self

        except Exception as e:
            self._initialized = False
            raise ExcelNotRunningError(f"启动 Excel 失败: {e}")

    def _get_process_id(self) -> Optional[int]:
        """获取进程 ID"""
        try:
            return self._excel.Hwnd
        except:
            # 通过进程名查找
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'EXCEL.EXE' in proc.info['name'].upper():
                    return proc.info['pid']
            return None

    @property
    def is_running(self) -> bool:
        """Excel 是否在运行"""
        if not self._excel or not self._initialized:
            return False

        try:
            # 尝试访问属性来检查是否存活
            _ = self._excel.Version
            return True
        except:
            return False

    @property
    def version(self) -> str:
        """获取 Excel 版本"""
        if not self.is_running:
            raise ExcelNotRunningError("Excel 未运行")

        try:
            return self._excel.Version
        except Exception as e:
            raise ExcelCOMError(f"获取版本失败: {e}")

    @property
    def com_object(self):
        """获取底层 COM 对象"""
        if not self.is_running:
            raise ExcelNotRunningError("Excel 未运行")
        return self._excel

    @property
    def count(self):
        """获取工作簿数量"""
        return self._workbooks.count

    @property
    def workbooks(self) -> Workbooks:
        """获取工作簿集合"""
        if not self.is_running:
            raise ExcelNotRunningError("Excel 未运行")
        return self._workbooks

    @property
    def active_workbook(self) -> Optional[Workbook]:
        """获取活动工作簿"""
        if not self.is_running:
            raise ExcelNotRunningError("Excel 未运行")

        try:
            com_wb = self._excel.ActiveWorkbook
            if com_wb:
                return Workbook(com_wb, self)
            return None
        except Exception as e:
            raise ExcelCOMError(f"获取活动工作簿失败: {e}")

    @property
    def active_sheet(self):
        """获取活动工作表（通过活动工作簿）"""
        wb = self.active_workbook
        if wb:
            return wb.get_active_sheet()
        return None

    def calculate(self):
        """强制计算所有打开的工作簿"""
        if not self.is_running:
            raise ExcelNotRunningError("Excel 未运行")

        try:
            self._excel.Calculate()
        except Exception as e:
            raise ExcelCOMError(f"计算失败: {e}")

    def wait(self, seconds: float):
        """
        等待指定时间

        Args:
            seconds: 等待秒数
        """
        time.sleep(seconds)

    def quit(self, force: bool = False):
        """
        退出 Excel

        Args:
            force: 是否强制退出（关闭所有工作簿）
        """
        if not self._excel:
            return

        try:
            if force:
                # 关闭所有工作簿
                for wb in self.workbooks:
                    try:
                        wb.close(save_changes=False)
                    except:
                        pass

            self._excel.Quit()
            logger.info("Excel 已退出")

        except Exception as e:
            logger.error(f"退出 Excel 失败: {e}")

        finally:
            self._excel = None
            self._workbooks = None
            self._initialized = False
            self._pid = None

            # 释放 COM
            try:
                pythoncom.CoUninitialize()
            except:
                pass

    def create_workbook(self, *args, **kwargs) -> Workbook:
        """
        创建新工作簿

        Returns:
            Workbook 对象
        """
        return self.workbooks.add(*args, **kwargs)

    def open_workbook(self, *args, **kwargs) -> Workbook:
        """
        打开工作簿

        Args:
        Returns:
            Workbook 对象
        """
        return self.workbooks.open(*args, **kwargs)

    def close_all_workbooks(self, save_changes: bool = False):
        """
        关闭所有工作簿

        Args:
            save_changes: 是否保存更改
        """
        self.workbooks.close_all(save_changes=save_changes)

    def run_macro(self, macro_name: str, *args):
        """
        运行宏

        Args:
            macro_name: 宏名称
            *args: 宏参数
        """
        if not self.is_running:
            raise ExcelNotRunningError("Excel 未运行")

        try:
            return self._excel.Run(macro_name, *args)
        except Exception as e:
            raise ExcelCOMError(f"运行宏失败: {e}")

    def get_open_workbook_names(self) -> List[str]:
        """
        获取所有打开的工作簿名称

        Returns:
            工作簿名称列表
        """
        return self.workbooks.names

    def find_workbook_by_name(self, name: str) -> Optional[Workbook]:
        """
        通过名称查找工作簿

        Args:
            name: 工作簿名称

        Returns:
            Workbook 对象或 None
        """
        for wb in self.workbooks:
            if wb.name.lower() == name.lower():
                return wb
        return None

    def get_process_info(self) -> Dict[str, Any]:
        """
        获取进程信息

        Returns:
            进程信息字典
        """
        if not self._pid:
            return {}

        try:
            proc = psutil.Process(self._pid)
            return {
                'pid': self._pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(),
                'memory_percent': proc.memory_percent(),
                'create_time': proc.create_time(),
                'exe': proc.exe(),
                'cwd': proc.cwd(),
                'cmdline': proc.cmdline(),
                'username': proc.username(),
            }
        except:
            return {'pid': self._pid}

    @classmethod
    def get_all_instances(cls) -> List['ExcelApp']:
        """获取所有 ExcelApp 实例"""
        instances = list(cls._instances.values())
        if cls._instance:
            instances.append(cls._instance)
        return instances

    @classmethod
    def cleanup_all(cls):
        """清理所有实例"""
        for instance in cls.get_all_instances():
            try:
                instance.quit(force=True)
            except:
                pass
        cls._instances.clear()
        cls._instance = None

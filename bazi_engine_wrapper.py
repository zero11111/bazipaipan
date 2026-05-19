"""
八字计算引擎包装器 - 仅导入 Streamlit 需要的函数
避免导入 customtkinter 等桌面依赖
"""

import sys
import os

def load_engine():
    """安全加载计算引擎"""
    try:
        # 添加路径
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # 方法1：尝试直接导入核心函数
        try:
            from debt_query10 import (
                calc_bazi,
                query_debt_by_year,
                CITY_COORDINATES,
                WUXING_MATERIAL
            )
            return {
                'calc_bazi': calc_bazi,
                'query_debt_by_year': query_debt_by_year,
                'CITY_COORDINATES': CITY_COORDINATES,
                'WUXING_MATERIAL': WUXING_MATERIAL,
                'loaded': True,
                'error': None
            }
        except ImportError as e:
            if "customtkinter" in str(e).lower():
                # customtkinter 缺失，尝试绕过
                return load_engine_without_gui()
            else:
                raise

    except Exception as e:
        return {
            'loaded': False,
            'error': str(e)
        }


def load_engine_without_gui():
    """在不加载 GUI 组件的情况下导入计算引擎"""
    try:
        # 创建虚拟模块来替代 customtkinter
        import types

        # 创建假的 customtkinter 模块
        fake_ctk = types.ModuleType('customtkinter')
        fake_ctk.CTk = object
        fake_ctk.CTkFrame = object
        fake_ctk.CTkButton = object
        fake_ctk.CTkLabel = object
        fake_ctk.set_appearance_mode = lambda x: None
        fake_ctk.set_default_color_theme = lambda x: None

        sys.modules['customtkinter'] = fake_ctk

        # 现在可以安全导入 debt_query10 了
        from debt_query10 import (
            calc_bazi,
            query_debt_by_year,
            CITY_COORDINATES,
            WUXING_MATERIAL
        )

        return {
            'calc_bazi': calc_bazi,
            'query_debt_by_year': query_debt_by_year,
            'CITY_COORDINATES': CITY_COORDINATES,
            'WUXING_MATERIAL': WUXING_MATERIAL,
            'loaded': True,
            'error': None
        }

    except Exception as e:
        return {
            'loaded': False,
            'error': str(e)
        }

"""
道系命盘 · 五行推演 v1.1 - Streamlit 移动版（完整版）
基于传统命理文化推演,仅供娱乐参考 <昊東>
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta
from zhdate import ZhDate
from cnlunar import Lunar
import math
import sys

# ==============================================
# 导入完整版计算模块（必须在页面配置之前）
# ==============================================
try:
    # 添加当前目录到路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # 导入 debt_query10 的完整函数
    from debt_query10 import (
        calc_bazi,
        query_debt_by_year,
        CITY_COORDINATES,
        GANZHI_DEBT_MAP,
        WUXING_MATERIAL,
        make_yongjin
    )

    HAS_FULL_MODULE = True

except Exception as e:
    print(f"⚠ 无法加载完整模块: {e}")
    print("  将使用简化版计算逻辑")
    HAS_FULL_MODULE = False
    # 定义默认值
    CITY_COORDINATES = {
        "北京": (116.4074, 39.9042),
        "上海": (121.4737, 31.2304),
        "广州": (113.2644, 23.1291),
        "深圳": (114.0579, 22.5431),
        "成都": (104.0668, 30.5728),
    }
    GANZHI_DEBT_MAP = {}
    WUXING_MATERIAL = {
        "木": {"color": "绿色系", "base": "绿东陵、绿玉髓、绿檀", "up": "橄榄石、绿幽灵、翡翠"},
        "火": {"color": "红色系", "base": "红玛瑙、红玉髓、南红", "up": "石榴石、红碧玺、紫水晶"},
        "土": {"color": "黄棕色系", "base": "黄玛瑙、黄玉髓、茶晶", "up": "蜜蜡、黄水晶、虎眼石"},
        "金": {"color": "白色系", "base": "白玛瑙、白水晶、白萤石", "up": "和田玉、钛晶、银饰"},
        "水": {"color": "黑蓝色系", "base": "黑曜石、蓝玉髓、黑玛瑙", "up": "海蓝宝、蓝月光、冰种黑曜石"}
    }

# ==============================================
# 页面配置（直接在模块级别执行，Streamlit 会自动处理）
# ==============================================
st.set_page_config(
    page_title="道系命盘 · 五行推演",
    page_icon="☯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 样式优化（移动端适配）
st.markdown("""
<style>
    .main { background-color: #0b0907; color: #f3e7c5; }
    h1, h2, h3 { color: #c8a96b !important; text-align: center; }
    .stButton>button {
        background-color: #c8a96b; color: #0b0907; font-weight: bold;
        border-radius: 20px; width: 100%;
    }
    .stButton>button:hover { background-color: #e7c98f; }
    .success-box {
        background-color: #1a3a1a; border-left: 4px solid #4CAF50;
        padding: 15px; margin: 10px 0; border-radius: 5px;
    }
    .warning-box {
        background-color: #3a2a1a; border-left: 4px solid #FF9800;
        padding: 15px; margin: 10px 0; border-radius: 5px;
    }
    .wuxing-木 { color: #4CAF50; font-weight: bold; }
    .wuxing-火 { color: #F44336; font-weight: bold; }
    .wuxing-土 { color: #FF9800; font-weight: bold; }
    .wuxing-金 { color: #9E9E9E; font-weight: bold; }
    .wuxing-水 { color: #2196F3; font-weight: bold; }
    @media (max-width: 768px) {
        .main .block-container { padding: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================
# UI 界面
# ==============================================

def main():
    # 标题
    st.markdown("<h1>☯ 道系命盘 · 五行推演 v1.1 ☯</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8c7b5d;'>基于传统命理文化推演，仅供娱乐参考 &lt;昊東&gt;</p>", unsafe_allow_html=True)

    # 显示版本信息
    if HAS_FULL_MODULE:
        st.success("✅ 已加载完整版计算引擎（包含《穷通宝鉴》完整算法）")
    else:
        st.warning("⚠️ 使用简化版计算引擎")

    # 侧边栏 - 输入区
    with st.sidebar:
        st.header("📝 生辰信息")

        # 历法选择
        cal_type = st.radio("历法类型", ["公历", "农历"], index=0, horizontal=True)
        is_lunar = (cal_type == "农历")

        # 性别选择
        gender = st.radio("命造", ["乾造(男)", "坤造(女)"], index=0, horizontal=True)
        gender_short = "男" if gender == "乾造(男)" else "女"

        # 出生地（使用完整版城市列表）
        if HAS_FULL_MODULE:
            city_options = sorted(list(CITY_COORDINATES.keys()))
        else:
            city_options = ["北京", "上海", "广州", "深圳", "成都"]

        city_name = st.selectbox("出生地", city_options, index=0)

        st.divider()

        # 日期时间输入
        col1, col2, col3 = st.columns(3)
        with col1:
            year = st.number_input("年", min_value=1900, max_value=2100, value=1990)
        with col2:
            month = st.number_input("月", min_value=1, max_value=12, value=8)
        with col3:
            day = st.number_input("日", min_value=1, max_value=31, value=5)

        col4, col5 = st.columns(2)
        with col4:
            hour = st.number_input("时", min_value=0, max_value=23, value=12)
        with col5:
            minute = st.number_input("分", min_value=0, max_value=59, value=0)

        st.divider()

        # 高级选项
        with st.expander("⚙️ 高级选项"):
            use_true_solar = st.checkbox("启用真太阳时修正", value=True)
            use_dst = st.checkbox("考虑夏令时", value=False)
            use_early_zi = st.checkbox("区分早晚子时", value=True)

        # 查询按钮
        st.markdown("<br>", unsafe_allow_html=True)
        query_button = st.button("🔮 开始排盘", type="primary", use_container_width=True)

    # ==============================================
    # 主内容区
    # ==============================================

    if query_button:
        with st.spinner("正在排盘分析..."):
            try:
                if HAS_FULL_MODULE:
                    # 使用完整版计算引擎
                    table_data, error_msg, bracelet_data = calc_bazi(
                        year, month, day, hour, minute,
                        is_lunar, gender_short, city_name,
                        use_true_solar, use_dst, use_early_zi
                    )

                    if error_msg:
                        st.error(error_msg)
                        return

                    if bracelet_data:
                        display_full_result(bracelet_data, year)
                    else:
                        st.error("排盘失败，未返回结果")
                else:
                    st.error("完整模块未加载，请使用原版 desktop 应用")

            except Exception as e:
                import traceback
                st.error(f"❌ 排盘失败：{str(e)}")
                st.code(traceback.format_exc())
    else:
        # 初始状态 - 显示欢迎信息
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h2 style='color: #c8a96b;'>欢迎使用道系命盘</h2>
            <p style='color: #8c7b5d; font-size: 16px;'>
                请在左侧输入您的生辰信息，点击【开始排盘】按钮<br>
                即可获取专属的八字命盘、五行分析和受身债信息
            </p>
            <p style='color: #8c7b5d; font-size: 14px; margin-top: 30px;'>
                ✨ 功能特色：<br>
                • 精准八字排盘（基于《穷通宝鉴》）<br>
                • 五级层级用神分析<br>
                • 五行能量可视化<br>
                • 手串定制建议<br>
                • 受身债查询
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ==============================================
    # 页脚
    # ==============================================
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #8c7b5d; font-size: 12px;'>"
        "&lt;昊東&gt; 结果基于传统命理文化推演，仅供娱乐参考 &lt;昊東&gt;<br>"
        "道系命盘 · 五行推演 v1.1 | Powered by Streamlit"
        "</p>",
        unsafe_allow_html=True
    )


def display_full_result(bracelet_data, year):
    """显示完整的排盘结果（使用原版数据结构）"""

    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["📊 八字排盘", "🧿 五行分析", "💰 受身债"])

    # ===== 标签页1: 八字排盘 =====
    with tab1:
        st.subheader("八字命盘")

        # 基本信息
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**命造**: {bracelet_data.get('gender_label', '')}\n\n"
                   f"**公历**: {bracelet_data.get('solar_time', '')}\n\n"
                   f"**农历**: {bracelet_data.get('lunar_time_chinese', '')}")
        with col2:
            st.info(f"**日主**: {bracelet_data.get('benmingzhu', '')}\n\n"
                   f"**格局**: {bracelet_data.get('strong', '')}")

        # 本气格局分析
        if 'geju_analysis' in bracelet_data:
            st.markdown("### 📜 本气格局")
            st.write(bracelet_data['geju_analysis'])

        # 帮扶/克泄力量
        if 'bangfu_count' in bracelet_data:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("帮扶力量", bracelet_data['bangfu_count'])
            with col2:
                st.metric("克泄力量", bracelet_data.get('kexie_count', 0))

        # 病症列表
        if 'bingzheng_list' in bracelet_data and bracelet_data['bingzheng_list']:
            st.markdown("### 🔍 命局病症")
            bingzheng_str = "、".join(bracelet_data['bingzheng_list'])
            st.warning(bingzheng_str)

    # ===== 标签页2: 五行分析 =====
    with tab2:
        st.subheader("五行能量分布")

        # 五行进度条
        if 'scores' in bracelet_data:
            scores = bracelet_data['scores']
            wuxing_colors = {
                "木": "#4CAF50", "火": "#F44336", "土": "#FF9800",
                "金": "#9E9E9E", "水": "#2196F3"
            }

            max_score = max(scores.values()) if scores else 1

            for wx_name in ["木", "火", "土", "金", "水"]:
                score = scores.get(wx_name, 0)
                percentage = (score / max_score * 100) if max_score > 0 else 0

                st.markdown(f"""
                <div style="margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span style="color: {wuxing_colors[wx_name]}; font-size: 18px; font-weight: bold;">{wx_name}</span>
                        <span style="color: #f3e7c5;">{score:.1f}</span>
                    </div>
                    <div style="background-color: #1a1510; border-radius: 10px; height: 25px; overflow: hidden;">
                        <div style="background-color: {wuxing_colors[wx_name]}; width: {percentage}%; height: 100%; 
                                  border-radius: 10px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # 五级层级分析
        st.subheader("🎯 五级层级用神分析")

        # 第一用神
        if 'yong_shen_1' in bracelet_data:
            yong1 = bracelet_data['yong_shen_1']
            if isinstance(yong1, dict) and yong1.get('name'):
                st.markdown(f"""
                <div class='success-box'>
                    <h3 style='margin: 0 0 10px 0;'>⭐ 第一用神（全局头号刚需）</h3>
                    <p style='font-size: 24px; color: #4CAF50; margin: 10px 0;'>
                        {yong1['name']}
                    </p>
                    <p><strong>颜色：</strong>{yong1.get('detail', {}).get('color', '')}</p>
                    <p><strong>基础材质：</strong>{yong1.get('detail', {}).get('base', '')}</p>
                    <p><strong>升级材质：</strong>{yong1.get('detail', {}).get('up', '')}</p>
                </div>
                """, unsafe_allow_html=True)

        # 第二用神
        if 'yong_shen_2' in bracelet_data:
            yong2 = bracelet_data['yong_shen_2']
            if isinstance(yong2, dict) and yong2.get('name'):
                st.markdown(f"""
                <div class='success-box' style='border-left-color: #2196F3;'>
                    <h3 style='margin: 0 0 10px 0;'>⭐ 第二用神（辅助通关）</h3>
                    <p style='font-size: 20px; color: #2196F3; margin: 10px 0;'>
                        {yong2['name']}
                    </p>
                    <p><strong>颜色：</strong>{yong2.get('detail', {}).get('color', '')}</p>
                    <p><strong>基础材质：</strong>{yong2.get('detail', {}).get('base', '')}</p>
                    <p><strong>升级材质：</strong>{yong2.get('detail', {}).get('up', '')}</p>
                </div>
                """, unsafe_allow_html=True)

        # 闲神
        if 'xian_shen' in bracelet_data and bracelet_data['xian_shen']:
            xian_str = "、".join(bracelet_data['xian_shen'])
            st.info(f"⚖️ **闲神（中性五行）**：{xian_str}")

        # 一级忌神
        if 'ji_shen_1' in bracelet_data and bracelet_data['ji_shen_1']:
            ji1_str = "、".join(bracelet_data['ji_shen_1'])
            st.markdown(f"""
            <div class='warning-box'>
                <h3 style='margin: 0 0 10px 0; color: #F44336;'>❌ 一级忌神（严重危害）</h3>
                <p style='font-size: 18px;'>{ji1_str}</p>
            </div>
            """, unsafe_allow_html=True)

        # 二级忌神
        if 'ji_shen_2' in bracelet_data and bracelet_data['ji_shen_2']:
            ji2_str = "、".join(bracelet_data['ji_shen_2'])
            st.warning(f"⚠️ **二级忌神（轻微拖累）**：{ji2_str}")

        st.divider()

        # 专业分析报告
        if 'analysis_report' in bracelet_data:
            st.subheader("📖 专业分析报告")
            report = bracelet_data['analysis_report']

            # 分段显示报告
            sections = report.split("\n\n")
            for section in sections:
                if section.strip():
                    if section.startswith("【"):
                        st.markdown(f"**{section.split('】')[0]}】**")
                        if "】" in section:
                            content = section.split("】")[1].strip()
                            if content:
                                st.write(content)
                    else:
                        st.write(section)

        # 材质对照表
        st.subheader("📚 五行材质对照表")
        for wx, materials in WUXING_MATERIAL.items():
            with st.expander(f"{wx} ({materials['color']})"):
                st.write(f"**基础材质**：{materials['base']}")
                st.write(f"**升级材质**：{materials['up']}")

    # ===== 标签页3: 受身债 =====
    with tab3:
        st.subheader("💰 受身债查询")

        # 查询受身债
        if HAS_FULL_MODULE:
            debt_result = query_debt_by_year(year)
        else:
            debt_result = None

        if debt_result:
            # 基本信息
            col1, col2 = st.columns(2)
            with col1:
                st.metric("年份", debt_result['年份'])
                st.metric("干支", debt_result['干支'])
            with col2:
                st.metric("曹官", debt_result['曹官'])

            st.divider()

            # 债务详情
            st.markdown("### 债务明细")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**五斗十天干助生谢恩**\n\n{debt_result['五斗十天干助生谢恩']} 万贯")
            with col2:
                st.info(f"**十二地支助生谢恩**\n\n{debt_result['十二地支助生谢恩']} 万贯")
            with col3:
                st.info(f"**十二地支受生借款**\n\n{debt_result['十二地支受生借款']} 万贯")

            st.markdown(f"""
            <div class='warning-box' style='text-align: center;'>
                <h3 style='color: #FF9800; margin: 0;'>所欠合计</h3>
                <h2 style='color: #FF9800; margin: 10px 0;'>{debt_result['所欠合计']} 万贯</h2>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            # 偿还建议
            st.markdown("### 💡 偿还建议")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总贯数", f"{debt_result['总贯数']:,} 贯")
            with col2:
                st.metric("元宝袋数", f"{debt_result['元宝袋数']} 袋")
            with col3:
                st.metric("总价格", f"{debt_result['总价格']} 元")

            st.caption("注：1袋 = 7000贯，单价 69元/袋")
        else:
            st.warning(f"未找到 {year} 年的受身债信息")


# Streamlit 会自动执行这里的代码，不需要 if __name__ == "__main__"
main()

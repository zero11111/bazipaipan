"""
道系命盘 · 五行推演 v1.1 - Streamlit 移动版（完整版）
基于 debt_query10.py 完整计算引擎
移动端优化 - 上下布局
"""

import sys
import types
import json
import os
from datetime import datetime

# ==============================================
# 【关键修复】在导入任何模块前，创建虚拟 GUI 模块
# ==============================================
def create_fake_module(name):
    """创建虚拟模块以避免导入错误"""
    module = types.ModuleType(name)
    module.__file__ = f"/fake/{name}.py"
    sys.modules[name] = module
    return module

# 创建假的 tkinter 和 customtkinter 模块
fake_tk = create_fake_module('tkinter')
fake_tk.Tk = object
fake_tk.Frame = object
fake_tk.Label = object
fake_tk.Button = object
fake_tk.StringVar = object
fake_tk.IntVar = object
fake_tk.BooleanVar = object
fake_tk.DoubleVar = object
fake_tk.messagebox = types.ModuleType('messagebox')
fake_tk.messagebox.showerror = lambda *args, **kwargs: None
fake_tk.messagebox.showinfo = lambda *args, **kwargs: None
fake_tk.font = types.ModuleType('font')
fake_tk.font.Font = object
fake_tk.scrolledtext = types.ModuleType('scrolledtext')
fake_tk.scrolledtext.ScrolledText = object
fake_tk.ttk = types.ModuleType('ttk')
fake_tk.ttk.Treeview = object
fake_tk.ttk.Style = object

fake_ctk = create_fake_module('customtkinter')
fake_ctk.CTk = object
fake_ctk.CTkFrame = object
fake_ctk.CTkButton = object
fake_ctk.CTkLabel = object
fake_ctk.CTkEntry = object
fake_ctk.CTkComboBox = object
fake_ctk.CTkRadioButton = object
fake_ctk.CTkCheckBox = object
fake_ctk.CTkTextbox = object
fake_ctk.CTkTabview = object
fake_ctk.set_appearance_mode = lambda x: None
fake_ctk.set_default_color_theme = lambda x: None

# 现在可以安全导入 debt_query10 了
import streamlit as st

# ==============================================
# 页面配置（必须在最前面）
# ==============================================
st.set_page_config(
    page_title="道系命盘 · 五行推演",
    page_icon="☯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ... 其余代码保持不变 ...

# ==============================================
# CSS 样式（移动端优化）
# ==============================================
st.markdown("""
<style>
    .main { 
        background-color: #0b0907; 
        color: #f3e7c5; 
        padding: 10px;
    }
    h1 { 
        color: #c8a96b !important; 
        text-align: center; 
        font-size: 28px !important;
        margin: 10px 0;
    }
    h2, h3 { 
        color: #c8a96b !important; 
        font-size: 20px !important;
    }
    .stNumberInput > div > div > input {
        font-size: 16px !important;
        height: 45px !important;
    }
    .stButton>button {
        background-color: #c8a96b; 
        color: #0b0907; 
        font-weight: bold;
        border-radius: 25px; 
        width: 100%;
        height: 50px !important;
        font-size: 18px !important;
        margin: 10px 0;
    }
    .stButton>button:hover { 
        background-color: #e7c98f; 
    }
    .stRadio > div {
        flex-direction: row !important;
        gap: 10px;
    }
    .stSelectbox > div > div {
        font-size: 16px !important;
        min-height: 45px !important;
    }
    .stCheckbox > label {
        font-size: 16px !important;
    }
    .success-box {
        background-color: #1a3a1a; 
        border-left: 4px solid #4CAF50;
        padding: 15px; 
        margin: 10px 0; 
        border-radius: 10px;
    }
    .warning-box {
        background-color: #3a2a1a; 
        border-left: 4px solid #FF9800;
        padding: 15px; 
        margin: 10px 0; 
        border-radius: 10px;
    }
    .wuxing-木 { color: #4CAF50; font-weight: bold; }
    .wuxing-火 { color: #F44336; font-weight: bold; }
    .wuxing-土 { color: #FF9800; font-weight: bold; }
    .wuxing-金 { color: #9E9E9E; font-weight: bold; }
    .wuxing-水 { color: #2196F3; font-weight: bold; }
    .card {
        background-color: #15110d;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #2a2520;
    }
    hr {
        border-color: #2a2520;
        margin: 20px 0;
    }
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem;
            max-width: 100% !important;
        }
        h1 { font-size: 24px !important; }
        .stButton>button { font-size: 16px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================
# 导入完整计算引擎
# ==============================================

try:
    from bazi_engine_wrapper import load_engine

    engine = load_engine()

    if engine['loaded']:
        calc_bazi = engine['calc_bazi']
        query_debt_by_year = engine['query_debt_by_year']
        CITY_COORDINATES = engine['CITY_COORDINATES']
        WUXING_MATERIAL = engine['WUXING_MATERIAL']
        ENGINE_LOADED = True
    else:
        st.error(f"❌ 无法加载计算引擎: {engine['error']}")
        ENGINE_LOADED = False
        # 提供默认值
        CITY_COORDINATES = {"北京": (116.4074, 39.9042)}
        WUXING_MATERIAL = {}

except Exception as e:
    st.error(f"❌ 导入失败: {e}")
    ENGINE_LOADED = False
    CITY_COORDINATES = {"北京": (116.4074, 39.9042)}
    WUXING_MATERIAL = {}

# ==============================================
# 函数定义（必须在调用之前）
# ==============================================

HISTORY_FILE = "bazi_history.json"
MAX_HISTORY = 10

def load_history():
    """加载历史记录"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    """保存历史记录"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存历史记录失败: {e}")

def add_to_history(record):
    """添加记录到历史（保留最近10条）"""
    history = load_history()

    # 添加到开头
    history.insert(0, record)

    # 只保留最近10条
    if len(history) > MAX_HISTORY:
        history = history[:MAX_HISTORY]

    save_history(history)
    return history


# ... existing code ...

def display_history():
    """显示历史记录列表"""
    history = load_history()

    if not history:
        return None

    st.markdown("### 📜 最近排盘记录")

    selected_record = None

    for idx, record in enumerate(history):
        timestamp = record.get('timestamp', '')
        gender = record.get('gender_label', '')
        solar_time = record.get('solar_time', '')
        master = record.get('master', '')

        # 格式化显示
        display_text = f"{timestamp} | {gender} | {solar_time} | 日主:{master}"

        # 使用可点击的按钮
        if st.button(display_text, key=f"history_{idx}", use_container_width=True):
            selected_record = record

    if selected_record:
        st.divider()
        return selected_record

    return None


# ... existing code ...


def show_welcome():
    """显示欢迎界面"""
    st.markdown("""
    <div class="card" style='text-align: center;'>
        <h2 style='color: #c8a96b;'>欢迎使用道系命盘</h2>
        <p style='color: #8c7b5d; font-size: 16px;'>
            请输入您的生辰信息，点击【开始排盘】按钮<br>
            即可获取专属的八字命盘、五行分析和受身债信息
        </p>
        <p style='color: #8c7b5d; font-size: 14px; margin-top: 20px;'>
            ✨ 功能特色：<br>
            • 精准八字排盘（基于《穷通宝鉴》）<br>
            • 五级层级用神分析<br>
            • 五行能量可视化<br>
            • 手串定制建议<br>
            • 受身债查询
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_bazi_tab(bracelet_data, table_data=None):
    """显示八字排盘标签页"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("八字命盘")

    # 基本信息（垂直排列）
    st.info(
        f"**命造**: {bracelet_data.get('gender_label', '')}\n\n"
        f"**公历**: {bracelet_data.get('solar_time', '')}\n\n"
        f"**农历**: {bracelet_data.get('lunar_time_chinese', '')}"
    )

    st.info(
        f"**日主**: {bracelet_data.get('benmingzhu', '')}\n\n"
        f"**格局**: {bracelet_data.get('strong', '')}"
    )

    # 本气格局分析
    if 'geju_analysis' in bracelet_data and bracelet_data['geju_analysis']:
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

    # 四柱表格
    if table_data:
        st.markdown("### 四柱信息")
        import pandas as pd

        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)




def display_wuxing_tab(bracelet_data):
    """显示五行分析标签页"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
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
            <div style="margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: {wuxing_colors[wx_name]}; font-size: 18px; font-weight: bold;">{wx_name}</span>
                    <span style="color: #f3e7c5; font-size: 16px;">{score:.1f}</span>
                </div>
                <div style="background-color: #1a1510; border-radius: 10px; height: 30px; overflow: hidden;">
                    <div style="background-color: {wuxing_colors[wx_name]}; width: {percentage}%; height: 100%; 
                              border-radius: 10px; transition: width 0.3s ease;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ==============================================
    # 五级层级用神分析（整合推导理由）
    # ==============================================
    st.subheader("🎯 五级层级用神分析")

    # 获取分析报告
    analysis_report = bracelet_data.get('analysis_report', '')

    # 第一用神
    if 'yong_shen_1' in bracelet_data:
        yong1 = bracelet_data['yong_shen_1']
        if isinstance(yong1, dict) and yong1.get('name'):
            # 从 analysis_report 中提取第一用神推导理由
            reason = extract_yong_reason(analysis_report, "第一用神推导")

            st.markdown(f"""
            <div class='success-box'>
                <h3 style='margin: 0 0 10px 0;'>⭐ 第一用神：{yong1['name']}</h3>
            """, unsafe_allow_html=True)

            # 如果有推导理由，先显示
            if reason:
                st.markdown(f"""
                <p style='color: #c8a96b; font-style: italic; margin: 10px 0; padding: 10px; 
                         background-color: #0b0907; border-radius: 5px;'>
                    💡 <strong>推导理由：</strong><br>
                    {reason.replace(chr(10), '<br>')}
                </p>
                """, unsafe_allow_html=True)

            # 显示材质信息
            st.markdown(f"""
                <p><strong>颜色：</strong>{yong1.get('detail', {}).get('color', '')}</p>
                <p><strong>基础材质：</strong>{yong1.get('detail', {}).get('base', '')}</p>
                <p><strong>升级材质：</strong>{yong1.get('detail', {}).get('up', '')}</p>
            </div>
            """, unsafe_allow_html=True)

    # 第二用神
    if 'yong_shen_2' in bracelet_data:
        yong2 = bracelet_data['yong_shen_2']
        if isinstance(yong2, dict) and yong2.get('name'):
            # 从 analysis_report 中提取第二用神推导理由
            reason = extract_yong_reason(analysis_report, "第二用神推导")

            st.markdown(f"""
            <div class='success-box' style='border-left-color: #2196F3;'>
                <h3 style='margin: 0 0 10px 0;'>⭐ 第二用神：{yong2['name']}</h3>
            """, unsafe_allow_html=True)

            if reason:
                st.markdown(f"""
                <p style='color: #c8a96b; font-style: italic; margin: 10px 0; padding: 10px; 
                         background-color: #0b0907; border-radius: 5px;'>
                    💡 <strong>推导理由：</strong><br>
                    {reason.replace(chr(10), '<br>')}
                </p>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                <p><strong>颜色：</strong>{yong2.get('detail', {}).get('color', '')}</p>
                <p><strong>基础材质：</strong>{yong2.get('detail', {}).get('base', '')}</p>
                <p><strong>升级材质：</strong>{yong2.get('detail', {}).get('up', '')}</p>
            </div>
            """, unsafe_allow_html=True)

    # 闲神
    if 'xian_shen' in bracelet_data and bracelet_data['xian_shen']:
        xian_str = "、".join(bracelet_data['xian_shen'])
        # 提取闲神说明
        xian_reason = extract_yong_reason(analysis_report, "闲神说明")

        st.info(f"⚖️ **闲神（中性五行）**：{xian_str}")
        if xian_reason:
            st.markdown(f"""
            <p style='color: #8c7b5d; font-style: italic; margin: 5px 0; padding: 8px; 
                     background-color: #15110d; border-radius: 5px; font-size: 14px;'>
                💡 {xian_reason}
            </p>
            """, unsafe_allow_html=True)

    # 一级忌神
    if 'ji_shen_1' in bracelet_data and bracelet_data['ji_shen_1']:
        ji1_str = "、".join(bracelet_data['ji_shen_1'])
        # 提取一级忌神推导
        ji1_reason = extract_yong_reason(analysis_report, "一级忌神推导")

        st.markdown(f"""
        <div class='warning-box'>
            <h3 style='margin: 0 0 10px 0; color: #F44336;'>❌ 一级忌神</h3>
            <p style='font-size: 18px;'>{ji1_str}</p>
        """, unsafe_allow_html=True)

        if ji1_reason:
            st.markdown(f"""
            <p style='color: #ff9999; font-style: italic; margin: 10px 0; padding: 8px; 
                     background-color: #2a1a1a; border-radius: 5px; font-size: 14px;'>
                ⚠️ {ji1_reason}
            </p>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # 二级忌神
    if 'ji_shen_2' in bracelet_data and bracelet_data['ji_shen_2']:
        ji2_str = "、".join(bracelet_data['ji_shen_2'])
        # 提取二级忌神推导
        ji2_reason = extract_yong_reason(analysis_report, "二级忌神推导")

        st.warning(f"⚠️ **二级忌神（轻微拖累）**：{ji2_str}")
        if ji2_reason:
            st.markdown(f"""
            <p style='color: #ccaa88; font-style: italic; margin: 5px 0; padding: 8px; 
                     background-color: #1a1510; border-radius: 5px; font-size: 14px;'>
                ℹ️ {ji2_reason}
            </p>
            """, unsafe_allow_html=True)

    st.divider()

    # ==============================================
    # 专业分析报告（简化版，只显示核心内容）
    # ==============================================
    if analysis_report:
        st.subheader("📖 完整分析报告")

        # 分段显示
        sections = analysis_report.split("\n\n")
        for section in sections:
            if section.strip():
                if section.startswith("【"):
                    title = section.split('】')[0] + "】"
                    content = section.split('】', 1)[1].strip() if '】' in section else ""
                    st.markdown(f"**{title}**")
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

    st.markdown('</div>', unsafe_allow_html=True)


def extract_yong_reason(analysis_report, section_name):
    """从分析报告中提取指定章节的推导理由"""
    if not analysis_report or not section_name:
        return ""

    try:
        search_key = f"【{section_name}】"
        if search_key in analysis_report:
            # 提取该章节内容
            temp = analysis_report.split(search_key)[1]
            # 找到下一个【或结尾
            if "【" in temp:
                reason = temp.split("【")[0].strip()
            else:
                reason = temp.strip()
            return reason
    except Exception as e:
        print(f"提取推导理由失败: {e}")

    return ""


def display_debt_tab(year):
    """显示受身债标签页"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💰 受身债查询")

    debt_result = query_debt_by_year(year)

    if debt_result:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("年份", debt_result['年份'])
            st.metric("干支", debt_result['干支'])
        with col2:
            st.metric("曹官", debt_result['曹官'])

        st.divider()

        st.markdown("### 债务明细")

        st.info(f"**五斗十天干助生谢恩**：{debt_result['五斗十天干助生谢恩']} 万贯")
        st.info(f"**十二地支助生谢恩**：{debt_result['十二地支助生谢恩']} 万贯")
        st.info(f"**十二地支受生借款**：{debt_result['十二地支受生借款']} 万贯")

        st.markdown(f"""
        <div class='warning-box' style='text-align: center;'>
            <h3 style='color: #FF9800; margin: 0;'>所欠合计</h3>
            <h2 style='color: #FF9800; margin: 10px 0;'>{debt_result['所欠合计']} 万贯</h2>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

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

    st.markdown('</div>', unsafe_allow_html=True)


def display_results(bracelet_data, year, table_data=None):
    """显示完整的排盘结果"""
    tab1, tab2, tab3 = st.tabs(["📊 八字排盘", "🧿 五行分析", "💰 受身债"])

    with tab1:
        display_bazi_tab(bracelet_data, table_data)

    with tab2:
        display_wuxing_tab(bracelet_data)

    with tab3:
        display_debt_tab(year)


# ... existing code ...

# ==============================================
# 标题区
# ==============================================
st.markdown("<h1>☯ 道系命盘</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #8c7b5d; font-size: 14px;'>"
    "基于传统命理文化推演，仅供娱乐参考 &lt;昊東&gt;"
    "</p>",
    unsafe_allow_html=True
)

if ENGINE_LOADED:
    st.success("✅ 已加载完整版计算引擎")
else:
    st.warning("⚠️ 计算引擎加载失败")

# ==============================================
# 输入区（改为卡片式上下布局）
# ==============================================
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📝 生辰信息")

    col1, col2 = st.columns(2)
    with col1:
        cal_type = st.radio("历法类型", ["公历", "农历"], index=0, horizontal=True)
        is_lunar = (cal_type == "农历")

    with col2:
        gender = st.radio("命造", ["乾造(男)", "坤造(女)"], index=0, horizontal=True)
        gender_short = "男" if gender == "乾造(男)" else "女"

    city_options = sorted(list(CITY_COORDINATES.keys())) if ENGINE_LOADED else ["北京", "上海", "广州"]
    city_name = st.selectbox("🌍 出生地", city_options, index=0)

    st.divider()

    st.markdown("#### 📅 出生日期")
    col1, col2, col3 = st.columns(3)
    with col1:
        year = st.number_input("年", min_value=1800, max_value=2100, value=1990, step=1)
    with col2:
        month = st.number_input("月", min_value=1, max_value=12, value=8, step=1)
    with col3:
        day = st.number_input("日", min_value=1, max_value=31, value=5, step=1)

    st.markdown("#### ⏰ 出生时间")
    col1, col2 = st.columns(2)
    with col1:
        hour = st.number_input("时", min_value=0, max_value=23, value=12, step=1)
    with col2:
        minute = st.number_input("分", min_value=0, max_value=59, value=0, step=1)

    st.divider()

    with st.expander("⚙️ 高级选项"):
        use_true_solar = st.checkbox("启用真太阳时修正", value=True)
        use_dst = st.checkbox("考虑夏令时", value=False)
        use_early_zi = st.checkbox("区分早晚子时", value=True)

    st.markdown('</div>', unsafe_allow_html=True)

query_button = st.button("🔮 开始排盘", type="primary", use_container_width=True)

# ==============================================
# 主内容区
# ==============================================

# 初始化 session state
if 'selected_history_idx' not in st.session_state:
    st.session_state.selected_history_idx = None
if 'last_result' not in st.session_state:
    st.session_state.last_result = None
if 'should_rerun' not in st.session_state:
    st.session_state.should_rerun = False

# ... existing code ...

# 加载历史记录
history = load_history()

# 显示历史记录列表（如果有）
if history:
    st.markdown("---")
    st.markdown("### 📜 最近排盘记录")

    for idx, record in enumerate(history):
        timestamp = record.get('timestamp', '')
        gender_label = record.get('gender_label', '')
        solar_time = record.get('solar_time', '')
        master = record.get('master', '')

        # 提取用神信息
        yong_shen_1 = record.get('yong_shen_1', {})
        yong_name_1 = yong_shen_1.get('name', '') if isinstance(yong_shen_1, dict) else ''

        yong_shen_2 = record.get('yong_shen_2', {})
        yong_name_2 = yong_shen_2.get('name', '') if isinstance(yong_shen_2, dict) else ''

        ji_shen_1 = record.get('ji_shen_1', [])
        ji_str_1 = '、'.join(ji_shen_1) if ji_shen_1 else ''

        # 格式化显示 - 包含用喜忌信息
        display_parts = [timestamp, gender_label, f"日主:{master}"]

        if yong_name_1:
            display_parts.append(f"用:{yong_name_1}")
        if yong_name_2:
            display_parts.append(f"喜:{yong_name_2}")
        if ji_str_1:
            display_parts.append(f"忌:{ji_str_1}")

        display_text = " | ".join(display_parts)

        # 使用可点击的按钮
        if st.button(display_text, key=f"hist_btn_{idx}", use_container_width=True):
            st.session_state.selected_history_idx = idx
            st.session_state.should_rerun = True
            st.rerun()

# ... existing code ...


# 处理历史记录点击
if st.session_state.selected_history_idx is not None and st.session_state.selected_history_idx < len(history):
    selected_record = history[st.session_state.selected_history_idx]

    st.divider()
    st.info(f"📌 正在查看历史记录：{selected_record.get('timestamp', '')}")

    with st.spinner("正在加载历史记录..."):
        try:
            table_data, error_msg, bracelet_data = calc_bazi(
                selected_record['year'],
                selected_record['month'],
                selected_record['day'],
                selected_record['hour'],
                selected_record['minute'],
                selected_record['is_lunar'],
                selected_record['gender_short'],
                selected_record['city_name'],
                selected_record.get('use_true_solar', True),
                selected_record.get('use_dst', False),
                selected_record.get('use_early_zi', True)
            )

            if error_msg:
                st.error(error_msg)
            elif bracelet_data:
                display_results(bracelet_data, selected_record['year'], table_data)

                # 保存结果到 session state
                st.session_state.last_result = {
                    'bracelet_data': bracelet_data,
                    'year': selected_record['year'],
                    'table_data': table_data
                }
            else:
                st.error("排盘失败，未返回结果")

        except Exception as e:
            import traceback
            st.error(f"❌ 加载失败：{str(e)}")
            with st.expander("查看详细错误"):
                st.code(traceback.format_exc())

elif query_button:
    if not ENGINE_LOADED:
        st.error("计算引擎未加载，无法排盘")
    else:
        with st.spinner("正在排盘分析..."):
            try:
                table_data, error_msg, bracelet_data = calc_bazi(
                    year, month, day, hour, minute,
                    is_lunar, gender_short, city_name,
                    use_true_solar, use_dst, use_early_zi
                )

                if error_msg:
                    st.error(error_msg)
                elif bracelet_data:
                    # 清除选中的历史记录
                    st.session_state.selected_history_idx = None

                    # 显示结果
                    display_results(bracelet_data, year, table_data)

                    # 保存到历史记录
                    history_record = {
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'year': year,
                        'month': month,
                        'day': day,
                        'hour': hour,
                        'minute': minute,
                        'is_lunar': is_lunar,
                        'gender_short': gender_short,
                        'city_name': city_name,
                        'use_true_solar': use_true_solar,
                        'use_dst': use_dst,
                        'use_early_zi': use_early_zi,
                        **bracelet_data
                    }
                    add_to_history(history_record)

                    # 保存最后一次的完整结果
                    st.session_state.last_result = {
                        'bracelet_data': bracelet_data,
                        'year': year,
                        'table_data': table_data
                    }

                    # 触发页面刷新以显示新的历史记录
                    st.rerun()
                else:
                    st.error("排盘失败，未返回结果")

            except Exception as e:
                import traceback
                st.error(f"❌ 排盘失败：{str(e)}")
                with st.expander("查看详细错误"):
                    st.code(traceback.format_exc())

elif st.session_state.last_result:
    # 显示上次的排盘结果
    result = st.session_state.last_result
    display_results(result['bracelet_data'], result['year'], result['table_data'])

else:
    show_welcome()

# ... existing code ...


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

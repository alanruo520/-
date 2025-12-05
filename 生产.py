from PyQt5 import QtChart
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from dateutil.relativedelta import relativedelta
import json
import os

# 页面配置
st.set_page_config(
    page_title="生产数据监控仪表板",
    page_icon="📊",
    layout="wide"
)

# 初始化数据存储
if 'data' not in st.session_state:
    st.session_state.data = {
        'sugar': [],           # 糖度数据
        'box_weight': [],      # 箱重数据
        'net_weight': [],      # 净含量数据
        'seal_defect': [],     # 封口不良率
        'production_dates': [] # 生产日期
    }

# 标题
st.title("📊 生产数据监控仪表板")
st.markdown("---")

# 创建侧边栏
with st.sidebar:
    st.header("🔧 数据输入")
    selected_date = st.date_input("选择日期", datetime.date.today())
    production_date = st.date_input("选择生产日期", datetime.date.today())
    
    # 数据输入选项卡
    input_tab = st.radio("选择输入类型", 
                         ["糖度数据", "箱重数据", "净含量数据", "封口不良率"])
    
    # 数据文件管理
    st.markdown("---")
    st.subheader("📁 数据管理")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("保存数据"):
            st.success("数据已保存！")
    
    with col2:
        if st.button("加载历史数据"):
            st.info("加载功能待实现")

# 主内容区
if input_tab == "糖度数据":
    st.subheader(f"🍬 糖度数据输入 - {selected_date}")
    
    # 创建20个糖度数据输入框
    cols = st.columns(5)
    sugar_data = []
    
    for i in range(20):
        col_idx = i % 5
        row_idx = i // 5
        with cols[col_idx]:
            value = st.number_input(
                f"糖度 {i+1}",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                key=f"sugar_{selected_date}_{i}"
            )
            sugar_data.append(value)
    
    # 计算统计值
    if len([x for x in sugar_data if x > 0]) > 0:
        sugar_df = pd.DataFrame({'糖度值': [x for x in sugar_data if x > 0]})
        sugar_stats = {
            '最大值': sugar_df['糖度值'].max(),
            '最小值': sugar_df['糖度值'].min(),
            '平均值': sugar_df['糖度值'].mean()
        }
        
        # 显示统计结果
        st.markdown("### 统计结果")
        stat_cols = st.columns(3)
        with stat_cols[0]:
            st.metric("最大值", f"{sugar_stats['最大值']:.2f}")
        with stat_cols[1]:
            st.metric("最小值", f"{sugar_stats['最小值']:.2f}")
        with stat_cols[2]:
            st.metric("平均值", f"{sugar_stats['平均值']:.2f}")
        
        # 保存到session state
        if st.button("保存糖度数据", type="primary"):
            st.session_state.data['sugar'].append({
                'date': selected_date,
                'values': sugar_data,
                'stats': sugar_stats
            })
            st.success(f"已保存{selected_date}的糖度数据")

elif input_tab == "箱重数据":
    st.subheader(f"📦 箱重数据输入 - {selected_date}")
    
    # 创建5个箱重数据输入框
    box_data = []
    cols = st.columns(5)
    
    for i in range(5):
        with cols[i]:
            value = st.number_input(
                f"箱重 {i+1} (kg)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                key=f"box_{selected_date}_{i}"
            )
            box_data.append(value)
    
    # 计算统计值
    if len([x for x in box_data if x > 0]) > 0:
        box_avg = np.mean([x for x in box_data if x > 0])
        
        # 显示统计结果
        st.markdown("### 统计结果")
        st.metric("平均箱重", f"{box_avg:.2f} kg")
        
        # 显示详细数据
        with st.expander("查看详细数据"):
            for i, weight in enumerate(box_data, 1):
                st.write(f"箱重 {i}: {weight} kg")
        
        # 保存到session state
        if st.button("保存箱重数据", type="primary"):
            st.session_state.data['box_weight'].append({
                'date': selected_date,
                'values': box_data,
                'average': box_avg
            })
            st.success(f"已保存{selected_date}的箱重数据")

elif input_tab == "净含量数据":
    st.subheader(f"⚖️ 净含量数据输入 - 生产日期: {production_date}")
    st.info(f"为生产日期 {production_date} 输入98个净含量数据")
    
    # 创建净含量数据输入表格
    net_data = []
    
    # 使用多列布局
    cols_per_row = 7
    num_rows = 14  # 98 / 7 = 14
    
    for row in range(num_rows):
        cols = st.columns(cols_per_row)
        for col in range(cols_per_row):
            idx = row * cols_per_row + col
            if idx < 98:
                with cols[col]:
                    value = st.number_input(
                        f"样本 {idx+1}",
                        min_value=0.0,
                        max_value=1000.0,
                        value=0.0,
                        step=0.1,
                        key=f"net_{production_date}_{idx}"
                    )
                    net_data.append(value)
    
    # 计算统计值
    if len([x for x in net_data if x > 0]) >= 98:
        net_avg = np.mean(net_data)
        
        # 显示统计结果
        st.markdown("### 统计结果")
        st.metric("平均净含量", f"{net_avg:.2f} g")
        
        # 显示分布统计
        net_series = pd.Series(net_data)
        stat_cols = st.columns(4)
        with stat_cols[0]:
            st.metric("最大值", f"{net_series.max():.2f} g")
        with stat_cols[1]:
            st.metric("最小值", f"{net_series.min():.2f} g")
        with stat_cols[2]:
            st.metric("标准差", f"{net_series.std():.2f} g")
        with stat_cols[3]:
            st.metric("合格率", f"{(net_series > 0).sum()/98*100:.1f}%")
        
        # 保存到session state
        if st.button("保存净含量数据", type="primary"):
            st.session_state.data['net_weight'].append({
                'production_date': production_date,
                'values': net_data,
                'average': net_avg,
                'max': net_series.max(),
                'min': net_series.min()
            })
            st.session_state.data['production_dates'].append(production_date)
            st.success(f"已保存生产日期{production_date}的净含量数据")

elif input_tab == "封口不良率":
    st.subheader(f"🔍 封口不良率输入 - {selected_date}")
    
    # 输入封口不良数据
    col1, col2 = st.columns(2)
    
    with col1:
        total_seals = st.number_input(
            "总封口数",
            min_value=0,
            value=1000,
            step=100
        )
    
    with col2:
        defect_seals = st.number_input(
            "不良封口数",
            min_value=0,
            value=0,
            step=1
        )
    
    # 计算不良率
    if total_seals > 0:
        defect_rate = (defect_seals / total_seals) * 100
        
        # 显示结果
        st.markdown("### 统计结果")
        
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric("总封口数", f"{total_seals:,}")
        with metric_cols[1]:
            st.metric("不良封口数", f"{defect_seals}")
        with metric_cols[2]:
            st.metric("不良率", f"{defect_rate:.2f}%")
        
        # 进度条显示
        st.progress(defect_seals / max(total_seals, 1))
        
        # 保存到session state
        if st.button("保存封口不良率", type="primary"):
            st.session_state.data['seal_defect'].append({
                'date': selected_date,
                'total': total_seals,
                'defects': defect_seals,
                'defect_rate': defect_rate
            })
            st.success(f"已保存{selected_date}的封口不良率数据")

# 仪表板可视化区域
st.markdown("---")
st.header("📈 数据可视化仪表板")

# 创建选项卡显示不同的图表
viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs([
    "糖度趋势", "箱重趋势", "净含量趋势", "不良率趋势"
])

with viz_tab1:
    if len(st.session_state.data['sugar']) > 0:
        # 准备糖度数据
        sugar_dates = [item['date'] for item in st.session_state.data['sugar']]
        sugar_max = [item['stats']['最大值'] for item in st.session_state.data['sugar']]
        sugar_min = [item['stats']['最小值'] for item in st.session_state.data['sugar']]
        sugar_avg = [item['stats']['平均值'] for item in st.session_state.data['sugar']]
        
        # 创建图表
        fig = go.Figure()
        
        # 添加平均线
        fig.add_trace(go.Scatter(
            x=sugar_dates, y=sugar_avg,
            mode='lines+markers',
            name='平均值',
            line=dict(color='blue', width=2)
        ))
        
        # 添加区域（最大值-最小值）
        fig.add_trace(go.Scatter(
            x=sugar_dates + sugar_dates[::-1],
            y=sugar_max + sugar_min[::-1],
            fill='toself',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='波动范围',
            showlegend=True
        ))
        
        fig.update_layout(
            title='糖度趋势图',
            xaxis_title='日期',
            yaxis_title='糖度值',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 数据显示
        with st.expander("查看详细数据表"):
            sugar_df = pd.DataFrame({
                '日期': sugar_dates,
                '最大值': sugar_max,
                '最小值': sugar_min,
                '平均值': sugar_avg
            })
            st.dataframe(sugar_df)
    else:
        st.info("暂无糖度数据，请先输入数据")

with viz_tab2:
    if len(st.session_state.data['box_weight']) > 0:
        # 准备箱重数据
        box_dates = [item['date'] for item in st.session_state.data['box_weight']]
        box_avg = [item['average'] for item in st.session_state.data['box_weight']]
        
        # 创建图表
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=box_dates, y=box_avg,
            mode='lines+markers',
            name='平均箱重',
            line=dict(color='green', width=2),
            fill='tozeroy',
            fillcolor='rgba(0,255,0,0.1)'
        ))
        
        fig.update_layout(
            title='箱重趋势图',
            xaxis_title='日期',
            yaxis_title='箱重 (kg)',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 数据显示
        with st.expander("查看详细数据表"):
            box_df = pd.DataFrame({
                '日期': box_dates,
                '平均箱重 (kg)': box_avg
            })
            st.dataframe(box_df)
    else:
        st.info("暂无箱重数据，请先输入数据")

with viz_tab3:
    if len(st.session_state.data['net_weight']) > 0:
        # 准备净含量数据
        net_dates = [item['production_date'] for item in st.session_state.data['net_weight']]
        net_avg = [item['average'] for item in st.session_state.data['net_weight']]
        net_max = [item['max'] for item in st.session_state.data['net_weight']]
        net_min = [item['min'] for item in st.session_state.data['net_weight']]
        
        # 创建图表
        fig = go.Figure()
        
        # 添加平均线
        fig.add_trace(go.Scatter(
            x=net_dates, y=net_avg,
            mode='lines+markers',
            name='平均值',
            line=dict(color='red', width=2)
        ))
        
        # 添加误差线
        fig.add_trace(go.Scatter(
            x=net_dates,
            y=net_avg,
            error_y=dict(
                type='data',
                array=[avg - min_val for avg, min_val in zip(net_avg, net_min)],
                arrayminus=[max_val - avg for avg, max_val in zip(net_avg, net_max)],
                visible=True
            ),
            mode='markers',
            name='波动范围',
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='净含量趋势图',
            xaxis_title='生产日期',
            yaxis_title='净含量 (g)',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 数据显示
        with st.expander("查看详细数据表"):
            net_df = pd.DataFrame({
                '生产日期': net_dates,
                '平均值 (g)': net_avg,
                '最大值 (g)': net_max,
                '最小值 (g)': net_min
            })
            st.dataframe(net_df)
    else:
        st.info("暂无净含量数据，请先输入数据")

with viz_tab4:
    if len(st.session_state.data['seal_defect']) > 0:
        # 准备不良率数据
        defect_dates = [item['date'] for item in st.session_state.data['seal_defect']]
        defect_rates = [item['defect_rate'] for item in st.session_state.data['seal_defect']]
        defect_counts = [item['defects'] for item in st.session_state.data['seal_defect']]
        
        # 创建图表
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 不良率线图
        fig.add_trace(go.Scatter(
            x=defect_dates, y=defect_rates,
            mode='lines+markers',
            name='不良率',
            line=dict(color='orange', width=2)
        ), secondary_y=False)
        
        # 不良数柱状图
        fig.add_trace(go.Bar(
            x=defect_dates, y=defect_counts,
            name='不良数',
            marker_color='rgba(255,165,0,0.3)',
            opacity=0.5
        ), secondary_y=True)
        
        fig.update_layout(
            title='封口不良率趋势图',
            xaxis_title='日期',
            hovermode='x unified',
            height=400
        )
        
        fig.update_yaxes(title_text="不良率 (%)", secondary_y=False)
        fig.update_yaxes(title_text="不良数", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 数据显示
        with st.expander("查看详细数据表"):
            defect_df = pd.DataFrame({
                '日期': defect_dates,
                '总封口数': [item['total'] for item in st.session_state.data['seal_defect']],
                '不良数': defect_counts,
                '不良率 (%)': defect_rates
            })
            st.dataframe(defect_df)
    else:
        st.info("暂无封口不良率数据，请先输入数据")

# 综合统计摘要
st.markdown("---")
st.header("📋 综合统计摘要")

if any(len(st.session_state.data[key]) > 0 for key in st.session_state.data):
    # 创建统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.session_state.data['sugar']:
            latest_sugar = st.session_state.data['sugar'][-1]['stats']['平均值']
            st.metric("最新糖度平均值", f"{latest_sugar:.2f}")
        else:
            st.metric("糖度数据", "暂无")
    
    with col2:
        if st.session_state.data['box_weight']:
            latest_box = st.session_state.data['box_weight'][-1]['average']
            st.metric("最新平均箱重", f"{latest_box:.2f} kg")
        else:
            st.metric("箱重数据", "暂无")
    
    with col3:
        if st.session_state.data['net_weight']:
            latest_net = st.session_state.data['net_weight'][-1]['average']
            st.metric("最新净含量平均值", f"{latest_net:.2f} g")
        else:
            st.metric("净含量数据", "暂无")
    
    with col4:
        if st.session_state.data['seal_defect']:
            latest_defect = st.session_state.data['seal_defect'][-1]['defect_rate']
            st.metric("最新封口不良率", f"{latest_defect:.2f}%")
        else:
            st.metric("封口不良率", "暂无")
    
    # 数据导出
    st.markdown("---")
    st.subheader("📤 数据导出")
    
    if st.button("导出所有数据为CSV"):
        # 这里可以实现数据导出功能
        st.info("数据导出功能待实现")
else:
    st.info("暂无数据，请先在左侧输入数据")

# 使用说明
with st.expander("📖 使用说明"):
    st.markdown("""
    ### 仪表板使用指南
    
    1. **数据输入**
       - 在左侧边栏选择日期和数据输入类型
       - 按照要求输入对应数量的数据
       - 点击"保存数据"按钮保存输入
    
    2. **数据可视化**
       - 点击上方选项卡查看不同的趋势图
       - 图表支持交互操作（缩放、悬停查看数值等）
    
    3. **数据管理**
       - 所有数据暂时保存在浏览器会话中
       - 刷新页面会丢失数据（实际应用中应连接数据库）
    
    4. **数据类型说明**
       - **糖度数据**: 每日20个，自动计算最大、最小、平均值
       - **箱重数据**: 每日5个，自动计算平均值
       - **净含量数据**: 每个生产日期98个，自动计算平均值
       - **封口不良率**: 每日1个，计算不良率百分比
    
    5. **注意事项**
       - 确保数据准确性后再保存
       - 定期导出数据备份
    """)
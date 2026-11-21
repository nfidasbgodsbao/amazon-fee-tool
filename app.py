import streamlit as st
import pandas as pd

st.set_page_config(page_title="亚马逊费用预测器", layout="wide")
st.title("📦 亚马逊费用与未来预测工具")

# --- 侧边栏：基础设置 ---
st.sidebar.header("⚙️ 基础产品与费率设置")
price = st.sidebar.number_input("产品售价 ($)", min_value=0.0, value=29.99, step=1.0)
cost = st.sidebar.number_input("产品成本 ($)", min_value=0.0, value=10.0, step=1.0)
fba_fee = st.sidebar.number_input("FBA 基础配送费 ($)", min_value=0.0, value=5.0, step=0.5)
commission_rate = st.sidebar.slider("销售佣金比例 (%)", 0, 30, 15) / 100
# 附加费
fuel_surcharge_rate = st.sidebar.slider("物流附加费率 (%)", 0.0, 10.0, 3.5, step=0.1) / 100

# --- 侧边栏：库存与仓储设置 ---
st.sidebar.header("📦 库存与仓储")
daily_sales = st.sidebar.number_input("日均销量 (件)", min_value=1, value=10, step=1)
current_inventory = st.sidebar.number_input("当前库存总量 (件)", min_value=0, value=500, step=10)
unit_volume = st.sidebar.number_input("单件体积 (立方英尺)", min_value=0.01, value=0.2, step=0.01)
monthly_storage_fee_per_cuft = st.sidebar.number_input("月度仓储费率 ($/立方英尺)", value=0.87, step=0.01)

# 惩罚费率设定
low_stock_fee_per_unit = st.sidebar.number_input("低库存罚款预估 ($/件)", value=0.35, step=0.01)
aged_stock_fee_per_unit = st.sidebar.number_input("老化库存附加费预估 ($/件)", value=0.50, step=0.01)

# --- 主界面：计算逻辑 ---
# 1. 单件利润计算
total_revenue = price
commission_fee = price * commission_rate
fuel_fee = fba_fee * fuel_surcharge_rate
total_fees = commission_fee + fba_fee + fuel_fee
net_profit = total_revenue - cost - total_fees
margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("单件销售额", f"${total_revenue:.2f}")
col2.metric("单件总费用", f"${total_fees:.2f}")
col3.metric("单件净利润", f"${net_profit:.2f}", delta=f"{margin:.1f}% 利润率")
col4.metric("预计断货天数", f"{int(current_inventory / daily_sales)} 天")

st.markdown("---")

# 2. 未来 6 个月库存与费用预测
st.subheader("📈 未来 6 个月库存与费用预测")
st.write("假设日均销量不变，且无新补货的情况下，你的库存演变与潜在费用：")

forecast_data = []
for month in range(1, 7):
    # 每月按30天算
    inventory_start = current_inventory - (daily_sales * 30 * (month - 1))
    
    if inventory_start <= 0:
        break # 库存卖光了就停止预测
        
    inventory_end = max(0, inventory_start - (daily_sales * 30))
    avg_inventory = (inventory_start + inventory_end) / 2
    
    # 仓储费计算
    storage_fee = avg_inventory * unit_volume * monthly_storage_fee_per_cuft
    
    # 低库存预警 (假设低于28天供应量)
    supply_days = inventory_start / daily_sales
    low_stock_penalty = 0
    if supply_days < 28 and inventory_start > 0:
        low_stock_penalty = inventory_start * low_stock_fee_per_unit
        
    # 老化库存预警 (假设超过181天的部分)
    aged_units = 0
    aged_penalty = 0
    if supply_days > 181:
        aged_units = inventory_start - (181 * daily_sales)
        aged_penalty = aged_units * aged_stock_fee_per_unit

    forecast_data.append({
        "月份": f"第 {month} 个月",
        "期初库存": int(inventory_start),
        "期末库存": int(inventory_end),
        "预估仓储费": round(storage_fee, 2),
        "低库存罚款风险": round(low_stock_penalty, 2),
        "老化库存罚款风险": round(aged_penalty, 2),
        "当月总仓储相关费用": round(storage_fee + low_stock_penalty + aged_penalty, 2)
    })

if forecast_data:
    df = pd.DataFrame(forecast_data)
    # 展示表格
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 展示图表（各月总费用）
    st.bar_chart(data=df, x="月份", y="当月总仓储相关费用", color="#ffaa00")
else:
    st.warning("当前库存不足以支撑一个月的销售，请尽快补货！")

st.markdown("---")
st.caption("💡 提示：您可以修改左侧侧边栏的数据，右侧的表格和图表会实时更新。")

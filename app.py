import streamlit as st

# 设置网页标题
st.title("📦 亚马逊费用与利润计算器")
st.write("请在下方输入你的产品数据，实时查看利润情况。")

# 创建左右两列布局
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 收入数据")
    price = st.number_input("产品售价 ($)", min_value=0.0, value=29.99, step=1.0)
    shipping = st.number_input("买家支付的运费 ($)", min_value=0.0, value=0.0, step=1.0)

with col2:
    st.subheader("💸 成本与费用")
    cost = st.number_input("产品成本 ($)", min_value=0.0, value=10.0, step=1.0)
    commission_rate = st.slider("销售佣金比例 (%)", min_value=0, max_value=30, value=15)
    fba_fee = st.number_input("FBA 配送费 ($)", min_value=0.0, value=5.0, step=0.5)
    # 这里把我们之前聊到的燃油附加费加进去（默认3.5%）
    fuel_surcharge_rate = st.slider("物流附加费率 (%)", min_value=0.0, max_value=10.0, value=3.5, step=0.1)

# 计算过程
# 总销售额
total_revenue = price + shipping
# 佣金费用
commission_fee = total_revenue * (commission_rate / 100)
# 附加费
fuel_fee = fba_fee * (fuel_surcharge_rate / 100)
# 总费用
total_fees = commission_fee + fba_fee + fuel_fee
# 净利润
net_profit = total_revenue - cost - total_fees
# 利润率
margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

st.markdown("---")
st.subheader("📊 计算结果")

# 展示核心数据卡片
m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("总销售额 (Revenue)", f"${total_revenue:.2f}")
m_col2.metric("净利润 (Net Profit)", f"${net_profit:.2f}", delta=f"{margin:.1f}% 利润率")
m_col3.metric("总费用 (Total Fees)", f"${total_fees:.2f}")

# 费用明细展示
with st.expander("查看费用明细"):
    st.write(f"- 销售佣金: **${commission_fee:.2f}**")
    st.write(f"- FBA 基础配送费: **${fba_fee:.2f}**")
    st.write(f"- 物流附加费 ({fuel_surcharge_rate}%): **${fuel_fee:.2f}**")
    st.write(f"- 产品成本: **${cost:.2f}**")

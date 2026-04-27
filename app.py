import os
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="利益管理表",
    page_icon="💼",
    layout="wide"
)

DATA_FILE = "transactions.csv"
PARTNER_RATE = 0.30
OWNER_RATE = 0.70

COLUMNS = [
    "日付", "項目名", "仕入れ値", "売値", "その他経費",
    "粗利", "配分対象利益", "はやと氏支払分30%",
    "オーナー手残り70%", "支払ステータス", "支払日", "メモ"
]

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #050816, #0f172a, #111827);
    color: #f8fafc;
}
[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.9);
    padding: 18px;
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.25);
}
h1, h2, h3 {
    color: #f8fafc;
}
</style>
""", unsafe_allow_html=True)


def yen(x):
    try:
        return f"¥{int(round(float(x))):,}"
    except:
        return "¥0"


def recalc(df):
    df = df.copy()

    for col in ["仕入れ値", "売値", "その他経費"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["粗利"] = df["売値"] - df["仕入れ値"]
    df["配分対象利益"] = df["粗利"] - df["その他経費"]
    df["はやと氏支払分30%"] = df["配分対象利益"] * PARTNER_RATE
    df["オーナー手残り70%"] = df["配分対象利益"] * OWNER_RATE

    if "支払ステータス" not in df.columns:
        df["支払ステータス"] = "未払"

    df["支払ステータス"] = df["支払ステータス"].fillna("未払")
    df.loc[~df["支払ステータス"].isin(["未払", "支払済"]), "支払ステータス"] = "未払"

    return df


def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=COLUMNS)

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    return recalc(df[COLUMNS])


def save_data(df):
    df = recalc(df)
    df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")


if "df" not in st.session_state:
    st.session_state.df = load_data()

st.title("💼 利益管理表")
st.caption("共同経営の売上・仕入・利益配分・支払管理を一括管理")

df = recalc(st.session_state.df)

with st.sidebar:
    st.header("取引を追加")

    input_date = st.date_input("日付", value=date.today())
    item_name = st.text_input("項目名")
    cost = st.number_input("仕入れ値", min_value=0, step=100)
    sale = st.number_input("売値", min_value=0, step=100)
    expense = st.number_input("その他経費", min_value=0, step=100)
    status = st.selectbox("支払ステータス", ["未払", "支払済"])
    pay_date = st.date_input("支払日", value=date.today())
    memo = st.text_area("メモ")

    gross = sale - cost
    target_profit = gross - expense
    partner_pay = target_profit * PARTNER_RATE
    owner_profit = target_profit * OWNER_RATE

    st.markdown("---")
    st.write(f"粗利：**{yen(gross)}**")
    st.write(f"配分対象利益：**{yen(target_profit)}**")
    st.write(f"はやと氏30%：**{yen(partner_pay)}**")
    st.write(f"自分70%：**{yen(owner_profit)}**")

    if st.button("登録する", use_container_width=True):
        if item_name.strip() == "":
            st.error("項目名を入力してください")
        else:
            new_row = pd.DataFrame([{
                "日付": input_date,
                "項目名": item_name,
                "仕入れ値": cost,
                "売値": sale,
                "その他経費": expense,
                "粗利": 0,
                "配分対象利益": 0,
                "はやと氏支払分30%": 0,
                "オーナー手残り70%": 0,
                "支払ステータス": status,
                "支払日": pay_date if status == "支払済" else "",
                "メモ": memo
            }])

            st.session_state.df = pd.concat([df, new_row], ignore_index=True)
            st.session_state.df = recalc(st.session_state.df)
            save_data(st.session_state.df)
            st.success("登録しました")
            st.rerun()


df = recalc(st.session_state.df)

total_sales = df["売値"].sum()
total_cost = df["仕入れ値"].sum()
total_expense = df["その他経費"].sum()
total_profit = df["配分対象利益"].sum()
total_partner = df["はやと氏支払分30%"].sum()
total_owner = df["オーナー手残り70%"].sum()

paid_partner = df[df["支払ステータス"] == "支払済"]["はやと氏支払分30%"].sum()
unpaid_partner = df[df["支払ステータス"] == "未払"]["はやと氏支払分30%"].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("累計売上", yen(total_sales))
c2.metric("累計仕入＋経費", yen(total_cost + total_expense))
c3.metric("はやと氏 未払", yen(unpaid_partner))
c4.metric("自分の手残り", yen(total_owner))

tab1, tab2, tab3, tab4 = st.tabs(["📊 ダッシュボード", "🧾 取引履歴", "🤝 支払管理", "⬇️ CSV"])

with tab1:
    if df.empty:
        st.info("まだデータがありません。左から取引を登録してください。")
    else:
        chart_df = df.copy()
        chart_df["日付"] = pd.to_datetime(chart_df["日付"], errors="coerce")
        chart_df["月"] = chart_df["日付"].dt.to_period("M").astype(str)

        monthly = chart_df.groupby("月", as_index=False).agg({
            "売値": "sum",
            "仕入れ値": "sum",
            "その他経費": "sum",
            "配分対象利益": "sum",
            "はやと氏支払分30%": "sum",
            "オーナー手残り70%": "sum"
        })

        fig1 = px.bar(
            monthly,
            x="月",
            y=["はやと氏支払分30%", "オーナー手残り70%"],
            title="月別 利益配分",
            barmode="stack"
        )
        fig1.update_layout(template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.line(
            monthly,
            x="月",
            y=["売値", "仕入れ値", "その他経費", "配分対象利益"],
            markers=True,
            title="月別 収支推移"
        )
        fig2.update_layout(template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("取引履歴の編集・削除")

    if df.empty:
        st.info("取引履歴がありません。")
    else:
        edit_df = df.copy()
        edit_df.insert(0, "削除", False)

        edited = st.data_editor(
            edit_df,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            column_config={
                "削除": st.column_config.CheckboxColumn("削除"),
                "支払ステータス": st.column_config.SelectboxColumn(
                    "支払ステータス",
                    options=["未払", "支払済"]
                ),
                "粗利": st.column_config.NumberColumn("粗利", disabled=True),
                "配分対象利益": st.column_config.NumberColumn("配分対象利益", disabled=True),
                "はやと氏支払分30%": st.column_config.NumberColumn("はやと氏支払分30%", disabled=True),
                "オーナー手残り70%": st.column_config.NumberColumn("オーナー手残り70%", disabled=True),
            }
        )

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("編集内容を保存", use_container_width=True):
                new_df = edited.drop(columns=["削除"])
                new_df = recalc(new_df)
                st.session_state.df = new_df
                save_data(new_df)
                st.success("保存しました")
                st.rerun()

        with col_b:
            if st.button("チェックした行を削除", use_container_width=True):
                new_df = edited[edited["削除"] == False].drop(columns=["削除"])
                new_df = recalc(new_df)
                st.session_state.df = new_df
                save_data(new_df)
                st.warning("削除しました")
                st.rerun()

with tab3:
    st.subheader("はやと氏への支払管理")

    c1, c2, c3 = st.columns(3)
    c1.metric("未払合計", yen(unpaid_partner))
    c2.metric("支払済合計", yen(paid_partner))
    c3.metric("累計支払予定", yen(total_partner))

    unpaid_df = df[df["支払ステータス"] == "未払"]

    st.markdown("### 未払一覧")
    if unpaid_df.empty:
        st.success("未払はありません")
    else:
        st.dataframe(unpaid_df, use_container_width=True, hide_index=True)

        if st.button("未払をすべて支払済みにする", use_container_width=True):
            df.loc[df["支払ステータス"] == "未払", "支払ステータス"] = "支払済"
            df.loc[df["支払日"].astype(str).isin(["", "nan", "NaT"]), "支払日"] = str(date.today())
            st.session_state.df = recalc(df)
            save_data(st.session_state.df)
            st.success("すべて支払済みにしました")
            st.rerun()

with tab4:
    st.subheader("CSVダウンロード")

    csv = df.to_csv(index=False, encoding="utf-8-sig")

    st.download_button(
        "CSVをダウンロード",
        data=csv,
        file_name="rieki_kanrihyou.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("計算式：粗利 = 売値 - 仕入れ値 / 配分対象利益 = 粗利 - その他経費 / はやと氏30% / 自分70%")

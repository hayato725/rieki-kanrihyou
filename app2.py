import os
import calendar
from datetime import date
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="利益管理表",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "transactions.csv"

HAYATO_RATE = 0.30
RIKU_RATE = 0.70

COLUMNS = [
    "日付",
    "仕入れ値",
    "売値",
    "その他経費",
    "配分対象利益",
    "はやと最終利益30%",
    "りく最終利益70%",
    "メモ",
]

st.markdown("""
<style>
[data-testid="stSidebar"] {
    display: none;
}

[data-testid="collapsedControl"] {
    display: none;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(59,130,246,0.18), transparent 30%),
        radial-gradient(circle at top right, rgba(168,85,247,0.14), transparent 28%),
        linear-gradient(135deg, #f8fbff 0%, #eef5ff 45%, #f7f0ff 100%);
    color: #111827;
}

.block-container {
    padding-top: 1.1rem;
    padding-bottom: 2rem;
}

h1, h2, h3, p, span, label, div {
    color: #111827;
}

.main-title {
    font-size: 2rem;
    font-weight: 950;
    letter-spacing: -0.04em;
    margin-bottom: 0.1rem;
}

.sub-title {
    color: #475569;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

.nav-box {
    background: rgba(255,255,255,0.92);
    border: 1px solid rgba(15,23,42,0.08);
    border-radius: 22px;
    padding: 14px;
    box-shadow: 0 14px 40px rgba(15,23,42,0.08);
    margin-bottom: 14px;
}

.metric-card {
    background: rgba(255,255,255,0.96);
    border: 1px solid rgba(15,23,42,0.08);
    border-radius: 24px;
    padding: 18px;
    box-shadow: 0 16px 38px rgba(15,23,42,0.10);
    min-height: 120px;
}

.metric-label {
    color: #475569;
    font-size: 0.82rem;
    font-weight: 800;
    margin-bottom: 0.45rem;
}

.metric-value {
    color: #0f172a;
    font-size: 1.9rem;
    font-weight: 950;
    letter-spacing: -0.04em;
    line-height: 1.05;
}

.metric-note {
    color: #64748b;
    font-size: 0.76rem;
    font-weight: 650;
    margin-top: 0.4rem;
}

.card-blue { border-left: 7px solid #2563eb; }
.card-green { border-left: 7px solid #16a34a; }
.card-pink { border-left: 7px solid #db2777; }
.card-purple { border-left: 7px solid #7c3aed; }

.panel {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(15,23,42,0.08);
    border-radius: 24px;
    padding: 18px;
    box-shadow: 0 16px 38px rgba(15,23,42,0.08);
    margin-top: 12px;
}

.calc-box {
    background: linear-gradient(135deg, #ecfdf5, #ffffff);
    border: 1px solid rgba(22,163,74,0.18);
    border-radius: 18px;
    padding: 14px;
    margin: 10px 0;
    font-weight: 800;
}

.calc-box strong {
    color: #065f46;
    font-size: 1.05rem;
}

.calendar-wrap {
    overflow-x: auto;
    margin-top: 12px;
}

.calendar-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 8px;
    min-width: 720px;
}

.calendar-table th {
    color: #334155;
    font-weight: 950;
    text-align: center;
    padding: 7px;
}

.calendar-cell {
    vertical-align: top;
    background: #ffffff;
    border: 1px solid rgba(15,23,42,0.08);
    border-radius: 18px;
    padding: 10px;
    height: 122px;
    min-height: 122px;
    box-shadow: 0 10px 24px rgba(15,23,42,0.06);
}

.calendar-plus {
    background: linear-gradient(180deg, #ffffff, #ecfdf5);
    border-left: 6px solid #22c55e;
}

.calendar-minus {
    background: linear-gradient(180deg, #ffffff, #fef2f2);
    border-left: 6px solid #ef4444;
}

.calendar-other {
    opacity: 0.22;
    background: #e2e8f0;
}

.calendar-day {
    font-size: 1rem;
    font-weight: 950;
    color: #0f172a;
    margin-bottom: 7px;
}

.calendar-count {
    font-size: 0.76rem;
    color: #475569;
    font-weight: 850;
}

.calendar-sales {
    font-size: 0.75rem;
    color: #2563eb;
    font-weight: 850;
}

.calendar-profit-plus {
    font-size: 0.75rem;
    color: #15803d;
    font-weight: 950;
}

.calendar-profit-minus {
    font-size: 0.75rem;
    color: #dc2626;
    font-weight: 950;
}

.calendar-empty {
    font-size: 0.74rem;
    color: #94a3b8;
    font-weight: 750;
}

div[data-testid="stDataFrame"],
div[data-testid="stDataEditor"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(15,23,42,0.08);
    box-shadow: 0 12px 30px rgba(15,23,42,0.07);
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 16px;
    min-height: 48px;
    font-weight: 950;
}

.stButton > button {
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    color: white;
    border: none;
}

input, textarea {
    color: #111827 !important;
}

@media (max-width: 768px) {
    .main-title {
        font-size: 1.45rem;
    }

    .metric-card {
        padding: 14px;
        min-height: 105px;
    }

    .metric-value {
        font-size: 1.45rem;
    }

    .calendar-table {
        min-width: 680px;
    }
}
</style>
""", unsafe_allow_html=True)


def yen(value):
    try:
        return f"¥{int(round(float(value))):,}"
    except Exception:
        return "¥0"


def recalc(df):
    df = df.copy()

    if "はやと氏支払分30%" in df.columns and "はやと最終利益30%" not in df.columns:
        df["はやと最終利益30%"] = df["はやと氏支払分30%"]

    if "オーナー手残り70%" in df.columns and "りく最終利益70%" not in df.columns:
        df["りく最終利益70%"] = df["オーナー手残り70%"]

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    for col in ["仕入れ値", "売値", "その他経費"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["配分対象利益"] = df["売値"] - df["仕入れ値"] - df["その他経費"]
    df["はやと最終利益30%"] = df["配分対象利益"] * HAYATO_RATE
    df["りく最終利益70%"] = df["配分対象利益"] * RIKU_RATE

    df["日付"] = pd.to_datetime(df["日付"], errors="coerce").dt.date
    df["メモ"] = df["メモ"].fillna("")

    return df[COLUMNS]


def load_data():
    if os.path.exists(DATA_FILE):
        return recalc(pd.read_csv(DATA_FILE))
    return pd.DataFrame(columns=COLUMNS)


def save_data(df):
    save_df = recalc(df).copy()
    save_df["日付"] = pd.to_datetime(save_df["日付"], errors="coerce").dt.strftime("%Y-%m-%d")
    save_df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")


def metric_card(label, value, note, color_class):
    return f"""
    <div class="metric-card {color_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """


def build_calendar_html(df, year, month):
    temp = df.copy()
    temp["日付"] = pd.to_datetime(temp["日付"], errors="coerce").dt.date
    temp = temp.dropna(subset=["日付"])

    daily_map = {}

    if not temp.empty:
        daily = temp.groupby("日付", as_index=False).agg(
            件数=("日付", "size"),
            売値=("売値", "sum"),
            利益=("配分対象利益", "sum"),
            はやと=("はやと最終利益30%", "sum"),
            りく=("りく最終利益70%", "sum"),
        )
        daily_map = {row["日付"]: row for _, row in daily.iterrows()}

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)
    names = ["日", "月", "火", "水", "木", "金", "土"]

    html = '<div class="calendar-wrap"><table class="calendar-table">'
    html += "<thead><tr>"
    for n in names:
        html += f"<th>{n}</th>"
    html += "</tr></thead><tbody>"

    for week in weeks:
        html += "<tr>"
        for day in week:
            if day.month != month:
                html += '<td class="calendar-cell calendar-other"></td>'
                continue

            if day in daily_map:
                row = daily_map[day]
                profit = float(row["利益"])
                cell_class = "calendar-plus" if profit >= 0 else "calendar-minus"
                profit_class = "calendar-profit-plus" if profit >= 0 else "calendar-profit-minus"

                html += f"""
                <td class="calendar-cell {cell_class}">
                    <div class="calendar-day">{day.day}</div>
                    <div class="calendar-count">{int(row["件数"])}件</div>
                    <div class="calendar-sales">売上 {yen(row["売値"])}</div>
                    <div class="{profit_class}">利益 {yen(row["利益"])}</div>
                    <div class="calendar-profit-plus">はやと {yen(row["はやと"])}</div>
                    <div class="calendar-profit-plus">りく {yen(row["りく"])}</div>
                </td>
                """
            else:
                html += f"""
                <td class="calendar-cell">
                    <div class="calendar-day">{day.day}</div>
                    <div class="calendar-empty">取引なし</div>
                </td>
                """
        html += "</tr>"

    html += "</tbody></table></div>"
    return html


if "df" not in st.session_state:
    st.session_state.df = load_data()

df = recalc(st.session_state.df)

st.markdown('<div class="main-title">💼 利益管理表</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">左メニューなし。スマホで上から選んで管理する版。</div>', unsafe_allow_html=True)

st.markdown('<div class="nav-box">', unsafe_allow_html=True)
page = st.selectbox(
    "画面を選ぶ",
    [
        "🏠 ホーム",
        "➕ 取引追加",
        "📅 カレンダー",
        "🧾 取引一覧",
        "📆 月別集計",
        "⬇️ CSV",
    ]
)
st.markdown('</div>', unsafe_allow_html=True)

total_sales = df["売値"].sum()
total_cost = df["仕入れ値"].sum()
total_expense = df["その他経費"].sum()
total_profit = df["配分対象利益"].sum()
total_hayato = df["はやと最終利益30%"].sum()
total_riku = df["りく最終利益70%"].sum()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(metric_card("累計売上", yen(total_sales), "全部の売上", "card-blue"), unsafe_allow_html=True)

with c2:
    st.markdown(metric_card("仕入 + 経費", yen(total_cost + total_expense), f"仕入 {yen(total_cost)} / 経費 {yen(total_expense)}", "card-purple"), unsafe_allow_html=True)

with c3:
    st.markdown(metric_card("はやと 最終利益", yen(total_hayato), "利益の30%", "card-green"), unsafe_allow_html=True)

with c4:
    st.markdown(metric_card("りく 最終利益", yen(total_riku), "利益の70%", "card-pink"), unsafe_allow_html=True)


if page == "🏠 ホーム":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("すぐ入力")

    with st.form("quick_input", clear_on_submit=True):
        input_date = st.date_input("日付", value=date.today())
        cost = st.number_input("仕入れ値", min_value=0, step=100)
        sale = st.number_input("売値", min_value=0, step=100)
        expense = st.number_input("その他経費", min_value=0, step=100)
        memo = st.text_area("メモ", placeholder="商品名・相手・支払い方法など")

        profit = sale - cost - expense
        hayato = profit * HAYATO_RATE
        riku = profit * RIKU_RATE

        st.markdown(
            f"""
            <div class="calc-box">
                配分対象利益：<strong>{yen(profit)}</strong><br>
                はやと：<strong>{yen(hayato)}</strong><br>
                りく：<strong>{yen(riku)}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )

        submit = st.form_submit_button("登録する", use_container_width=True)

        if submit:
            new_row = pd.DataFrame([{
                "日付": input_date,
                "仕入れ値": cost,
                "売値": sale,
                "その他経費": expense,
                "配分対象利益": 0,
                "はやと最終利益30%": 0,
                "りく最終利益70%": 0,
                "メモ": memo,
            }])
            st.session_state.df = recalc(pd.concat([df, new_row], ignore_index=True))
            save_data(st.session_state.df)
            st.success("登録しました。")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("最近の取引")
    if df.empty:
        st.info("まだ取引がありません。")
    else:
        st.dataframe(df.sort_values("日付", ascending=False).head(8), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


elif page == "➕ 取引追加":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("取引追加")

    with st.form("main_input", clear_on_submit=True):
        input_date = st.date_input("日付", value=date.today())
        cost = st.number_input("仕入れ値", min_value=0, step=100)
        sale = st.number_input("売値", min_value=0, step=100)
        expense = st.number_input("その他経費", min_value=0, step=100)
        memo = st.text_area("メモ", placeholder="商品名・相手・支払い方法など")

        profit = sale - cost - expense
        hayato = profit * HAYATO_RATE
        riku = profit * RIKU_RATE

        st.markdown(
            f"""
            <div class="calc-box">
                配分対象利益：<strong>{yen(profit)}</strong><br>
                はやと：<strong>{yen(hayato)}</strong><br>
                りく：<strong>{yen(riku)}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )

        submit = st.form_submit_button("登録する", use_container_width=True)

        if submit:
            new_row = pd.DataFrame([{
                "日付": input_date,
                "仕入れ値": cost,
                "売値": sale,
                "その他経費": expense,
                "配分対象利益": 0,
                "はやと最終利益30%": 0,
                "りく最終利益70%": 0,
                "メモ": memo,
            }])
            st.session_state.df = recalc(pd.concat([df, new_row], ignore_index=True))
            save_data(st.session_state.df)
            st.success("登録しました。")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


elif page == "📅 カレンダー":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("カレンダー")

    if df["日付"].dropna().empty:
        current_year = date.today().year
        current_month = date.today().month
    else:
        last_date = max(df["日付"].dropna())
        current_year = last_date.year
        current_month = last_date.month

    y_options = list(range(date.today().year - 3, date.today().year + 4))

    col_y, col_m = st.columns(2)
    with col_y:
        selected_year = st.selectbox("年", y_options, index=y_options.index(current_year))
    with col_m:
        selected_month = st.selectbox("月", list(range(1, 13)), index=current_month - 1)

    month_df = df.copy()
    month_df["日付"] = pd.to_datetime(month_df["日付"], errors="coerce").dt.date
    month_df = month_df[
        month_df["日付"].apply(
            lambda x: x.year == selected_year and x.month == selected_month if pd.notnull(x) else False
        )
    ]

    a, b, c, d = st.columns(4)
    a.metric("件数", f"{len(month_df)}件")
    b.metric("売上", yen(month_df["売値"].sum()))
    c.metric("はやと", yen(month_df["はやと最終利益30%"].sum()))
    d.metric("りく", yen(month_df["りく最終利益70%"].sum()))

    st.markdown(build_calendar_html(month_df, selected_year, selected_month), unsafe_allow_html=True)

    if not month_df.empty:
        st.subheader("日付別の詳細")
        days = sorted(month_df["日付"].dropna().unique(), reverse=True)
        selected_day = st.selectbox("日付", days, format_func=lambda x: x.strftime("%Y-%m-%d"))
        day_df = month_df[month_df["日付"] == selected_day]

        x1, x2, x3 = st.columns(3)
        x1.metric("利益", yen(day_df["配分対象利益"].sum()))
        x2.metric("はやと", yen(day_df["はやと最終利益30%"].sum()))
        x3.metric("りく", yen(day_df["りく最終利益70%"].sum()))

        st.dataframe(day_df, use_container_width=True, hide_index=True)
    else:
        st.info("この月はまだ取引なし。")

    st.markdown('</div>', unsafe_allow_html=True)


elif page == "🧾 取引一覧":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("取引一覧・編集・削除")

    if df.empty:
        st.info("まだ取引がありません。")
    else:
        edit_df = df.sort_values("日付", ascending=False).copy()
        edit_df.insert(0, "削除", False)

        edited = st.data_editor(
            edit_df,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            column_config={
                "削除": st.column_config.CheckboxColumn("削除"),
                "日付": st.column_config.DateColumn("日付"),
                "仕入れ値": st.column_config.NumberColumn("仕入れ値", format="¥%d"),
                "売値": st.column_config.NumberColumn("売値", format="¥%d"),
                "その他経費": st.column_config.NumberColumn("その他経費", format="¥%d"),
                "配分対象利益": st.column_config.NumberColumn("配分対象利益", format="¥%d", disabled=True),
                "はやと最終利益30%": st.column_config.NumberColumn("はやと最終利益30%", format="¥%d", disabled=True),
                "りく最終利益70%": st.column_config.NumberColumn("りく最終利益70%", format="¥%d", disabled=True),
                "メモ": st.column_config.TextColumn("メモ"),
            }
        )

        b1, b2 = st.columns(2)

        with b1:
            if st.button("編集を保存", use_container_width=True):
                new_df = edited.drop(columns=["削除"])
                st.session_state.df = recalc(new_df)
                save_data(st.session_state.df)
                st.success("保存しました。")
                st.rerun()

        with b2:
            if st.button("削除する", use_container_width=True):
                new_df = edited[edited["削除"] == False].drop(columns=["削除"])
                st.session_state.df = recalc(new_df)
                save_data(st.session_state.df)
                st.warning("削除しました。")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


elif page == "📆 月別集計":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("月別集計")

    if df.empty:
        st.info("まだデータがありません。")
    else:
        temp = df.copy()
        temp["日付"] = pd.to_datetime(temp["日付"], errors="coerce")
        temp["月"] = temp["日付"].dt.to_period("M").astype(str)

        monthly = temp.groupby("月", as_index=False).agg(
            件数=("日付", "size"),
            売上=("売値", "sum"),
            仕入れ=("仕入れ値", "sum"),
            経費=("その他経費", "sum"),
            利益=("配分対象利益", "sum"),
            はやと=("はやと最終利益30%", "sum"),
            りく=("りく最終利益70%", "sum"),
        ).sort_values("月", ascending=False)

        st.dataframe(monthly, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)


elif page == "⬇️ CSV":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("CSV・バックアップ")

    csv = df.to_csv(index=False, encoding="utf-8-sig")

    st.download_button(
        "CSVをダウンロード",
        data=csv,
        file_name="rieki_kanrihyou_backup.csv",
        mime="text/csv",
        use_container_width=True
    )

    uploaded = st.file_uploader("CSVを読み込む", type=["csv"])

    if uploaded is not None:
        imported = pd.read_csv(uploaded)
        st.session_state.df = recalc(imported)
        save_data(st.session_state.df)
        st.success("読み込みました。")
        st.rerun()

    st.dataframe(df.sort_values("日付", ascending=False), use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("配分対象利益 = 売値 - 仕入れ値 - その他経費 / はやと30% / りく70%")

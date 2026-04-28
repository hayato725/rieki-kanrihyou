import os
from datetime import date
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="かんたん収支管理",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_FILE = "kantan_shushi_data.csv"

HAYATO_RATE = 0.40
RIKU_RATE = 0.60

COLUMNS = [
    "日付",
    "名前",
    "場所",
    "元グラム",
    "売却グラム",
    "仕入れ金額",
    "売上金額",
    "その他経費",
    "利益",
    "はやと40%",
    "りく60%",
    "残グラム",
    "メモ",
]

st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(59,130,246,.16), transparent 32%),
        radial-gradient(circle at top right, rgba(34,197,94,.15), transparent 30%),
        linear-gradient(135deg, #f8fbff 0%, #eef7ff 48%, #f7fff3 100%);
    color: #0f172a;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

h1, h2, h3, p, div, span, label {
    color: #0f172a;
}

.title {
    font-size: 2rem;
    font-weight: 950;
    letter-spacing: -0.05em;
    margin-bottom: 0.1rem;
}

.subtitle {
    color: #475569;
    font-size: 0.92rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.nav {
    background: rgba(255,255,255,.94);
    border: 1px solid rgba(15,23,42,.08);
    border-radius: 22px;
    padding: 14px;
    box-shadow: 0 14px 38px rgba(15,23,42,.08);
    margin-bottom: 14px;
}

.panel {
    background: rgba(255,255,255,.96);
    border: 1px solid rgba(15,23,42,.08);
    border-radius: 26px;
    padding: 18px;
    box-shadow: 0 18px 45px rgba(15,23,42,.10);
    margin-bottom: 14px;
}

.input-panel {
    background: linear-gradient(135deg, #ffffff 0%, #eff6ff 100%);
    border: 1px solid rgba(37,99,235,.14);
    border-radius: 28px;
    padding: 18px;
    box-shadow: 0 20px 55px rgba(15,23,42,.12);
    margin-bottom: 14px;
}

.metric-card {
    background: rgba(255,255,255,.96);
    border: 1px solid rgba(15,23,42,.08);
    border-radius: 22px;
    padding: 15px;
    box-shadow: 0 14px 34px rgba(15,23,42,.09);
    min-height: 105px;
}

.metric-label {
    color: #475569;
    font-size: .80rem;
    font-weight: 850;
    margin-bottom: .35rem;
}

.metric-value {
    color: #0f172a;
    font-size: 1.55rem;
    font-weight: 950;
    letter-spacing: -0.045em;
    line-height: 1.05;
}

.metric-note {
    color: #64748b;
    font-size: .72rem;
    font-weight: 700;
    margin-top: .35rem;
}

.blue { border-left: 7px solid #2563eb; }
.green { border-left: 7px solid #16a34a; }
.pink { border-left: 7px solid #db2777; }
.orange { border-left: 7px solid #f97316; }
.purple { border-left: 7px solid #7c3aed; }
.gray { border-left: 7px solid #64748b; }

.calc-box {
    background: linear-gradient(135deg, #ecfdf5, #ffffff);
    border: 1px solid rgba(22,163,74,.22);
    border-radius: 20px;
    padding: 14px;
    margin: 10px 0 16px 0;
    font-weight: 900;
}

.calc-row {
    display: flex;
    justify-content: space-between;
    border-bottom: 1px solid #dcfce7;
    padding: 7px 0;
    gap: 16px;
}

.calc-row:last-child {
    border-bottom: none;
}

.calc-row span {
    color: #334155;
    white-space: nowrap;
}

.calc-row strong {
    color: #065f46;
    font-size: 1.05rem;
    text-align: right;
}

.record-card {
    background: #ffffff;
    border: 1px solid rgba(15,23,42,.08);
    border-radius: 20px;
    padding: 14px;
    box-shadow: 0 12px 28px rgba(15,23,42,.08);
    margin-bottom: 10px;
}

.record-top {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 8px;
    margin-bottom: 8px;
}

.record-name {
    font-weight: 950;
    font-size: 1rem;
    color: #0f172a;
}

.record-date {
    font-weight: 800;
    color: #64748b;
    font-size: .82rem;
    white-space: nowrap;
}

.record-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 7px 12px;
}

.record-item {
    font-size: .82rem;
    color: #334155;
}

.record-item strong {
    color: #0f172a;
}

.stButton > button {
    border-radius: 16px;
    min-height: 50px;
    font-weight: 950;
    border: 0;
    color: white;
    background: linear-gradient(90deg, #2563eb, #16a34a);
}

.stDownloadButton > button {
    border-radius: 16px;
    min-height: 48px;
    font-weight: 950;
}

div[data-testid="stDataFrame"],
div[data-testid="stDataEditor"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(15,23,42,.08);
    box-shadow: 0 12px 30px rgba(15,23,42,.08);
}

input, textarea {
    color: #0f172a !important;
}

@media (max-width: 768px) {
    .title { font-size: 1.45rem; }
    .metric-value { font-size: 1.22rem; }
    .metric-card { padding: 12px; min-height: 95px; }
    .panel, .input-panel { padding: 14px; border-radius: 22px; }
    .record-grid { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)


def yen(value):
    try:
        return f"¥{int(round(float(value))):,}"
    except Exception:
        return "¥0"


def gram(value):
    try:
        return f"{float(value):g}g"
    except Exception:
        return "0g"


def recalc(df):
    df = df.copy()

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    for col in ["元グラム", "売却グラム", "仕入れ金額", "売上金額", "その他経費"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["利益"] = df["売上金額"] - df["仕入れ金額"] - df["その他経費"]
    df["はやと40%"] = df["利益"] * HAYATO_RATE
    df["りく60%"] = df["利益"] * RIKU_RATE
    df["残グラム"] = df["元グラム"] - df["売却グラム"]

    df["日付"] = pd.to_datetime(df["日付"], errors="coerce").dt.date
    df["名前"] = df["名前"].fillna("")
    df["場所"] = df["場所"].fillna("")
    df["メモ"] = df["メモ"].fillna("")

    return df[COLUMNS]


def load_data():
    if os.path.exists(DATA_FILE):
        return recalc(pd.read_csv(DATA_FILE))
    return pd.DataFrame(columns=COLUMNS)


def save_data(df):
    out = recalc(df).copy()
    out["日付"] = pd.to_datetime(out["日付"], errors="coerce").dt.strftime("%Y-%m-%d")
    out.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")


def metric_card(label, value, note="", color="blue"):
    return f"""
    <div class="metric-card {color}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """


def summary_cards(target_df, title):
    total_sales = target_df["売上金額"].sum()
    total_cost = target_df["仕入れ金額"].sum()
    total_expense = target_df["その他経費"].sum()
    total_profit = target_df["利益"].sum()
    total_hayato = target_df["はやと40%"].sum()
    total_riku = target_df["りく60%"].sum()

    total_base_g = target_df["元グラム"].sum()
    total_sold_g = target_df["売却グラム"].sum()
    total_left_g = target_df["残グラム"].sum()

    st.subheader(title)

    a, b, c = st.columns(3)
    with a:
        st.markdown(metric_card("総売上", yen(total_sales), "売れた金額の合計", "blue"), unsafe_allow_html=True)
    with b:
        st.markdown(metric_card("総仕入れ", yen(total_cost), "仕入れた金額の合計", "orange"), unsafe_allow_html=True)
    with c:
        st.markdown(metric_card("その他経費", yen(total_expense), "送料・手数料など", "gray"), unsafe_allow_html=True)

    d, e, f = st.columns(3)
    with d:
        st.markdown(metric_card("合計利益", yen(total_profit), "売上−仕入れ−経費", "green"), unsafe_allow_html=True)
    with e:
        st.markdown(metric_card("はやと 40%", yen(total_hayato), "利益から自動計算", "pink"), unsafe_allow_html=True)
    with f:
        st.markdown(metric_card("りく 60%", yen(total_riku), "残りの取り分", "purple"), unsafe_allow_html=True)

    g, h, i = st.columns(3)
    with g:
        st.markdown(metric_card("元グラム合計", gram(total_base_g), "元の合計", "blue"), unsafe_allow_html=True)
    with h:
        st.markdown(metric_card("売却グラム合計", gram(total_sold_g), "売れた量の合計", "green"), unsafe_allow_html=True)
    with i:
        st.markdown(metric_card("残グラム合計", gram(total_left_g), "元g−売却g", "orange"), unsafe_allow_html=True)


def record_cards(target_df, limit=50):
    show_df = target_df.sort_values("日付", ascending=False).head(limit)

    for _, row in show_df.iterrows():
        name = row["名前"] if str(row["名前"]).strip() else "名前なし"
        place = row["場所"] if str(row["場所"]).strip() else "場所なし"
        memo = row["メモ"] if str(row["メモ"]).strip() else "メモなし"
        date_text = row["日付"].strftime("%Y-%m-%d") if pd.notnull(row["日付"]) else ""

        st.markdown(
            f"""
            <div class="record-card">
                <div class="record-top">
                    <div>
                        <div class="record-name">{name}</div>
                        <div class="record-item">{place}</div>
                    </div>
                    <div class="record-date">{date_text}</div>
                </div>
                <div class="record-grid">
                    <div class="record-item">元g：<strong>{gram(row["元グラム"])}</strong></div>
                    <div class="record-item">売却g：<strong>{gram(row["売却グラム"])}</strong></div>
                    <div class="record-item">仕入れ：<strong>{yen(row["仕入れ金額"])}</strong></div>
                    <div class="record-item">売上：<strong>{yen(row["売上金額"])}</strong></div>
                    <div class="record-item">経費：<strong>{yen(row["その他経費"])}</strong></div>
                    <div class="record-item">利益：<strong>{yen(row["利益"])}</strong></div>
                    <div class="record-item">はやと40%：<strong>{yen(row["はやと40%"])}</strong></div>
                    <div class="record-item">りく60%：<strong>{yen(row["りく60%"])}</strong></div>
                    <div class="record-item">残g：<strong>{gram(row["残グラム"])}</strong></div>
                    <div class="record-item">メモ：<strong>{memo}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


if "df" not in st.session_state:
    st.session_state.df = load_data()

df = recalc(st.session_state.df)

st.markdown('<div class="title">💰 かんたん収支管理</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">1回ごとの記録を残して、日付ごとに売上・仕入れ・利益・はやと40%・りく60%を自動集計。</div>',
    unsafe_allow_html=True
)

st.markdown('<div class="nav">', unsafe_allow_html=True)
page = st.selectbox(
    "画面を選ぶ",
    ["入力", "今日のまとめ", "日付別まとめ", "細かい記録", "編集・削除", "CSV"],
)
st.markdown('</div>', unsafe_allow_html=True)

summary_cards(df, "全体の合計")


if page == "入力":
    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    st.subheader("1回分を入力")

    with st.form("input_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            input_date = st.date_input("日付", value=date.today())
            name = st.text_input("名前", placeholder="例：Aさん、山田さんなど")
            place = st.text_input("場所", placeholder="例：施設名、エリア名など")
        with c2:
            base_g = st.number_input("元グラム", min_value=0.0, step=0.01, format="%.2f")
            sold_g = st.number_input("売却グラム", min_value=0.0, step=0.01, format="%.2f")
            expense = st.number_input("その他経費", min_value=0, step=100)

        c3, c4 = st.columns(2)
        with c3:
            cost = st.number_input("仕入れ金額", min_value=0, step=100)
        with c4:
            sale = st.number_input("売上金額", min_value=0, step=100)

        memo = st.text_input("メモ", placeholder="必要ならメモ")

        profit = sale - cost - expense
        hayato = profit * HAYATO_RATE
        riku = profit * RIKU_RATE
        left_g = base_g - sold_g

        st.markdown(
            f"""
            <div class="calc-box">
                <div class="calc-row"><span>利益</span><strong>{yen(profit)}</strong></div>
                <div class="calc-row"><span>はやと 40%</span><strong>{yen(hayato)}</strong></div>
                <div class="calc-row"><span>りく 60%</span><strong>{yen(riku)}</strong></div>
                <div class="calc-row"><span>残グラム</span><strong>{gram(left_g)}</strong></div>
            </div>
            """,
            unsafe_allow_html=True
        )

        submitted = st.form_submit_button("この内容を記録する", use_container_width=True)

        if submitted:
            new_row = pd.DataFrame([{
                "日付": input_date,
                "名前": name,
                "場所": place,
                "元グラム": base_g,
                "売却グラム": sold_g,
                "仕入れ金額": cost,
                "売上金額": sale,
                "その他経費": expense,
                "利益": 0,
                "はやと40%": 0,
                "りく60%": 0,
                "残グラム": 0,
                "メモ": memo,
            }])

            st.session_state.df = recalc(pd.concat([df, new_row], ignore_index=True))
            save_data(st.session_state.df)
            st.success("記録しました。")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("最近の細かい記録")
    if df.empty:
        st.info("まだ記録がありません。")
    else:
        record_cards(df, limit=8)
    st.markdown('</div>', unsafe_allow_html=True)


elif page == "今日のまとめ":
    today_df = df[df["日付"] == date.today()].copy()

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    if today_df.empty:
        st.info("今日の記録はまだありません。")
    else:
        summary_cards(today_df, "今日の合計")
        st.markdown("### 今日の細かい記録")
        record_cards(today_df, limit=50)
    st.markdown('</div>', unsafe_allow_html=True)


elif page == "日付別まとめ":
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    if df.empty:
        st.info("まだ記録がありません。")
    else:
        available_dates = sorted(df["日付"].dropna().unique(), reverse=True)
        selected_day = st.selectbox(
            "見たい日付を選ぶ",
            available_dates,
            format_func=lambda x: x.strftime("%Y-%m-%d")
        )

        day_df = df[df["日付"] == selected_day].copy()
        summary_cards(day_df, f"{selected_day.strftime('%Y-%m-%d')} の合計")

        st.markdown("### その日の細かい記録")
        record_cards(day_df, limit=100)

    st.markdown('</div>', unsafe_allow_html=True)


elif page == "細かい記録":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("1回ごとの細かい記録")

    if df.empty:
        st.info("まだ記録がありません。")
    else:
        record_cards(df, limit=200)

    st.markdown('</div>', unsafe_allow_html=True)


elif page == "編集・削除":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("編集・削除")

    if df.empty:
        st.info("まだ記録がありません。")
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
                "名前": st.column_config.TextColumn("名前"),
                "場所": st.column_config.TextColumn("場所"),
                "元グラム": st.column_config.NumberColumn("元グラム", format="%.2f"),
                "売却グラム": st.column_config.NumberColumn("売却グラム", format="%.2f"),
                "仕入れ金額": st.column_config.NumberColumn("仕入れ金額", format="¥%d"),
                "売上金額": st.column_config.NumberColumn("売上金額", format="¥%d"),
                "その他経費": st.column_config.NumberColumn("その他経費", format="¥%d"),
                "利益": st.column_config.NumberColumn("利益", format="¥%d", disabled=True),
                "はやと40%": st.column_config.NumberColumn("はやと40%", format="¥%d", disabled=True),
                "りく60%": st.column_config.NumberColumn("りく60%", format="¥%d", disabled=True),
                "残グラム": st.column_config.NumberColumn("残グラム", format="%.2f", disabled=True),
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
            if st.button("チェックした行を削除", use_container_width=True):
                new_df = edited[edited["削除"] == False].drop(columns=["削除"])
                st.session_state.df = recalc(new_df)
                save_data(st.session_state.df)
                st.warning("削除しました。")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


elif page == "CSV":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("CSV保存・読み込み")

    csv = df.to_csv(index=False, encoding="utf-8-sig")

    st.download_button(
        "CSVをダウンロード",
        data=csv,
        file_name="kantan_shushi_kanri.csv",
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

st.caption("計算式：利益 = 売上金額 − 仕入れ金額 − その他経費 / はやと = 利益の40% / りく = 利益の60% / 残グラム = 元グラム − 売却グラム")

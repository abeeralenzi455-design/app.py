# app.py
# WIQAA | وِقاء
# AI-Powered Residency Compliance Platform
# Hackathon Prototype — Enhanced Edition
# Demo data only — not real records

import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="وِقاء | WIQAA",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# STYLE
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Tajawal', 'Segoe UI', sans-serif;
}
.main { background-color: #f6f8fb; }
.block-container { padding-top: 1.6rem; }

.wiqaa-title {
    font-size: 44px;
    font-weight: 800;
    margin-bottom: 0;
    color: #101828;
}
.wiqaa-subtitle {
    color: #667085;
    font-size: 17px;
    margin-top: 4px;
}
.badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    background: #eef2ff;
    color: #3730a3;
    font-size: 13px;
    font-weight: 700;
    margin: 3px;
    border: 1px solid #e0e7ff;
}
.badge-arrow { color: #98a2b3; font-size: 13px; margin: 0 2px; }

.metric-card {
    padding: 18px 20px;
    border-radius: 16px;
    background: white;
    border: 1px solid #eaecf0;
    box-shadow: 0 1px 2px rgba(16,24,40,0.04);
}
.alert-card {
    padding: 16px 18px;
    border-radius: 14px;
    background: #fff7ed;
    border: 1px solid #fed7aa;
}
.danger-card {
    padding: 16px 18px;
    border-radius: 14px;
    background: #fef2f2;
    border: 1px solid #fecaca;
}
.success-card {
    padding: 16px 18px;
    border-radius: 14px;
    background: #ecfdf3;
    border: 1px solid #abefc6;
}
.info-card {
    padding: 16px 18px;
    border-radius: 14px;
    background: #eff8ff;
    border: 1px solid #b9e6fe;
}
[data-testid="stMetricValue"] { font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "notifications" not in st.session_state:
    st.session_state.notifications = []

# --------------------------------------------------
# DEMO DATA
# --------------------------------------------------
@st.cache_data
def build_demo_data():
    today = date.today()
    np.random.seed(42)

    n = 14
    names = [f"وافد {str(i+1).zfill(3)}" for i in range(n)]
    case_ids = [f"WQ-{1001 + i}" for i in range(n)]
    residency_types = np.random.choice(
        ["عمل", "زيارة", "إقامة مميزة", "عمل منزلي"],
        size=n, p=[0.55, 0.2, 0.1, 0.15]
    )
    sectors = np.random.choice(
        ["قطاع خاص", "قطاع حكومي", "أعمال منزلية", "غير مصنف"],
        size=n, p=[0.5, 0.15, 0.15, 0.2]
    )
    offsets = [5, 12, 25, 45, 75, -3, 8, -10, 2, 18, 60, -1, 33, 90]
    expiry_dates = [today + timedelta(days=o) for o in offsets]
    processing_time = [1.2, 0.8, 0.5, 0.2, 0.1, 4.8, 1.7, 6.1,
                        0.9, 1.1, 0.3, 5.4, 0.6, 0.2]
    channels = np.random.choice(
        ["رسالة نصية", "بريد إلكتروني", "تطبيق الجوال"], size=n
    )

    df = pd.DataFrame({
        "رقم الحالة": case_ids,
        "الاسم": names,
        "الجهة/القطاع": sectors,
        "نوع الإقامة": residency_types,
        "تاريخ الانتهاء": expiry_dates,
        "زمن المعالجة": processing_time,
        "قناة التواصل": channels,
    })
    df["الأيام المتبقية"] = (
        pd.to_datetime(df["تاريخ الانتهاء"]) - pd.Timestamp(today)
    ).dt.days

    def status_from_days(d):
        if d < 0:
            return "منتهية"
        elif d <= 7:
            return "تنبيه عاجل"
        elif d <= 14:
            return "متابعة"
        elif d <= 30:
            return "تنبيه مبكر"
        else:
            return "مستقرة"

    df["حالة الإجراء"] = df["الأيام المتبقية"].apply(status_from_days)
    return df

data = build_demo_data()

# --------------------------------------------------
# RISK ENGINE
# --------------------------------------------------
def calculate_risk(days):
    if days < 0:
        return 100
    elif days <= 7:
        return 90
    elif days <= 14:
        return 75
    elif days <= 30:
        return 50
    elif days <= 60:
        return 25
    else:
        return 10

data["درجة الأولوية"] = data["الأيام المتبقية"].apply(calculate_risk)

STATUS_COLORS = {
    "منتهية": "#d92d20",
    "تنبيه عاجل": "#f79009",
    "متابعة": "#fac515",
    "تنبيه مبكر": "#2e90fa",
    "مستقرة": "#12b76a",
}

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.markdown("## 🛡️ وِقاء")
st.sidebar.caption("WIQAA | Immigration Compliance Intelligence")

page = st.sidebar.radio(
    "القائمة الرئيسية",
    [
        "🏠 لوحة التحكم",
        "👤 سجل الوافدين",
        "🔮 التنبؤ بانتهاء الإقامة",
        "📲 مركز الإشعارات",
        "🚨 الحالات المخالفة",
        "⚙️ إدارة الإجراءات",
    ],
)

st.sidebar.divider()
type_filter = st.sidebar.multiselect(
    "🔍 تصفية حسب نوع الإقامة",
    options=sorted(data["نوع الإقامة"].unique().tolist()),
    default=sorted(data["نوع الإقامة"].unique().tolist()),
)
data = data[data["نوع الإقامة"].isin(type_filter)] if type_filter else data

st.sidebar.divider()
st.sidebar.info(
    "نسخة تجريبية للهاكاثون\n\nجميع البيانات المعروضة افتراضية "
    "ولا تمثل بيانات حقيقية لأي جهة."
)

# ==================================================
# DASHBOARD
# ==================================================
if page == "🏠 لوحة التحكم":
    st.markdown('<p class="wiqaa-title">وِقاء 🛡️</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="wiqaa-subtitle">من الوقاية من المخالفة إلى تسريع معالجتها — '
        'منصة استباقية لإدارة امتثال الإقامة.</p>',
        unsafe_allow_html=True,
    )

    st.markdown("#### دورة الامتثال الكاملة")
    stages = ["تسجيل", "حساب", "تنبؤ", "إشعار", "كشف",
              "ترتيب أولوية", "توجيه", "معالجة", "إغلاق", "تعلّم"]
    st.markdown(
        " ".join(
            f'<span class="badge">{s}</span>'
            + ('<span class="badge-arrow">←</span>' if i < len(stages) - 1 else "")
            for i, s in enumerate(stages)
        ),
        unsafe_allow_html=True,
    )

    st.divider()

    total = len(data)
    expiring_30 = len(data[(data["الأيام المتبقية"] >= 0) & (data["الأيام المتبقية"] <= 30)])
    expired = len(data[data["الأيام المتبقية"] < 0])
    urgent = len(data[data["درجة الأولوية"] >= 75])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي الحالات", total)
    c2.metric("تنتهي خلال 30 يوم", expiring_30)
    c3.metric("إقامات منتهية", expired)
    c4.metric("تحتاج تدخل عاجل", urgent)

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🔮 توزيع الحالات حسب قرب انتهاء الإقامة")

        def expiry_group(d):
            if d < 0:
                return "منتهية"
            elif d <= 7:
                return "خلال 7 أيام"
            elif d <= 30:
                return "خلال 30 يوم"
            elif d <= 60:
                return "خلال 60 يوم"
            else:
                return "أكثر من 60 يوم"

        order = ["منتهية", "خلال 7 أيام", "خلال 30 يوم", "خلال 60 يوم", "أكثر من 60 يوم"]
        chart_data = data["الأيام المتبقية"].apply(expiry_group).value_counts().reindex(order).fillna(0).reset_index()
        chart_data.columns = ["الفترة", "عدد الحالات"]
        fig = px.bar(chart_data, x="الفترة", y="عدد الحالات",
                     color="الفترة",
                     color_discrete_map={
                         "منتهية": "#d92d20", "خلال 7 أيام": "#f79009",
                         "خلال 30 يوم": "#2e90fa", "خلال 60 يوم": "#7a5af8",
                         "أكثر من 60 يوم": "#12b76a"
                     })
        fig.update_layout(showlegend=False, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("🧭 مؤشر الصحة العامة")
        compliance_score = max(0, 100 - (urgent / max(total, 1)) * 100)
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=compliance_score,
            number={"suffix": "%"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#12b76a" if compliance_score >= 70 else "#f79009"},
                "steps": [
                    {"range": [0, 40], "color": "#fef2f2"},
                    {"range": [40, 70], "color": "#fff7ed"},
                    {"range": [70, 100], "color": "#ecfdf3"},
                ],
            },
        ))
        gauge.update_layout(height=300, margin=dict(t=30, b=10, l=20, r=20))
        st.plotly_chart(gauge, use_container_width=True)

    st.subheader("🚨 الحالات ذات الأولوية")
    priority = data.sort_values("درجة الأولوية", ascending=False).head(6)
    st.dataframe(
        priority[["رقم الحالة", "تاريخ الانتهاء", "الأيام المتبقية",
                  "درجة الأولوية", "حالة الإجراء"]],
        use_container_width=True, hide_index=True,
    )

# ==================================================
# RESIDENT DATABASE
# ==================================================
elif page == "👤 سجل الوافدين":
    st.title("👤 سجل الوافدين")
    st.write("قاعدة بيانات تجريبية لمتابعة صلاحية الإقامات.")

    search = st.text_input("🔎 البحث برقم الحالة أو الاسم")
    filtered = data.copy()
    if search:
        filtered = filtered[
            filtered["رقم الحالة"].str.contains(search, case=False, na=False)
            | filtered["الاسم"].str.contains(search, case=False, na=False)
        ]

    st.dataframe(
        filtered[["رقم الحالة", "الاسم", "الجهة/القطاع", "نوع الإقامة",
                  "تاريخ الانتهاء", "الأيام المتبقية", "حالة الإجراء"]],
        use_container_width=True, hide_index=True,
    )

    csv = filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ تنزيل كملف CSV", data=csv,
                        file_name="wiqaa_residents.csv", mime="text/csv")

# ==================================================
# PREDICTION
# ==================================================
elif page == "🔮 التنبؤ بانتهاء الإقامة":
    st.title("🔮 محرك التنبؤ")
    st.write("يحدد النظام الحالات التي تحتاج إلى تدخل قبل انتهاء صلاحية الإقامة.")

    if data.empty:
        st.warning("لا توجد حالات مطابقة للفلترة الحالية.")
    else:
        selected = st.selectbox("اختر حالة", data["رقم الحالة"])
        row = data[data["رقم الحالة"] == selected].iloc[0]
        days = int(row["الأيام المتبقية"])
        risk = row["درجة الأولوية"]

        c1, c2, c3 = st.columns(3)
        c1.metric("تاريخ الانتهاء", pd.to_datetime(row["تاريخ الانتهاء"]).strftime("%Y-%m-%d"))
        c2.metric("الأيام المتبقية", days)
        c3.metric("درجة الأولوية", f"{risk}%")

        st.divider()

        col_gauge, col_timeline = st.columns([1, 2])
        with col_gauge:
            g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk,
                title={"text": "درجة الخطورة"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": STATUS_COLORS.get(row["حالة الإجراء"], "#667085")},
                }
            ))
            g.update_layout(height=260, margin=dict(t=40, b=10, l=20, r=20))
            st.plotly_chart(g, use_container_width=True)

        with col_timeline:
            st.markdown("**الخط الزمني للحالة**")
            today = date.today()
            expiry = pd.to_datetime(row["تاريخ الانتهاء"]).date()
            start = min(today, expiry) - timedelta(days=5)
            timeline_df = pd.DataFrame({
                "الحدث": ["اليوم", "تاريخ الانتهاء"],
                "التاريخ": [today, expiry],
            })
            tfig = px.scatter(timeline_df, x="التاريخ", y=["الحدث"] * 2,
                               text="الحدث", color="الحدث")
            tfig.update_traces(marker=dict(size=16), textposition="top center")
            tfig.update_yaxes(visible=False)
            tfig.update_layout(height=260, showlegend=False,
                                margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(tfig, use_container_width=True)

        if days < 0:
            st.markdown('<div class="danger-card">🔴 الإقامة منتهية — الحالة تحتاج مراجعة وفق الإجراءات النظامية.</div>', unsafe_allow_html=True)
        elif days <= 7:
            st.markdown('<div class="alert-card">⚠️ تنبيه عاجل: الإقامة تقترب من الانتهاء.</div>', unsafe_allow_html=True)
        elif days <= 30:
            st.markdown('<div class="info-card">🟠 تنبيه مبكر: يوصى باتخاذ الإجراء قبل اقتراب موعد الانتهاء.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-card">🟢 الحالة مستقرة حاليًا.</div>', unsafe_allow_html=True)

        st.subheader("📲 محاكاة إشعار الوافد")
        if st.button("إرسال تنبيه تجريبي"):
            note = {
                "رقم الحالة": selected,
                "القناة": row["قناة التواصل"],
                "التاريخ": date.today().strftime("%Y-%m-%d %H:%M"),
                "الرسالة": f"ستنتهي إقامتك بتاريخ {expiry}. يرجى اتخاذ الإجراء النظامي.",
            }
            st.session_state.notifications.insert(0, note)
            st.success(f"تم إرسال تنبيه تجريبي للحالة {selected} عبر {row['قناة التواصل']}.")

# ==================================================
# NOTIFICATION CENTER
# ==================================================
elif page == "📲 مركز الإشعارات":
    st.title("📲 مركز الإشعارات")
    st.write("سجل بكل التنبيهات المُرسلة خلال هذه الجلسة التجريبية.")

    notes = st.session_state.notifications
    c1, c2 = st.columns(2)
    c1.metric("إجمالي الإشعارات المُرسلة", len(notes))
    if notes:
        by_channel = pd.DataFrame(notes)["القناة"].value_counts().idxmax()
        c2.metric("القناة الأكثر استخدامًا", by_channel)
    else:
        c2.metric("القناة الأكثر استخدامًا", "—")

    st.divider()
    if notes:
        st.dataframe(pd.DataFrame(notes), use_container_width=True, hide_index=True)
    else:
        st.info("لم يتم إرسال أي إشعارات بعد. جرّبي ذلك من صفحة «التنبؤ بانتهاء الإقامة».")

# ==================================================
# VIOLATIONS
# ==================================================
elif page == "🚨 الحالات المخالفة":
    st.title("🚨 إدارة الحالات المخالفة")
    violations = data[data["الأيام المتبقية"] < 0].copy()

    st.metric("إجمالي الحالات المنتهية", len(violations))
    st.divider()

    if len(violations) > 0:
        violations["أولوية المعالجة"] = violations["درجة الأولوية"]
        violations = violations.sort_values("أولوية المعالجة", ascending=False)
        st.dataframe(
            violations[["رقم الحالة", "تاريخ الانتهاء", "الأيام المتبقية",
                        "أولوية المعالجة", "زمن المعالجة"]],
            use_container_width=True, hide_index=True,
        )
        st.subheader("🧠 توصية النظام")
        st.markdown(
            '<div class="info-card">يتم ترتيب الحالات حسب الأولوية وزمن التأخر، '
            'ثم توجيهها للمسار الإجرائي المختص وفق الصلاحيات المعتمدة.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="success-card">لا توجد حالات منتهية في البيانات التجريبية المفلترة حاليًا.</div>', unsafe_allow_html=True)

# ==================================================
# PROCESS MANAGEMENT
# ==================================================
elif page == "⚙️ إدارة الإجراءات":
    st.title("⚙️ إدارة وتسريع الإجراءات")
    st.write("تحليل الاختناقات في معالجة الحالات ومحاكاة أثر تحسين الطاقة التشغيلية.")

    avg_time = data["زمن المعالجة"].mean()
    c1, c2, c3 = st.columns(3)
    c1.metric("متوسط زمن المعالجة", f"{avg_time:.1f} يوم")
    c2.metric("أعلى زمن معالجة", f"{data['زمن المعالجة'].max():.1f} يوم")
    c3.metric("حالات تحتاج تدخل", len(data[data["زمن المعالجة"] > 3]))

    st.divider()

    process_data = data[["رقم الحالة", "زمن المعالجة"]].sort_values(
        "زمن المعالجة", ascending=False
    )
    fig = px.bar(process_data, x="رقم الحالة", y="زمن المعالجة",
                 title="زمن معالجة الحالات (الوضع الحالي)")
    fig.update_layout(height=360)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔎 الاختناقات المحتملة")
    bottlenecks = data[data["زمن المعالجة"] > 3]
    if len(bottlenecks) > 0:
        st.markdown(
            f'<div class="alert-card">تم رصد {len(bottlenecks)} حالات تتجاوز 3 أيام '
            'في البيانات التجريبية. التوصية: مراجعة سبب التأخير وإعادة توزيع الحالات '
            'وفق الطاقة التشغيلية والصلاحيات المعتمدة.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="success-card">لا توجد اختناقات واضحة في البيانات التجريبية.</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("🧪 محاكاة قبل / بعد التحسين")
    automation_pct = st.slider("نسبة الأتمتة المقترحة (%)", 0, 90, 30, step=10)
    improved = process_data.copy()
    improved["زمن المعالجة"] = improved["زمن المعالجة"] * (1 - automation_pct / 100)

    compare = pd.concat([
        process_data.assign(الحالة="قبل التحسين"),
        improved.assign(الحالة="بعد التحسين"),
    ])
    cfig = px.bar(compare, x="رقم الحالة", y="زمن المعالجة", color="الحالة",
                  barmode="group", title="أثر الأتمتة على زمن المعالجة")
    cfig.update_layout(height=380)
    st.plotly_chart(cfig, use_container_width=True)

    saved = avg_time - improved["زمن المعالجة"].mean()
    st.markdown(
        f'<div class="success-card">بتطبيق {automation_pct}% أتمتة، ينخفض متوسط '
        f'زمن المعالجة من {avg_time:.1f} يوم إلى {improved["زمن المعالجة"].mean():.1f} يوم '
        f'(توفير {saved:.1f} يوم لكل حالة تقريبًا).</div>',
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption("WIQAA | Hackathon Prototype | Demo Data Only — REGISTER → CALCULATE → PREDICT → NOTIFY → DETECT → PRIORITIZE → ROUTE → PROCESS → CLOSE → LEARN")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlalchemy
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import DB_PATH
from ml.models import (forecast_sales, predict_profitability,
                       segment_customers, detect_anomalies)

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Smart Sales Platform",
    page_icon="📊",
    layout="wide"
)

# ─────────────────────────────────────────
# CHARGEMENT
# ─────────────────────────────────────────
@st.cache_data
def load_data():
    engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")
    df = pd.read_sql("SELECT * FROM sales_features", con=engine)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df

@st.cache_data
def load_rfm():
    engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")
    return pd.read_sql("SELECT * FROM rfm_segments", con=engine)

@st.cache_data
def get_ml_results(_df):
    try:
        monthly, forecast_df, full_forecast, metrics = forecast_sales(_df)
        df_scored = predict_profitability(_df)
        _, _, customer_df = segment_customers(_df)
        _, df_anomalies = detect_anomalies(_df)
        return monthly, forecast_df, full_forecast, metrics, df_scored, customer_df, df_anomalies
    except FileNotFoundError:
        st.error("⚠️ Modèles ML non trouvés. Veuillez d'abord entraîner les modèles avec : python ml/train_models.py")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ Erreur lors du chargement des modèles : {e}")
        st.stop()

try:
    df = load_data()
    rfm_df = load_rfm()
except Exception as e:
    st.error(f"⚠️ Erreur de chargement des données : {e}")
    st.error("Veuillez d'abord exécuter le pipeline ETL : python etl/run_pipeline.py")
    st.stop()

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=55)
st.sidebar.title("Smart Sales Platform")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", [
    "📊 Vue Générale",
    "📅 Forecast",
    "👥 Analyse Clients & RFM",
    "🤖 ML — Rentabilité",
    "🚨 Anomalies"
])

st.sidebar.markdown("---")

years   = sorted(df["year"].unique())
regions = ["Toutes"] + sorted(df["region"].unique())
cats    = ["Toutes"] + sorted(df["category"].unique())

sel_years  = st.sidebar.multiselect("Année(s)", years, default=years)
sel_region = st.sidebar.selectbox("Région", regions)
sel_cat    = st.sidebar.selectbox("Catégorie", cats)

# Filtrage
dff = df[df["year"].isin(sel_years)]
if sel_region != "Toutes":
    dff = dff[dff["region"] == sel_region]
if sel_cat != "Toutes":
    dff = dff[dff["category"] == sel_cat]

st.sidebar.markdown("---")
st.sidebar.metric("Commandes filtrées", f"{len(dff):,}")

# ML results (toujours sur le dataset complet)
monthly, forecast_df, full_forecast, prophet_metrics, df_scored, customer_df, df_anomalies = get_ml_results(df)

# ══════════════════════════════════════════
# PAGE 1 — VUE GÉNÉRALE
# ══════════════════════════════════════════
if page == "📊 Vue Générale":
    st.title("📊 Vue Générale")
    st.caption("KPIs · Catégories · Géographie · Remises")
    st.markdown("---")

    # KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("💰 Ventes totales",   f"${dff['sales'].sum():,.0f}")
    k2.metric("📈 Profit total",     f"${dff['profit'].sum():,.0f}")
    k3.metric("🛒 Commandes",        f"{dff['order_id'].nunique():,}")
    k4.metric("👥 Clients uniques",  f"{dff['customer_id'].nunique():,}")
    k5.metric("📦 Marge moyenne",    f"{dff['profit_margin'].mean()*100:.1f}%")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ventes & Profit par catégorie")
        cat_df = dff.groupby("category")[["sales", "profit"]].sum().reset_index()
        fig = px.bar(cat_df, x="category", y=["sales", "profit"],
                     barmode="group",
                     color_discrete_sequence=["#636EFA", "#00CC96"])
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Profit par sous-catégorie")
        sub_df = (dff.groupby("sub_category")["profit"]
                  .sum().reset_index()
                  .sort_values("profit"))
        fig = px.bar(sub_df, x="profit", y="sub_category",
                     orientation="h",
                     color="profit",
                     color_continuous_scale=["#EF553B", "#636EFA", "#00CC96"])
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Ventes par région")
        reg_df = dff.groupby("region")["sales"].sum().reset_index()
        fig = px.pie(reg_df, names="region", values="sales",
                     hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Impact des remises sur le profit")
        disc_df = dff.groupby("discount_tier")["profit"].mean().reset_index()
        order = ["none", "low", "medium", "high"]
        disc_df["discount_tier"] = pd.Categorical(
            disc_df["discount_tier"], categories=order, ordered=True)
        disc_df = disc_df.sort_values("discount_tier")
        fig = px.bar(disc_df, x="discount_tier", y="profit",
                     color="profit",
                     color_continuous_scale=["#EF553B", "#636EFA", "#00CC96"],
                     labels={"discount_tier": "Palier remise",
                             "profit": "Profit moyen ($)"})
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════
# PAGE 2 — FORECAST
# ══════════════════════════════════════════
elif page == "📅 Forecast":
    st.title("📅 Forecast des Ventes")
    st.caption("Modèle Prophet · Saisonnalité · Tendance")
    st.markdown("---")

    periods = st.slider("Horizon de prévision (mois)", 3, 24, 12)
    monthly_fresh, forecast_fresh, full_fresh, metrics_fresh = forecast_sales(df, periods=periods)

    # Graphique principal
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly_fresh["ds"], y=monthly_fresh["y"],
        mode="lines+markers", name="Ventes réelles",
        line=dict(color="#636EFA", width=2)
    ))

    hist = full_fresh[full_fresh["ds"] <= monthly_fresh["ds"].max()]
    fig.add_trace(go.Scatter(
        x=hist["ds"], y=hist["yhat"],
        mode="lines", name="Modèle fitted",
        line=dict(color="#00CC96", width=1.5, dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=forecast_fresh["date"], y=forecast_fresh["predicted_sales"],
        mode="lines+markers", name=f"Forecast {periods} mois",
        line=dict(color="#FF6692", width=2),
        marker=dict(symbol="diamond", size=7)
    ))

    fig.add_trace(go.Scatter(
        x=pd.concat([forecast_fresh["date"],
                     forecast_fresh["date"].iloc[::-1]]),
        y=pd.concat([forecast_fresh["upper_bound"],
                     forecast_fresh["lower_bound"].iloc[::-1]]),
        fill="toself", fillcolor="rgba(255,102,146,0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Intervalle 95%"
    ))

    fig.add_vline(x=str(monthly_fresh["ds"].max()),
                  line_dash="dot", line_color="gray")
    fig.update_layout(
        height=420, hovermode="x unified",
        margin=dict(l=0,r=0,t=10,b=0),
        legend=dict(orientation="h", y=1.08),
        yaxis_tickformat="$,.0f"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Métriques forecast (dynamiques)
    f1, f2, f3 = st.columns(3)
    f1.metric("MAPE", f"{metrics_fresh['mape']:.2f}%")
    f2.metric("MAE", f"${metrics_fresh['mae']:,.0f}")
    f3.metric("Ventes prévues",
              f"${forecast_fresh['predicted_sales'].sum():,.0f}",
              f"sur {periods} mois")

    # Tableau forecast
    with st.expander("📋 Voir le tableau des prévisions"):
        st.dataframe(
            forecast_fresh.rename(columns={
                "date":            "Mois",
                "predicted_sales": "Prévision ($)",
                "lower_bound":     "Borne basse ($)",
                "upper_bound":     "Borne haute ($)"
            }).style.format({
                "Prévision ($)":   "${:,.0f}",
                "Borne basse ($)": "${:,.0f}",
                "Borne haute ($)": "${:,.0f}"
            }),
            use_container_width=True,
            hide_index=True
        )

# ══════════════════════════════════════════
# PAGE 3 — CLIENTS & RFM
# ══════════════════════════════════════════
elif page == "👥 Analyse Clients & RFM":
    st.title("👥 Analyse Clients & Segmentation RFM")
    st.caption("8 segments actionnables · Pareto · Valeur client")
    st.markdown("---")

    colors_map = {
        "Champions":          "#00CC96",
        "Loyal Customers":    "#636EFA",
        "Potential Loyalists":"#AB63FA",
        "At Risk":            "#FFA15A",
        "New Customers":      "#19D3F3",
        "Can't Lose Them":    "#FF6692",
        "Hibernating":        "#B6E880",
        "Lost":               "#EF553B"
    }

    # KPIs RFM
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Clients total",        f"{len(rfm_df):,}")
    r2.metric("Champions",
              f"{len(rfm_df[rfm_df['segment']=='Champions']):,}")
    r3.metric("⚠️ At Risk",
              f"{len(rfm_df[rfm_df['segment']=='At Risk']):,}")
    cant_lose_count = len(rfm_df[rfm_df['segment']=="Can't Lose Them"])
    r4.metric("🚨 Can't Lose Them", f"{cant_lose_count:,}")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribution des segments")
        seg_counts = rfm_df["segment"].value_counts().reset_index()
        seg_counts.columns = ["segment", "count"]
        fig = px.bar(
            seg_counts.sort_values("count"),
            x="count", y="segment", orientation="h",
            color="segment",
            color_discrete_map=colors_map
        )
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=10,b=0),
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Recency vs Frequency")
        fig = px.scatter(
            rfm_df, x="recency", y="frequency",
            color="segment", size="monetary",
            color_discrete_map=colors_map,
            hover_data=["customer_id", "monetary", "RFM_score"],
            labels={"recency":   "Recency (jours)",
                    "frequency": "Frequency (commandes)"}
        )
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    # Valeur par segment
    st.subheader("Valeur totale par segment")
    seg_value = (rfm_df.groupby("segment")["monetary"]
                 .sum().reset_index()
                 .sort_values("monetary", ascending=False))
    seg_value["pct"] = (seg_value["monetary"] /
                        seg_value["monetary"].sum() * 100).round(1)
    seg_value["color"] = seg_value["segment"].map(colors_map)

    fig = px.bar(
        seg_value, x="segment", y="monetary",
        color="segment", color_discrete_map=colors_map,
        text=seg_value["pct"].apply(lambda x: f"{x}%"),
        labels={"monetary": "Valeur totale ($)"}
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=320, margin=dict(l=0,r=0,t=30,b=0),
                      showlegend=False, yaxis_tickformat="$,.0f")
    st.plotly_chart(fig, use_container_width=True)

    # Filtre segment
    st.subheader("🔍 Explorer un segment")
    seg_select = st.selectbox("Choisir un segment", rfm_df["segment"].unique())
    seg_detail = rfm_df[rfm_df["segment"] == seg_select]

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Clients",         f"{len(seg_detail):,}")
    d2.metric("Recency moy.",    f"{seg_detail['recency'].mean():.0f} j")
    d3.metric("Frequency moy.",  f"{seg_detail['frequency'].mean():.1f}")
    d4.metric("Monetary moy.",   f"${seg_detail['monetary'].mean():,.0f}")

    st.dataframe(
        seg_detail[["customer_id","recency","frequency",
                    "monetary","RFM_score","segment"]]
        .sort_values("RFM_score", ascending=False),
        use_container_width=True, hide_index=True
    )

# ══════════════════════════════════════════
# PAGE 4 — ML RENTABILITÉ
# ══════════════════════════════════════════
elif page == "🤖 ML — Rentabilité":
    st.title("🤖 Prédiction de Rentabilité")
    st.caption("Random Forest · ROC-AUC 0.990 · 25 features")
    st.markdown("---")

    # KPIs
    n_total    = len(df_scored)
    n_risk     = (df_scored["profit_predicted"] == 0).sum()
    pct_risk   = n_risk / n_total * 100
    avg_proba  = df_scored["profit_proba"].mean()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Commandes analysées",     f"{n_total:,}")
    m2.metric("⚠️ Prédites non rentables", f"{n_risk:,}")
    m3.metric("Taux de risque",           f"{pct_risk:.1f}%")
    m4.metric("Confiance moyenne",        f"{avg_proba*100:.1f}%")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribution des probabilités")
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=df_scored[df_scored["is_profitable"]==1]["profit_proba"],
            name="Réellement rentable",
            marker_color="#00CC96", opacity=0.7, nbinsx=40
        ))
        fig.add_trace(go.Histogram(
            x=df_scored[df_scored["is_profitable"]==0]["profit_proba"],
            name="Réellement non rentable",
            marker_color="#EF553B", opacity=0.7, nbinsx=40
        ))
        fig.add_vline(x=0.5, line_dash="dash", line_color="black")
        fig.update_layout(height=320, barmode="overlay",
                          margin=dict(l=0,r=0,t=10,b=0),
                          legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Commandes à risque par catégorie")
        risk_cat = (df_scored[df_scored["profit_predicted"]==0]
                    .groupby("category")
                    .size().reset_index(name="count"))
        fig = px.pie(risk_cat, names="category", values="count",
                     hole=0.4,
                     color_discrete_sequence=["#EF553B","#FFA15A","#636EFA"])
        fig.update_layout(height=320, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    # Commandes à risque par remise
    st.subheader("Taux de commandes non rentables par palier de remise")
    risk_disc = df_scored.groupby("discount_tier").agg(
        total=("profit_predicted", "count"),
        at_risk=("profit_predicted", lambda x: (x==0).sum())
    ).reset_index()
    risk_disc["pct_risk"] = (risk_disc["at_risk"] /
                              risk_disc["total"] * 100).round(1)
    order = ["none","low","medium","high"]
    risk_disc["discount_tier"] = pd.Categorical(
        risk_disc["discount_tier"], categories=order, ordered=True)
    risk_disc = risk_disc.sort_values("discount_tier")

    fig = px.bar(risk_disc, x="discount_tier", y="pct_risk",
                 color="pct_risk",
                 color_continuous_scale=["#00CC96","#FFA15A","#EF553B"],
                 text=risk_disc["pct_risk"].apply(lambda x: f"{x}%"),
                 labels={"discount_tier": "Palier de remise",
                         "pct_risk":      "% commandes non rentables"})
    fig.add_hline(y=50, line_dash="dash", line_color="red")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=300, margin=dict(l=0,r=0,t=30,b=0),
                      coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    # Top commandes à risque
    with st.expander("🔍 Voir les commandes prédites non rentables"):
        risky = (df_scored[df_scored["profit_predicted"]==0]
                 [["order_id","customer_name","category",
                   "sub_category","sales","discount",
                   "profit_proba"]]
                 .sort_values("profit_proba")
                 .head(100))
        risky.columns = ["Order ID","Client","Catégorie",
                         "Sous-catégorie","Ventes ($)",
                         "Remise","Proba rentable"]
        st.dataframe(risky, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════
# PAGE 5 — ANOMALIES
# ══════════════════════════════════════════
elif page == "🚨 Anomalies":
    st.title("🚨 Détection d'Anomalies")
    st.caption("Isolation Forest · 5% contamination · 500 anomalies")
    st.markdown("---")

    anomalies = df_anomalies[df_anomalies["is_anomaly"]]

    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Anomalies détectées",  f"{len(anomalies):,}")
    a2.metric("% du total",           f"{len(anomalies)/len(df_anomalies)*100:.1f}%")
    a3.metric("Perte moyenne",        f"${anomalies['profit'].mean():.0f}")
    a4.metric("Remise moyenne",       f"{anomalies['discount'].mean()*100:.0f}%")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ventes vs Profit — anomalies en rouge")
        fig = px.scatter(
            df_anomalies, x="sales", y="profit",
            color="is_anomaly",
            color_discrete_map={False: "#636EFA", True: "#EF553B"},
            opacity=0.5,
            labels={"sales": "Ventes ($)", "profit": "Profit ($)",
                    "is_anomaly": "Anomalie"}
        )
        fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Anomalies par catégorie")
        anom_cat = (anomalies.groupby("category")
                    .agg(count=("order_id","count"),
                         profit_moy=("profit","mean"))
                    .reset_index())
        fig = px.bar(anom_cat, x="category", y="count",
                     color="profit_moy",
                     color_continuous_scale=["#EF553B","#FFA15A","#636EFA"],
                     text="count",
                     labels={"count": "Nombre d'anomalies",
                             "profit_moy": "Profit moyen ($)"})
        fig.update_traces(textposition="outside")
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("🔍 Voir les commandes anormales"):
        st.dataframe(
            anomalies[["order_id","customer_name","category",
                       "sub_category","sales","profit","discount"]]
            .sort_values("profit")
            .head(100),
            use_container_width=True, hide_index=True
        )

st.markdown("---")
st.caption("Smart Sales Platform v2 · ETL · Feature Engineering · "
           "RFM · Prophet · Random Forest")
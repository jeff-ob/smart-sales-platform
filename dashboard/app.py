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
    st.caption("KPIs · Tendances · Performance · Insights")
    st.markdown("---")

    # KPIs avec deltas (comparaison année précédente)
    if len(sel_years) > 1:
        current_year = max(sel_years)
        prev_year = current_year - 1
        
        dff_current = dff[dff["year"] == current_year]
        dff_prev = dff[dff["year"] == prev_year]
        
        sales_current = dff_current["sales"].sum()
        sales_prev = dff_prev["sales"].sum()
        sales_delta = ((sales_current - sales_prev) / sales_prev * 100) if sales_prev > 0 else 0
        
        profit_current = dff_current["profit"].sum()
        profit_prev = dff_prev["profit"].sum()
        profit_delta = ((profit_current - profit_prev) / profit_prev * 100) if profit_prev > 0 else 0
        
        orders_current = dff_current["order_id"].nunique()
        orders_prev = dff_prev["order_id"].nunique()
        orders_delta = ((orders_current - orders_prev) / orders_prev * 100) if orders_prev > 0 else 0
        
        clients_current = dff_current["customer_id"].nunique()
        clients_prev = dff_prev["customer_id"].nunique()
        clients_delta = ((clients_current - clients_prev) / clients_prev * 100) if clients_prev > 0 else 0
        
        margin_current = dff_current["profit_margin"].mean() * 100
        margin_prev = dff_prev["profit_margin"].mean() * 100
        margin_delta = margin_current - margin_prev
    else:
        sales_delta = profit_delta = orders_delta = clients_delta = margin_delta = None

    # KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("💰 Ventes totales", f"${dff['sales'].sum():,.0f}",
              f"{sales_delta:+.1f}%" if sales_delta is not None else None)
    k2.metric("📈 Profit total", f"${dff['profit'].sum():,.0f}",
              f"{profit_delta:+.1f}%" if profit_delta is not None else None)
    k3.metric("🛒 Commandes", f"{dff['order_id'].nunique():,}",
              f"{orders_delta:+.1f}%" if orders_delta is not None else None)
    k4.metric("👥 Clients uniques", f"{dff['customer_id'].nunique():,}",
              f"{clients_delta:+.1f}%" if clients_delta is not None else None)
    k5.metric("📦 Marge moyenne", f"{dff['profit_margin'].mean()*100:.1f}%",
              f"{margin_delta:+.1f}pp" if margin_delta is not None else None)
    
    st.markdown("---")
    
    # Insights automatiques
    st.subheader("💡 Insights Clés")
    insights_cols = st.columns(3)
    
    # Insight 1: Meilleure catégorie
    best_cat = dff.groupby("category")["profit"].sum().idxmax()
    best_cat_profit = dff.groupby("category")["profit"].sum().max()
    insights_cols[0].info(f"🏆 **{best_cat}** est la catégorie la plus rentable avec **${best_cat_profit:,.0f}** de profit")
    
    # Insight 2: Remises excessives
    high_disc = dff[dff["discount"] > 0.3]
    if len(high_disc) > 0:
        pct_high_disc = len(high_disc) / len(dff) * 100
        loss_high_disc = high_disc[high_disc["profit"] < 0]["profit"].sum()
        insights_cols[1].warning(f"⚠️ **{pct_high_disc:.1f}%** des commandes ont une remise >30%, causant **${abs(loss_high_disc):,.0f}** de pertes")
    
    # Insight 3: Top client
    top_client = dff.groupby("customer_name")["sales"].sum().idxmax()
    top_client_sales = dff.groupby("customer_name")["sales"].sum().max()
    insights_cols[2].success(f"⭐ **{top_client}** est le meilleur client avec **${top_client_sales:,.0f}** de ventes")
    
    st.markdown("---")
    
    # Évolution temporelle
    st.subheader("📈 Évolution des Ventes et Profit")
    monthly_trend = dff.groupby(dff["order_date"].dt.to_period("M")).agg({
        "sales": "sum",
        "profit": "sum"
    }).reset_index()
    monthly_trend["order_date"] = monthly_trend["order_date"].dt.to_timestamp()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_trend["order_date"], y=monthly_trend["sales"],
        mode="lines+markers", name="Ventes",
        line=dict(color="#636EFA", width=2),
        yaxis="y"
    ))
    fig.add_trace(go.Scatter(
        x=monthly_trend["order_date"], y=monthly_trend["profit"],
        mode="lines+markers", name="Profit",
        line=dict(color="#00CC96", width=2),
        yaxis="y2"
    ))
    fig.update_layout(
        height=300,
        margin=dict(l=0,r=0,t=10,b=0),
        hovermode="x unified",
        yaxis=dict(title="Ventes ($)", tickformat="$,.0f"),
        yaxis2=dict(title="Profit ($)", overlaying="y", side="right", tickformat="$,.0f"),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
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
    
    st.markdown("---")
    
    # Top & Flop produits
    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("🏆 Top 5 Produits (Profit)")
        top_products = (dff.groupby("product_name")["profit"]
                       .sum().reset_index()
                       .sort_values("profit", ascending=False)
                       .head(5))
        fig = px.bar(top_products, x="profit", y="product_name",
                     orientation="h",
                     color_discrete_sequence=["#00CC96"])
        fig.update_layout(height=250, margin=dict(l=0,r=0,t=10,b=0),
                         yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col6:
        st.subheader("📉 Flop 5 Produits (Profit)")
        flop_products = (dff.groupby("product_name")["profit"]
                        .sum().reset_index()
                        .sort_values("profit")
                        .head(5))
        fig = px.bar(flop_products, x="profit", y="product_name",
                     orientation="h",
                     color_discrete_sequence=["#EF553B"])
        fig.update_layout(height=250, margin=dict(l=0,r=0,t=10,b=0),
                         yaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════
# PAGE 2 — FORECAST
# ══════════════════════════════════════════
elif page == "📅 Forecast":
    st.title("📅 Forecast des Ventes")
    st.caption("Modèle Prophet · Saisonnalité · Tendance · Scénarios")
    st.markdown("---")

    periods = st.slider("Horizon de prévision (mois)", 3, 24, 12)
    monthly_fresh, forecast_fresh, full_fresh, metrics_fresh = forecast_sales(df, periods=periods)

    # Métriques forecast (en haut)
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("📊 MAPE", f"{metrics_fresh['mape']:.2f}%",
              help="Mean Absolute Percentage Error - Plus c'est bas, mieux c'est")
    f2.metric("📏 MAE", f"${metrics_fresh['mae']:,.0f}",
              help="Mean Absolute Error - Erreur moyenne en dollars")
    f3.metric("💰 Ventes prévues", f"${forecast_fresh['predicted_sales'].sum():,.0f}",
              f"sur {periods} mois")
    
    # Calcul de la croissance prévue
    last_real = monthly_fresh["y"].iloc[-12:].sum()
    forecast_sum = forecast_fresh['predicted_sales'].sum()
    growth = ((forecast_sum - last_real) / last_real * 100) if last_real > 0 else 0
    f4.metric("📈 Croissance prévue", f"{growth:+.1f}%",
              help=f"vs derniers 12 mois réels")
    
    st.markdown("---")

    # Graphique principal (ORIGINAL - non modifié)
    st.subheader("📈 Prévisions avec Intervalle de Confiance")
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
    
    st.markdown("---")
    
    # Composantes de saisonnalité
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Saisonnalité Annuelle")
        # Extraire la composante yearly de Prophet
        if "yearly" in full_fresh.columns:
            yearly_comp = full_fresh[["ds", "yearly"]].copy()
            yearly_comp["month"] = pd.to_datetime(yearly_comp["ds"]).dt.month
            yearly_avg = yearly_comp.groupby("month")["yearly"].mean().reset_index()
            yearly_avg["month_name"] = yearly_avg["month"].apply(
                lambda x: ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
                          "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"][x-1]
            )
            
            fig = px.bar(yearly_avg, x="month_name", y="yearly",
                        color="yearly",
                        color_continuous_scale=["#EF553B", "#636EFA", "#00CC96"],
                        labels={"month_name": "Mois", "yearly": "Effet saisonnier ($)"})
            fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                            coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Insight saisonnalité
            best_month = yearly_avg.loc[yearly_avg["yearly"].idxmax(), "month_name"]
            worst_month = yearly_avg.loc[yearly_avg["yearly"].idxmin(), "month_name"]
            st.info(f"📊 Meilleur mois : **{best_month}** · Pire mois : **{worst_month}**")
        else:
            st.info("Composante de saisonnalité non disponible dans ce modèle")
    
    with col2:
        st.subheader("📊 Tendance Générale")
        # Extraire la tendance
        if "trend" in full_fresh.columns:
            trend_data = full_fresh[["ds", "trend"]].copy()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend_data["ds"], y=trend_data["trend"],
                mode="lines", name="Tendance",
                line=dict(color="#636EFA", width=2),
                fill="tozeroy", fillcolor="rgba(99,110,250,0.1)"
            ))
            fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                            yaxis_tickformat="$,.0f",
                            xaxis_title="Date",
                            yaxis_title="Tendance ($)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Insight tendance
            trend_start = trend_data["trend"].iloc[0]
            trend_end = trend_data["trend"].iloc[-1]
            trend_growth = ((trend_end - trend_start) / trend_start * 100)
            if trend_growth > 0:
                st.success(f"📈 Tendance à la hausse : **+{trend_growth:.1f}%** sur la période")
            else:
                st.warning(f"📉 Tendance à la baisse : **{trend_growth:.1f}%** sur la période")
        else:
            st.info("Composante de tendance non disponible dans ce modèle")
    
    st.markdown("---")
    
    # Scénarios optimiste/pessimiste
    st.subheader("🎯 Scénarios de Prévision")
    scenario_cols = st.columns(3)
    
    # Scénario pessimiste (borne basse)
    pessimistic = forecast_fresh["lower_bound"].sum()
    scenario_cols[0].metric(
        "😟 Scénario Pessimiste",
        f"${pessimistic:,.0f}",
        f"{((pessimistic - last_real) / last_real * 100):+.1f}%",
        help="Borne basse de l'intervalle de confiance 95%"
    )
    
    # Scénario réaliste (prévision)
    realistic = forecast_fresh["predicted_sales"].sum()
    scenario_cols[1].metric(
        "😐 Scénario Réaliste",
        f"${realistic:,.0f}",
        f"{((realistic - last_real) / last_real * 100):+.1f}%",
        help="Prévision centrale du modèle"
    )
    
    # Scénario optimiste (borne haute)
    optimistic = forecast_fresh["upper_bound"].sum()
    scenario_cols[2].metric(
        "😃 Scénario Optimiste",
        f"${optimistic:,.0f}",
        f"{((optimistic - last_real) / last_real * 100):+.1f}%",
        help="Borne haute de l'intervalle de confiance 95%"
    )

    # Tableau forecast
    with st.expander("📋 Voir le tableau détaillé des prévisions"):
        forecast_table = forecast_fresh.copy()
        forecast_table["scenario_pessimiste"] = forecast_table["lower_bound"]
        forecast_table["scenario_realiste"] = forecast_table["predicted_sales"]
        forecast_table["scenario_optimiste"] = forecast_table["upper_bound"]
        
        st.dataframe(
            forecast_table[["date", "scenario_pessimiste", "scenario_realiste", "scenario_optimiste"]].rename(columns={
                "date": "Mois",
                "scenario_pessimiste": "Pessimiste ($)",
                "scenario_realiste": "Réaliste ($)",
                "scenario_optimiste": "Optimiste ($)"
            }).style.format({
                "Pessimiste ($)": "${:,.0f}",
                "Réaliste ($)": "${:,.0f}",
                "Optimiste ($)": "${:,.0f}"
            }),
            use_container_width=True,
            hide_index=True
        )

# ══════════════════════════════════════════
# PAGE 3 — CLIENTS & RFM
# ══════════════════════════════════════════
elif page == "👥 Analyse Clients & RFM":
    st.title("👥 Analyse Clients & Segmentation RFM")
    st.caption("8 segments actionnables · Pareto · Actions recommandées")
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
    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("👥 Clients total", f"{len(rfm_df):,}")
    r2.metric("🏆 Champions",
              f"{len(rfm_df[rfm_df['segment']=='Champions']):,}",
              f"{len(rfm_df[rfm_df['segment']=='Champions'])/len(rfm_df)*100:.1f}%")
    r3.metric("⚠️ At Risk",
              f"{len(rfm_df[rfm_df['segment']=='At Risk']):,}",
              f"{len(rfm_df[rfm_df['segment']=='At Risk'])/len(rfm_df)*100:.1f}%")
    cant_lose_count = len(rfm_df[rfm_df['segment']=="Can't Lose Them"])
    r4.metric("🚨 Can't Lose", f"{cant_lose_count:,}",
              f"{cant_lose_count/len(rfm_df)*100:.1f}%")
    
    # Valeur à risque
    at_risk_value = rfm_df[rfm_df['segment'].isin(['At Risk', "Can't Lose Them"])]['monetary'].sum()
    r5.metric("💰 Valeur à risque", f"${at_risk_value:,.0f}",
              help="Valeur totale des segments At Risk + Can't Lose Them")
    
    st.markdown("---")
    
    # Actions recommandées par segment
    st.subheader("🎯 Actions Recommandées par Segment")
    actions_map = {
        "Champions": "🏆 Fidéliser avec programmes VIP, early access, récompenses exclusives",
        "Loyal Customers": "💎 Développer avec upsell, cross-sell, programmes de parrainage",
        "Potential Loyalists": "⭐ Augmenter la fréquence avec offres ciblées et engagement",
        "At Risk": "⚠️ URGENT - Campagne de réactivation, enquête satisfaction, offres personnalisées",
        "New Customers": "🆕 Onboarder avec welcome pack, tutoriels, support prioritaire",
        "Can't Lose Them": "🚨 CRITIQUE - Contact direct, offre spéciale, account manager dédié",
        "Hibernating": "😴 Réactivation douce avec newsletter, nouveautés, petites remises",
        "Lost": "💤 Faible priorité - Campagne win-back à faible coût si ROI positif"
    }
    
    action_cols = st.columns(2)
    for idx, (segment, action) in enumerate(actions_map.items()):
        col = action_cols[idx % 2]
        segment_count = len(rfm_df[rfm_df['segment'] == segment])
        segment_value = rfm_df[rfm_df['segment'] == segment]['monetary'].sum()
        
        with col:
            with st.expander(f"{segment} ({segment_count} clients - ${segment_value:,.0f})"):
                st.write(action)
    
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

    # Valeur par segment (Pareto amélioré)
    st.subheader("💰 Valeur Totale par Segment (Analyse Pareto)")
    seg_value = (rfm_df.groupby("segment")["monetary"]
                 .sum().reset_index()
                 .sort_values("monetary", ascending=False))
    seg_value["pct"] = (seg_value["monetary"] /
                        seg_value["monetary"].sum() * 100).round(1)
    seg_value["cumul_pct"] = seg_value["pct"].cumsum()
    seg_value["color"] = seg_value["segment"].map(colors_map)

    fig = go.Figure()
    
    # Barres de valeur
    fig.add_trace(go.Bar(
        x=seg_value["segment"], y=seg_value["monetary"],
        name="Valeur ($)",
        marker_color=seg_value["segment"].map(colors_map),
        text=seg_value["pct"].apply(lambda x: f"{x}%"),
        textposition="outside",
        yaxis="y"
    ))
    
    # Ligne cumulative
    fig.add_trace(go.Scatter(
        x=seg_value["segment"], y=seg_value["cumul_pct"],
        name="Cumul %",
        mode="lines+markers",
        line=dict(color="#EF553B", width=2),
        marker=dict(size=8),
        yaxis="y2"
    ))
    
    # Ligne 80% (sur le deuxième axe Y)
    fig.add_shape(
        type="line",
        x0=-0.5, x1=len(seg_value)-0.5,
        y0=80, y1=80,
        yref="y2",
        line=dict(color="red", width=2, dash="dash")
    )
    fig.add_annotation(
        x=len(seg_value)-1, y=80,
        yref="y2",
        text="80%",
        showarrow=False,
        xanchor="left"
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=0,r=0,t=30,b=0),
        yaxis=dict(title="Valeur totale ($)", tickformat="$,.0f"),
        yaxis2=dict(title="Cumul (%)", overlaying="y", side="right", range=[0, 100]),
        legend=dict(orientation="h", y=1.1),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Insight Pareto
    pareto_80 = seg_value[seg_value["cumul_pct"] <= 80]
    st.info(f"📊 **{len(pareto_80)} segments** génèrent **80%** de la valeur : {', '.join(pareto_80['segment'].tolist())}")
    
    st.markdown("---")
    
    # Matrice RFM
    st.subheader("🔥 Matrice RFM (Heatmap)")
    
    # Créer la matrice
    rfm_matrix = rfm_df.groupby(['R_score', 'F_score']).agg({
        'customer_id': 'count',
        'monetary': 'sum'
    }).reset_index()
    rfm_matrix.columns = ['Recency', 'Frequency', 'Clients', 'Valeur']
    
    # Pivot pour heatmap
    matrix_pivot = rfm_matrix.pivot(index='Frequency', columns='Recency', values='Clients')
    
    fig = px.imshow(
        matrix_pivot,
        labels=dict(x="Recency Score", y="Frequency Score", color="Nombre de clients"),
        x=[4, 3, 2, 1],
        y=[1, 2, 3, 4],
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )
    fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("💡 Vert = Beaucoup de clients · Rouge = Peu de clients · Haut-Droite = Meilleurs clients")
    
    st.markdown("---")

    # Filtre segment
    st.subheader("🔍 Explorer un Segment")
    seg_select = st.selectbox("Choisir un segment", sorted(rfm_df["segment"].unique()))
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
    st.caption("Random Forest · ROC-AUC 0.983 · 23 features")
    st.markdown("---")

    # KPIs
    n_total    = len(df_scored)
    n_risk     = (df_scored["profit_predicted"] == 0).sum()
    pct_risk   = n_risk / n_total * 100
    avg_proba  = df_scored["profit_proba"].mean()
    
    # Calcul des métriques de performance
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    accuracy = accuracy_score(df_scored["is_profitable"], df_scored["profit_predicted"])
    precision = precision_score(df_scored["is_profitable"], df_scored["profit_predicted"])
    recall = recall_score(df_scored["is_profitable"], df_scored["profit_predicted"])
    f1 = f1_score(df_scored["is_profitable"], df_scored["profit_predicted"])

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("🎯 Accuracy", f"{accuracy*100:.1f}%",
              help="Pourcentage de prédictions correctes")
    m2.metric("🎯 Precision", f"{precision*100:.1f}%",
              help="Parmi les prédictions 'rentable', combien le sont vraiment")
    m3.metric("🎯 Recall", f"{recall*100:.1f}%",
              help="Parmi les commandes rentables, combien sont détectées")
    m4.metric("🎯 F1-Score", f"{f1*100:.1f}%",
              help="Moyenne harmonique de Precision et Recall")
    m5.metric("⚠️ À risque", f"{n_risk:,}",
              f"{pct_risk:.1f}%")
    
    st.markdown("---")
    
    # Matrice de confusion
    col_conf1, col_conf2 = st.columns([1, 1])
    
    with col_conf1:
        st.subheader("📊 Matrice de Confusion")
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(df_scored["is_profitable"], df_scored["profit_predicted"])
        
        # Créer la heatmap
        fig = px.imshow(
            cm,
            labels=dict(x="Prédit", y="Réel", color="Nombre"),
            x=["Non Rentable", "Rentable"],
            y=["Non Rentable", "Rentable"],
            color_continuous_scale="Blues",
            text_auto=True,
            aspect="auto"
        )
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        # Explication
        tn, fp, fn, tp = cm.ravel()
        st.caption(f"✅ Vrais Positifs: {tp:,} · ✅ Vrais Négatifs: {tn:,}")
        st.caption(f"❌ Faux Positifs: {fp:,} · ❌ Faux Négatifs: {fn:,}")
    
    with col_conf2:
        st.subheader("🎯 Feature Importance (Top 10)")
        # Charger le modèle pour obtenir les importances
        try:
            import joblib
            rf_model = joblib.load("ml/saved_models/rf_classifier.pkl")
            feature_cols = joblib.load("ml/saved_models/feature_cols.pkl")
            
            # Créer DataFrame des importances
            importance_df = pd.DataFrame({
                'feature': feature_cols,
                'importance': rf_model.feature_importances_
            }).sort_values('importance', ascending=False).head(10)
            
            fig = px.bar(
                importance_df,
                x='importance', y='feature',
                orientation='h',
                color='importance',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                            coloraxis_showscale=False,
                            yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption(f"💡 **{importance_df.iloc[0]['feature']}** est la feature la plus importante")
        except Exception as e:
            st.info("Feature importance non disponible")
    
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

    # Analyse détaillée par catégorie
    st.subheader("📊 Analyse de Risque par Catégorie")
    risk_by_cat = df_scored.groupby("category").agg(
        total=("profit_predicted", "count"),
        at_risk=("profit_predicted", lambda x: (x==0).sum()),
        avg_proba=("profit_proba", "mean"),
        total_sales=("sales", "sum")
    ).reset_index()
    risk_by_cat["pct_risk"] = (risk_by_cat["at_risk"] / risk_by_cat["total"] * 100).round(1)
    risk_by_cat = risk_by_cat.sort_values("pct_risk", ascending=False)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=risk_by_cat["category"],
        y=risk_by_cat["pct_risk"],
        name="% à risque",
        marker_color=risk_by_cat["pct_risk"],
        marker=dict(
            colorscale=[[0, "#00CC96"], [0.5, "#FFA15A"], [1, "#EF553B"]],
            cmin=0, cmax=50
        ),
        text=risk_by_cat["pct_risk"].apply(lambda x: f"{x}%"),
        textposition="outside"
    ))
    fig.update_layout(height=300, margin=dict(l=0,r=0,t=30,b=0),
                     yaxis_title="% commandes à risque")
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
    st.caption("Isolation Forest · 5% contamination · Patterns · Impact business")
    st.markdown("---")

    anomalies = df_anomalies[df_anomalies["is_anomaly"]]
    normal = df_anomalies[~df_anomalies["is_anomaly"]]

    # KPIs améliorés
    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric("🚨 Anomalies", f"{len(anomalies):,}",
              f"{len(anomalies)/len(df_anomalies)*100:.1f}%")
    
    total_loss = anomalies[anomalies["profit"] < 0]["profit"].sum()
    a2.metric("💸 Perte totale", f"${abs(total_loss):,.0f}",
              help="Somme des pertes sur les anomalies déficitaires")
    
    a3.metric("📉 Profit moy.", f"${anomalies['profit'].mean():.0f}",
              f"vs ${normal['profit'].mean():.0f} normal")
    
    a4.metric("🎯 Remise moy.", f"{anomalies['discount'].mean()*100:.0f}%",
              f"vs {normal['discount'].mean()*100:.0f}% normal")
    
    avg_sales_anom = anomalies["sales"].mean()
    avg_sales_norm = normal["sales"].mean()
    a5.metric("💰 Ventes moy.", f"${avg_sales_anom:,.0f}",
              f"{((avg_sales_anom - avg_sales_norm) / avg_sales_norm * 100):+.1f}%")
    
    st.markdown("---")
    
    # Évolution temporelle des anomalies
    st.subheader("📈 Évolution Temporelle des Anomalies")
    
    # Grouper par mois
    anomalies_temp = df_anomalies.copy()
    anomalies_temp["month"] = pd.to_datetime(anomalies_temp["order_date"]).dt.to_period("M")
    
    monthly_anom = anomalies_temp.groupby("month").agg(
        total=("is_anomaly", "count"),
        anomalies=("is_anomaly", "sum")
    ).reset_index()
    monthly_anom["pct_anomalies"] = (monthly_anom["anomalies"] / monthly_anom["total"] * 100).round(1)
    monthly_anom["month"] = monthly_anom["month"].dt.to_timestamp()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_anom["month"], y=monthly_anom["anomalies"],
        mode="lines+markers", name="Nombre d'anomalies",
        line=dict(color="#EF553B", width=2),
        yaxis="y"
    ))
    fig.add_trace(go.Scatter(
        x=monthly_anom["month"], y=monthly_anom["pct_anomalies"],
        mode="lines+markers", name="% d'anomalies",
        line=dict(color="#FFA15A", width=2, dash="dash"),
        yaxis="y2"
    ))
    fig.update_layout(
        height=300,
        margin=dict(l=0,r=0,t=10,b=0),
        hovermode="x unified",
        yaxis=dict(title="Nombre d'anomalies"),
        yaxis2=dict(title="% d'anomalies", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Insight temporel
    max_month = monthly_anom.loc[monthly_anom["anomalies"].idxmax(), "month"].strftime("%B %Y")
    max_count = monthly_anom["anomalies"].max()
    st.info(f"📊 Pic d'anomalies en **{max_month}** avec **{max_count:.0f}** anomalies détectées")
    
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
    
    st.markdown("---")
    
    # Patterns d'anomalies
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🔍 Top 10 Produits Anormaux")
        top_anom_products = (anomalies.groupby("product_name")
                            .agg(count=("order_id", "count"),
                                 total_loss=("profit", "sum"))
                            .reset_index()
                            .sort_values("count", ascending=False)
                            .head(10))
        
        fig = px.bar(top_anom_products, x="count", y="product_name",
                    orientation="h",
                    color="total_loss",
                    color_continuous_scale=["#EF553B", "#FFA15A", "#636EFA"],
                    labels={"count": "Nombre d'anomalies",
                           "product_name": "Produit",
                           "total_loss": "Perte totale ($)"})
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=10,b=0),
                         yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.subheader("👥 Top 10 Clients Anormaux")
        top_anom_customers = (anomalies.groupby("customer_name")
                             .agg(count=("order_id", "count"),
                                  total_loss=("profit", "sum"))
                             .reset_index()
                             .sort_values("count", ascending=False)
                             .head(10))
        
        fig = px.bar(top_anom_customers, x="count", y="customer_name",
                    orientation="h",
                    color="total_loss",
                    color_continuous_scale=["#EF553B", "#FFA15A", "#636EFA"],
                    labels={"count": "Nombre d'anomalies",
                           "customer_name": "Client",
                           "total_loss": "Perte totale ($)"})
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=10,b=0),
                         yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Distribution des remises dans les anomalies
    st.subheader("🎯 Distribution des Remises (Anomalies vs Normal)")
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=normal["discount"] * 100,
        name="Commandes normales",
        marker_color="#636EFA",
        opacity=0.7,
        nbinsx=30
    ))
    fig.add_trace(go.Histogram(
        x=anomalies["discount"] * 100,
        name="Anomalies",
        marker_color="#EF553B",
        opacity=0.7,
        nbinsx=30
    ))
    fig.update_layout(
        height=300,
        margin=dict(l=0,r=0,t=10,b=0),
        barmode="overlay",
        xaxis_title="Remise (%)",
        yaxis_title="Nombre de commandes",
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("💡 Les anomalies ont tendance à avoir des remises plus élevées")

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

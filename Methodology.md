
## 3.0 Complete Methodology Flow Diagram

```
╔════════════════════════════════════════════════════════════════════════════════════╗
║                        MBU GAP ANALYZER - COMPLETE WORKFLOW                        ║
╚════════════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: DATA ACQUISITION & PREPROCESSING                                          │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
        ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
        │   ENROLMENT DATA  │ │  BIOMETRIC DATA   │ │ DEMOGRAPHIC DATA  │
        │   1,006,029 rows  │ │  1,861,108 rows   │ │  2,071,700 rows   │
        └─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘
                  │                     │                     │
                  │  Load Multiple CSV  │  Load Multiple CSV  │  Load Multiple CSV
                  │  Files & Concat     │  Files & Concat     │  Files & Concat
                  │                     │                     │
                  ▼                     ▼                     ▼
        ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
        │ Date Parsing      │ │ Date Parsing      │ │ Date Parsing      │
        │ • DD-MM-YYYY      │ │ • DD-MM-YYYY      │ │ • DD-MM-YYYY      │
        │ • Extract: Year   │ │ • Extract: Year   │ │ • Extract: Year   │
        │           Month   │ │           Month   │ │           Month   │
        │      Year_Month   │ │      Year_Month   │ │      Year_Month   │
        └─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘
                  │                     │                     │
                  └─────────────────────┼─────────────────────┘
                                        ▼
                            ┌───────────────────────┐
                            │  Feature Engineering  │
                            │  • State aggregation  │
                            │  • District rollup    │
                            │  • Handle nulls       │
                            └───────────┬───────────┘
                                        │
┌───────────────────────────────────────┼───────────────────────────────────────────┐
│ PHASE 2: GAP ANALYSIS & RISK CALCULATION                                         │
└───────────────────────────────────────┼───────────────────────────────────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
        ┌───────────────────────┐               ┌───────────────────────┐
        │ Aggregate Enrolments  │               │ Aggregate Bio Updates │
        │ by District           │               │ by District           │
        │ • age_0_5             │               │ • bio_age_5_17        │
        │ • age_5_17            │               │ • bio_age_17_         │
        └───────────┬───────────┘               └───────────┬───────────┘
                    │                                       │
                    │ Calculate MBU_ELIGIBLE                │
                    │ = age_0_5 + age_5_17                  │
                    │                                       │
                    └───────────────────┬───────────────────┘
                                        │
                                        ▼
                            ┌───────────────────────┐
                            │  MERGE ON            │
                            │  [state, district]   │
                            └───────────┬───────────┘
                                        │
                                        ▼
                            ┌───────────────────────────────────┐
                            │  CALCULATE KEY METRICS            │
                            │                                   │
                            │  MBU_GAP =                        │
                            │    mbu_eligible - bio_age_5_17    │
                            │                                   │
                            │  COMPLIANCE_RATIO =               │
                            │    (bio_age_5_17/mbu_eligible)×100│
                            └───────────┬───────────────────────┘
                                        │
                                        ▼
                            ┌───────────────────────────────────┐
                            │  RISK CLASSIFICATION              │
                            │                                   │
                            │  >= 80% → Green (Compliant)       │
                            │  50-79% → Yellow (Moderate)       │
                            │  < 50%  → Red (Service Desert)    │
                            └───────────┬───────────────────────┘
                                        │
┌───────────────────────────────────────┼───────────────────────────────────────────┐
│ PHASE 3: MACHINE LEARNING - SERVICE DESERT IDENTIFICATION                        │
└───────────────────────────────────────┼───────────────────────────────────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────────┐
                        │  FEATURE PREPARATION              │
                        │  • mbu_eligible                   │
                        │  • bio_age_5_17                   │
                        │  • mbu_gap                        │
                        │  • mbu_compliance_ratio           │
                        └───────────┬───────────────────────┘
                                    │
                                    ▼
                        ┌───────────────────────────────────┐
                        │  STANDARDIZATION                  │
                        │  StandardScaler()                 │
                        │  • Mean = 0                       │
                        │  • Std Dev = 1                    │
                        └───────────┬───────────────────────┘
                                    │
                                    ▼
                        ┌───────────────────────────────────┐
                        │  K-MEANS CLUSTERING               │
                        │  • n_clusters = 4                 │
                        │  • random_state = 42              │
                        │  • Elbow Method optimization      │
                        └───────────┬───────────────────────┘
                                    │
                                    ▼
                        ┌───────────────────────────────────┐
                        │  CLUSTER INTERPRETATION           │
                        │  Map clusters to risk levels      │
                        │  Identify Service Desert clusters │
                        └───────────┬───────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────────────────┐
│ PHASE 4: DEEP LEARNING - LSTM TIME SERIES FORECASTING                            │
└───────────────────────────────────┼───────────────────────────────────────────────┘
                                    │
                ┌───────────────────┴───────────────────┐
                ▼                                       ▼
    ┌─────────────────────────┐         ┌─────────────────────────┐
    │  TIME SERIES DATA PREP  │         │  SEQUENCE CREATION      │
    │  • Daily aggregation    │         │  • Lookback = 30 days   │
    │  • Sort by date         │         │  • Sliding window       │
    │  • Fill missing dates   │         │  • Train/Test split 80% │
    └────────────┬────────────┘         └────────────┬────────────┘
                 │                                   │
                 └───────────────┬───────────────────┘
                                 ▼
                    ┌────────────────────────────────┐
                    │  LSTM MODEL ARCHITECTURE       │
                    │                                │
                    │  Input Layer (1 feature)       │
                    │         ↓                      │
                    │  LSTM Layer 1 (64 units)       │
                    │         ↓                      │
                    │  LSTM Layer 2 (64 units)       │
                    │         ↓                      │
                    │  Dropout (0.2)                 │
                    │         ↓                      │
                    │  Dense (32 units + ReLU)       │
                    │         ↓                      │
                    │  Dropout (0.2)                 │
                    │         ↓                      │
                    │  Output Layer (1 unit)         │
                    └────────────┬───────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────────┐
                    │  TRAINING CONFIGURATION        │
                    │  • Optimizer: Adam (lr=0.001)  │
                    │  • Loss: MSE                   │
                    │  • Epochs: 100                 │
                    │  • Batch Size: 32              │
                    │  • LR Scheduler: ReduceLR      │
                    └────────────┬───────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────────┐
                    │  FORECAST GENERATION           │
                    │  • 6-month prediction          │
                    │  • Identify peak demand        │
                    │  • School admission rush alert │
                    └────────────┬───────────────────┘
                                 │
┌────────────────────────────────┼────────────────────────────────────────────────┐
│ PHASE 5: ANOMALY DETECTION - AUTOENCODER                                        │
└────────────────────────────────┼────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────────┐
                    │  AUTOENCODER ARCHITECTURE      │
                    │                                │
                    │  ENCODER:                      │
                    │    Input (4) → Dense(32)       │
                    │            → ReLU              │
                    │            → Dense(16)         │
                    │            → ReLU              │
                    │            → Dense(8)          │
                    │                                │
                    │  DECODER:                      │
                    │    Dense(8) → Dense(16)        │
                    │            → ReLU              │
                    │            → Dense(32)         │
                    │            → ReLU              │
                    │            → Dense(4) Output   │
                    └────────────┬───────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────────┐
                    │  RECONSTRUCTION ERROR          │
                    │  error = MSE(input, output)    │
                    │                                │
                    │  THRESHOLD:                    │
                    │  μ + 2σ                        │
                    └────────────┬───────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────────┐
                    │  ANOMALY FLAGGING              │
                    │  Districts with error > thresh │
                    │  → Suspicious patterns detected│
                    └────────────┬───────────────────┘
                                 │
┌────────────────────────────────┼────────────────────────────────────────────────┐
│ PHASE 6: EXPLAINABLE AI - SHAP ANALYSIS                                         │
└────────────────────────────────┼────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────────┐
                    │  SHAP KERNEL EXPLAINER         │
                    │  • Background samples: 100     │
                    │  • Explain K-Means decisions   │
                    │  • Feature importance ranking  │
                    └────────────┬───────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────────┐
                    │  FEATURE IMPORTANCE            │
                    │                                │
                    │  1. Compliance Ratio (0.194)   │
                    │  2. Bio Updates (0.175)        │
                    │  3. MBU Gap (0.062)            │
                    │  4. MBU Eligible (0.012)       │
                    └────────────┬───────────────────┘
                                 │
┌────────────────────────────────┼────────────────────────────────────────────────┐
│ PHASE 7: VISUALIZATION & REPORTING                                              │
└────────────────────────────────┼────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ PLOTLY CHARTS    │  │ FOLIUM MAP       │  │ CSV EXPORTS      │
│ • Bar charts     │  │ • Geospatial viz │  │ • Gap analysis   │
│ • Treemaps       │  │ • State markers  │  │ • Service deserts│
│ • Scatter plots  │  │ • Risk coloring  │  │ • Ghost cohorts  │
│ • Time series    │  │ • Interactive    │  │ • Summaries      │
│ • Forecasts      │  │   popups         │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 ▼
                    ┌────────────────────────────────┐
                    │  FINAL OUTPUTS                 │
                    │  • 6 Interactive HTML charts   │
                    │  • 1 Interactive map           │
                    │  • 4 CSV reports               │
                    │  • Policy recommendations      │
                    └────────────────────────────────┘

╔════════════════════════════════════════════════════════════════════════════════════╗
║  KEY OUTPUTS:                                                                      ║
║  ✓ 147 Service Desert districts identified                                        ║
║  ✓ 177,900 children at risk of benefit loss                                       ║
║  ✓ Rs. 42.69 Crore financial impact quantified                                    ║
║  ✓ 6-month demand forecast for resource planning                                  ║
║  ✓ 21 anomalous districts flagged for investigation                               ║
╚════════════════════════════════════════════════════════════════════════════════════╝
```
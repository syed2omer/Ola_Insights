# 🚗 OLA Ride Insights Dashboard

An interactive data analytics dashboard built with **Streamlit** and **Plotly** analyzing OLA ride-sharing data from July 2024 (Bangalore).

## 🔗 Live App
> Deployed on Streamlit Cloud — accessible by anyone, no setup needed.

## 📊 Features

| Page | Description |
|------|-------------|
| 🏠 Overall | KPI cards, daily ride volume, booking status breakdown |
| 🚘 Vehicle Type | Ride distance, booking count, revenue by vehicle |
| 💰 Revenue | Payment methods, top customers, revenue trends |
| ❌ Cancellation | Customer & driver cancellation reasons analysis |
| ⭐ Ratings | Driver vs customer ratings, distributions by vehicle |
| 🔍 SQL Queries | All 10 project SQL queries run live on the dataset |

## 🛠 Tech Stack
- Python, Pandas
- Streamlit
- Plotly Express
- MySQL (local development)

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Project Structure
```
OLA_Ride_Insights/
├── app.py                  # Streamlit app
├── OLA_DataSet.xlsx        # Dataset (July 2024)
├── requirements.txt        # Dependencies
└── README.md
```

## 💡 Key Insights
- 63,967 out of 103,024 rides were successful (62% success rate)
- Cash and UPI are the dominant payment methods
- "Driver not moving towards pickup" is the top customer cancellation reason
- Auto rides have the shortest avg distance; Prime Sedan has the longest

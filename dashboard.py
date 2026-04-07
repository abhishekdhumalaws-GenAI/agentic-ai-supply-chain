import streamlit as st
import boto3
import pandas as pd

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('supply_chain_results')

st.title("📊 Supply Chain AI Dashboard")

response = table.scan()
items = response.get("Items", [])

df = pd.DataFrame(items)

if not df.empty:
    st.dataframe(df)

    st.subheader("Stockout Risks")
    st.bar_chart(df['stockout_risk'].value_counts())

    st.subheader("AI Reasons")
    st.write(df[['product_id', 'ai_reason']])
else:
    st.write("No data available")

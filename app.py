import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Local Food Wastage Management System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Database Connection
import streamlit as st
import psycopg2

# ===========================
# Database Connection (Neon)
# ===========================

conn = psycopg2.connect(
    host="ep-wispy-haze-ao0lqvsm.c-2.ap-southeast-1.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password=st.secrets["DB_PASSWORD"],
    sslmode="require"
)

cursor = conn.cursor()
cursor.execute('SET search_path TO "Food_wastage_mngnt_Sys";')
cursor.close()

# -----------------------------
# Dashboard Metrics
# -----------------------------

providers_count = pd.read_sql(
    'SELECT COUNT(*) FROM "Food_wastage_mngnt_Sys".providers',
    conn
).iloc[0, 0]

receivers_count = pd.read_sql(
    'SELECT COUNT(*) FROM "Food_wastage_mngnt_Sys".receivers',
    conn
).iloc[0, 0]

food_count = pd.read_sql(
    'SELECT COUNT(*) FROM "Food_wastage_mngnt_Sys".food_listings',
    conn
).iloc[0, 0]

claims_count = pd.read_sql(
    'SELECT COUNT(*) FROM "Food_wastage_mngnt_Sys".claims',
    conn
).iloc[0, 0]

# -----------------------------
# Title
# -----------------------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Dashboard",
    "🍱 Food Listings",
    "👨‍💼 Providers",
    "📊 SQL Analysis",
    "📈 Charts",
    "🛠 CRUD"
])

# -----------------------------
# Metrics
# -----------------------------
with tab1:

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Providers", providers_count)

    with col2:
        st.metric("Receivers", receivers_count)

    with col3:
        st.metric("Food Listings", food_count)

    with col4:
        st.metric("Claims", claims_count)
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.success("✅ Database Connected")
        st.info(f"📦 Total Food Quantity : {pd.read_sql('SELECT SUM(quantity) FROM food_listings', conn).iloc[0,0]}")

    with col2:
        st.info(f"🏙️ Cities Covered : {pd.read_sql('SELECT COUNT(DISTINCT city) FROM providers', conn).iloc[0,0]}")
        st.info(f"🍽️ Food Types : {pd.read_sql('SELECT COUNT(DISTINCT food_type) FROM food_listings', conn).iloc[0,0]}")
    st.divider()

    st.markdown("### 📋 Project Information")

    st.write("**Project:** Local Food Wastage Management System")
    st.write("**Database:** PostgreSQL")
    st.write("**Frontend:** Streamlit")
    st.write("**Current Date & Time:**", datetime.now().strftime("%d-%m-%Y %I:%M %p"))


with tab2:

    st.subheader("🍱 Food Listings")

    food_types = pd.read_sql(
        "SELECT DISTINCT food_type FROM food_listings ORDER BY food_type",
        conn
    )

    meal_types = pd.read_sql(
        "SELECT DISTINCT meal_type FROM food_listings ORDER BY meal_type",
        conn
    )

    selected_food_type = st.selectbox(
        "Food Type",
        ["All"] + food_types["food_type"].tolist(),
        key="food_type"
    )

    selected_meal_type = st.selectbox(
        "Meal Type",
        ["All"] + meal_types["meal_type"].tolist(),
        key="meal_type"
    )
    search_food = st.text_input(
        "🔍 Search Food Name",
        placeholder="Enter food name..."
    )
    query = """
    SELECT *
    FROM food_listings
    WHERE 1=1
    """

    if search_food:
        query += f" AND food_name ILIKE '%{search_food}%'"

    if selected_food_type != "All":
        query += f" AND food_type = '{selected_food_type}'"

    if selected_meal_type != "All":
        query += f" AND meal_type = '{selected_meal_type}'"

    food_df = pd.read_sql(query, conn)

    st.dataframe(food_df, use_container_width=True)

with tab3:

    st.subheader("👨‍💼 Providers")

    cities = pd.read_sql(
        "SELECT DISTINCT city FROM providers ORDER BY city",
        conn
    )

    selected_city = st.selectbox(
        "City",
        ["All"] + cities["city"].tolist(),
        key="city"
    )

    search_provider = st.text_input(
        "🔍 Search Provider Name",
        placeholder="Enter provider name..."
    )
    query = """
    SELECT provider_id,
           name,
           city,
           contact
    FROM providers
    """

    conditions = []

    if search_provider:
        conditions.append(f"name ILIKE '%{search_provider}%'")

    if selected_city != "All":
        conditions.append(f"city = '{selected_city}'")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    provider_df = pd.read_sql(query, conn)

    st.dataframe(
        provider_df,
        use_container_width=True
    )

with tab4:

    st.subheader("📊 SQL Analysis")

    query_options = {
        "1. Providers and Receivers in Each City":
        """
        SELECT
            COALESCE(p.city,r.city) AS city,
            COALESCE(no_of_providers,0) AS no_of_providers,
            COALESCE(no_of_receivers,0) AS no_of_receivers
        FROM
            (SELECT city, COUNT(*) AS no_of_providers
            FROM providers
            GROUP BY city) p
        FULL OUTER JOIN
            (SELECT city, COUNT(*) AS no_of_receivers
            FROM receivers
            GROUP BY city) r
        ON p.city=r.city
        ORDER BY city;
        """,

        "2. Provider Type Contribution":
        """
        SELECT
            provider_type,
            SUM(quantity) AS total_quantity
        FROM food_listings
        GROUP BY provider_type
        ORDER BY total_quantity DESC;
        """,

        "3. Provider Contact Information":
        """
        SELECT
            provider_id,
            name,
            city,
            contact
        FROM providers;
        """,

        "4. Receiver With Most Claims":
        """
        SELECT
            r.name,
            COUNT(c.claim_id) AS no_of_claims
        FROM receivers r
        JOIN claims c
        ON r.receiver_id=c.receiver_id
        GROUP BY r.name
        ORDER BY no_of_claims DESC
        LIMIT 1;
        """,

        "5. Total Quantity of Food Available":
        """
        SELECT
            SUM(quantity) AS total_quantity_of_food
        FROM food_listings;
        """,

        "6. City With Highest Number of Food Listings":
        """
        SELECT
            location,
            COUNT(food_id) AS no_of_food_listings
        FROM food_listings
        GROUP BY location
        ORDER BY no_of_food_listings DESC
        LIMIT 1;
        """,

        "7. Most Commonly Available Food Types":
        """
        SELECT
            food_type,
            COUNT(food_id) AS total_listings
        FROM food_listings
        GROUP BY food_type
        ORDER BY total_listings DESC;
        """,

        "8. Number of Claims for Each Food Item":
        """
        SELECT
            f.food_name,
            COUNT(c.food_id) AS no_of_claims
        FROM food_listings f
        JOIN claims c
        ON f.food_id = c.food_id
        GROUP BY f.food_name
        ORDER BY no_of_claims DESC;
        """,

        "9. Provider With Highest Successful Claims":
        """
        SELECT
            p.name,
            COUNT(c.claim_id)
            FILTER (WHERE c.status='Completed')
            AS no_of_successful_claims
        FROM providers p
        JOIN food_listings f
        ON p.provider_id=f.provider_id
        JOIN claims c
        ON f.food_id=c.food_id
        GROUP BY p.provider_id,p.name
        ORDER BY no_of_successful_claims DESC
        LIMIT 1;
        """,
        "10. Claim Status Percentage":
        """
        SELECT
            ROUND(
                COUNT(*) FILTER (WHERE status='Completed')::numeric /
                COUNT(*) * 100,2
            ) AS completed_percentage,

            ROUND(
                COUNT(*) FILTER (WHERE status='Pending')::numeric /
                COUNT(*) * 100,2
            ) AS pending_percentage,

            ROUND(
                COUNT(*) FILTER (WHERE status='Cancelled')::numeric /
                COUNT(*) * 100,2
            ) AS cancelled_percentage
        FROM claims;
        """,

        "11. Average Quantity Claimed Per Receiver":
        """
        SELECT
            r.name,
            ROUND(AVG(f.quantity),2) AS avg_quantity_of_food_claimed
        FROM receivers r
        JOIN claims c
        ON r.receiver_id = c.receiver_id
        JOIN food_listings f
        ON c.food_id = f.food_id
        GROUP BY
            r.receiver_id,
            r.name
        ORDER BY avg_quantity_of_food_claimed DESC;
        """,

        "12. Most Claimed Meal Type":
        """
        SELECT
            f.meal_type,
            COUNT(c.claim_id) AS no_of_claims
        FROM food_listings f
        JOIN claims c
        ON f.food_id = c.food_id
        GROUP BY f.meal_type
        ORDER BY no_of_claims DESC
        LIMIT 1;
        """,

        "13. Total Quantity Donated By Each Provider":
        """
        SELECT
            p.provider_id,
            p.name,
            COALESCE(SUM(f.quantity),0) AS total_quantity_of_food_donated
        FROM providers p
        LEFT JOIN food_listings f
        ON p.provider_id = f.provider_id
        GROUP BY
            p.provider_id,
            p.name
        ORDER BY total_quantity_of_food_donated DESC;
        """
        
    }

    selected_query = st.selectbox(
        "Select SQL Analysis",
        list(query_options.keys())
    )

    result_df = pd.read_sql(
        query_options[selected_query],
        conn
    )

    st.dataframe(
        result_df,
        use_container_width=True
    )
    csv = result_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Result as CSV",
        data=csv,
        file_name="sql_analysis_result.csv",
        mime="text/csv"
    )

with tab5:

    st.subheader("📈 Visualizations")

    chart_option = st.selectbox(
        "Select Chart",
        [
            "Food Type Distribution",
            "Meal Type Distribution",
            "Provider Type Contribution",
            "Claim Status Distribution"
        ]
    )

    if chart_option == "Food Type Distribution":

        df = pd.read_sql("""
            SELECT
                food_type,
                COUNT(*) AS count
            FROM food_listings
            GROUP BY food_type
        """, conn)

        fig = px.bar(
            df,
            x="food_type",
            y="count",
            title="Food Type Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    elif chart_option == "Meal Type Distribution":

        df = pd.read_sql("""
            SELECT
                meal_type,
                COUNT(*) AS count
            FROM food_listings
            GROUP BY meal_type
        """, conn)

        fig = px.pie(
            df,
            names="meal_type",
            values="count",
            title="Meal Type Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    elif chart_option == "Provider Type Contribution":

        df = pd.read_sql("""
            SELECT
                provider_type,
                SUM(quantity) AS total_quantity
            FROM food_listings
            GROUP BY provider_type
        """, conn)

        fig = px.bar(
            df,
            x="provider_type",
            y="total_quantity",
            title="Provider Type Contribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    elif chart_option == "Claim Status Distribution":

        df = pd.read_sql("""
            SELECT
                status,
                COUNT(*) AS count
            FROM claims
            GROUP BY status
        """, conn)

        fig = px.pie(
            df,
            names="status",
            values="count",
            title="Claim Status Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)
# =====================================================
# CRUD OPERATIONS
# =====================================================


with tab6:

    st.subheader("🛠 CRUD Operations")

    crud_table = st.selectbox(
        "Select Table",
        ["Food Listings", "Claims"]
    )

    crud_action = st.selectbox(
        "Select Operation",
        ["Add", "Update", "Delete"]
    )

    if crud_table == "Food Listings":

        # ===========================
        # ADD
        # ===========================

        if crud_action == "Add":

            st.markdown("### ➕ Add Food Listing")

            food_name = st.text_input("Food Name")

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                step=1
            )

            expiry_date = st.text_input(
                "Expiry Date (MM/DD/YYYY)",
                placeholder="03/17/2025"
            )

            provider_id = st.number_input(
                "Provider ID",
                min_value=1,
                step=1
            )

            provider_type = st.text_input("Provider Type")

            location = st.text_input("Location")

            food_type = st.selectbox(
                "Food Type",
                ["Vegetarian", "Non-Vegetarian", "Vegan"]
            )

            meal_type = st.selectbox(
                "Meal Type",
                ["Breakfast", "Lunch", "Dinner", "Snacks"]
            )

            if st.button("Add Food"):

                cursor = conn.cursor()

                cursor.execute("""
                    SELECT COALESCE(MAX(food_id),0)+1
                    FROM food_listings
                """)

                new_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO food_listings
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    new_id,
                    food_name,
                    quantity,
                    expiry_date,
                    provider_id,
                    provider_type,
                    location,
                    food_type,
                    meal_type
                ))

                conn.commit()
                cursor.close()

                st.success("✅ Food Listing Added Successfully")
                st.rerun()

        # ===========================
        # UPDATE
        # ===========================

        elif crud_action == "Update":

            st.markdown("### ✏️ Update Food Listing")

            food_ids = pd.read_sql(
                "SELECT food_id FROM food_listings ORDER BY food_id",
                conn
            )

            selected_id = st.selectbox(
                "Select Food ID",
                food_ids["food_id"].tolist()
            )

            food = pd.read_sql(
                f"SELECT * FROM food_listings WHERE food_id={selected_id}",
                conn
            ).iloc[0]

            food_name = st.text_input(
                "Food Name",
                value=food["food_name"]
            )

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                value=int(food["quantity"])
            )

            expiry_date = st.text_input(
                "Expiry Date (MM/DD/YYYY)",
                value=food["expiry_date"]
            )

            provider_id = st.number_input(
                "Provider ID",
                min_value=1,
                value=int(food["provider_id"])
            )

            provider_type = st.text_input(
                "Provider Type",
                value=food["provider_type"]
            )

            location = st.text_input(
                "Location",
                value=food["location"]
            )

            food_type = st.selectbox(
                "Food Type",
                ["Vegetarian", "Non-Vegetarian", "Vegan"],
                index=["Vegetarian","Non-Vegetarian","Vegan"].index(food["food_type"])
            )

            meal_type = st.selectbox(
                "Meal Type",
                ["Breakfast","Lunch","Dinner","Snacks"],
                index=["Breakfast","Lunch","Dinner","Snacks"].index(food["meal_type"])
            )

            if st.button("Update Food"):

                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE food_listings
                    SET food_name=%s,
                        quantity=%s,
                        expiry_date=%s,
                        provider_id=%s,
                        provider_type=%s,
                        location=%s,
                        food_type=%s,
                        meal_type=%s
                    WHERE food_id=%s
                """,
                (
                    food_name,
                    quantity,
                    expiry_date,
                    provider_id,
                    provider_type,
                    location,
                    food_type,
                    meal_type,
                    selected_id
                ))

                conn.commit()
                cursor.close()

                st.success("✅ Food Listing Updated Successfully")
                st.rerun()

        # ===========================
        # DELETE
        # ===========================

        elif crud_action == "Delete":

            st.markdown("### 🗑 Delete Food Listing")

            food_ids = pd.read_sql(
                "SELECT food_id FROM food_listings ORDER BY food_id",
                conn
            )

            selected_id = st.selectbox(
                "Select Food ID",
                food_ids["food_id"].tolist(),
                key="delete_food"
            )

            food = pd.read_sql(
                f"SELECT food_name FROM food_listings WHERE food_id={selected_id}",
                conn
            ).iloc[0]

            st.write(f"**Food Name:** {food['food_name']}")

            if st.button("Delete Food"):

                cursor = conn.cursor()

                cursor.execute(
                    "DELETE FROM food_listings WHERE food_id=%s",
                    (selected_id,)
                )

                conn.commit()
                cursor.close()

                st.success("✅ Food Listing Deleted Successfully")

                st.rerun()
    elif crud_table == "Claims":

        if crud_action == "Add":

            st.markdown("### ➕ Add Claim")

            food_ids = pd.read_sql(
                "SELECT food_id FROM food_listings ORDER BY food_id",
                conn
            )

            receivers = pd.read_sql(
                "SELECT receiver_id FROM receivers ORDER BY receiver_id",
                conn
            )

            food_id = st.selectbox(
                "Food ID",
                food_ids["food_id"].tolist()
            )

            receiver_id = st.selectbox(
                "Receiver ID",
                receivers["receiver_id"].tolist()
            )

            status = st.selectbox(
                "Status",
                ["Pending", "Completed", "Cancelled"]
            )

            timestamp = st.text_input(
                "Timestamp (MM/DD/YYYY HH:MM)",
                placeholder="03/21/2025 10:30"
            )

            if st.button("Add Claim"):

                cursor = conn.cursor()

                cursor.execute("""
                    SELECT COALESCE(MAX(claim_id),0)+1
                    FROM claims
                """)

                new_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO claims
                    VALUES (%s,%s,%s,%s,%s)
                """,
                (
                    new_id,
                    food_id,
                    receiver_id,
                    status,
                    timestamp
                ))

                conn.commit()
                cursor.close()

                st.success("✅ Claim Added Successfully")

                st.rerun()
        elif crud_action == "Update":
            st.markdown("### ✏️ Update Claim")

            claim_ids = pd.read_sql(
                "SELECT claim_id FROM claims ORDER BY claim_id",
                conn
            )

            selected_id = st.selectbox(
                "Select Claim ID",
                claim_ids["claim_id"].tolist(),
                key="update_claim"
            )

            claim = pd.read_sql(
                f"SELECT * FROM claims WHERE claim_id={selected_id}",
                conn
            ).iloc[0]

            food_ids = pd.read_sql(
                "SELECT food_id FROM food_listings ORDER BY food_id",
                conn
            )

            receivers = pd.read_sql(
                "SELECT receiver_id FROM receivers ORDER BY receiver_id",
                conn
            )

            food_id = st.selectbox(
                "Food ID",
                food_ids["food_id"].tolist(),
                index=food_ids["food_id"].tolist().index(claim["food_id"])
            )

            receiver_id = st.selectbox(
                "Receiver ID",
                receivers["receiver_id"].tolist(),
                index=receivers["receiver_id"].tolist().index(claim["receiver_id"])
            )

            status_list = ["Pending", "Completed", "Cancelled"]

            status = st.selectbox(
                "Status",
                status_list,
                index=status_list.index(claim["status"])
            )

            timestamp = st.text_input(
                "Timestamp (MM/DD/YYYY HH:MM)",
                value=claim["timestamp"]
            )

            if st.button("Update Claim"):

                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE claims
                    SET food_id=%s,
                        receiver_id=%s,
                        status=%s,
                        timestamp=%s
                    WHERE claim_id=%s
                """,
                (
                    food_id,
                    receiver_id,
                    status,
                    timestamp,
                    selected_id
                ))

                conn.commit()
                cursor.close()

                st.success("✅ Claim Updated Successfully")

                st.rerun()
        elif crud_action == "Delete":
            st.markdown("### 🗑 Delete Claim")

            claim_ids = pd.read_sql(
                "SELECT claim_id FROM claims ORDER BY claim_id",
                conn
            )

            selected_id = st.selectbox(
                "Select Claim ID",
                claim_ids["claim_id"].tolist(),
                key="delete_claim"
            )

            claim = pd.read_sql(
                f"SELECT * FROM claims WHERE claim_id={selected_id}",
                conn
            ).iloc[0]

            st.write(f"**Food ID:** {claim['food_id']}")
            st.write(f"**Receiver ID:** {claim['receiver_id']}")
            st.write(f"**Status:** {claim['status']}")

            if st.button("Delete Claim"):

                cursor = conn.cursor()

                cursor.execute(
                    "DELETE FROM claims WHERE claim_id=%s",
                    (selected_id,)
                )

                conn.commit()
                cursor.close()

                st.success("✅ Claim Deleted Successfully")

                st.rerun()
st.divider()

st.markdown(
    """
    <div style='text-align:center; color:gray;'>
        <h4>🍽 Local Food Wastage Management System</h4>
        <p>Developed by <b>Sujal Dhiman</b></p>
    </div>
    """,
    unsafe_allow_html=True
)
# Close Connection
conn.close()
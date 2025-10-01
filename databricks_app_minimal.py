"""
Minimal Databricks App - Order Management System
This is the consolidated version with only essential files for Databricks deployment
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import uuid
import os
from typing import Dict, List, Optional

# Configuration
class Config:
    # Databricks Configuration
    DATABRICKS_HOST = os.getenv('DATABRICKS_HOST', 'https://your-workspace.cloud.databricks.com')
    DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN', '')
    DATABRICKS_CLUSTER_ID = os.getenv('DATABRICKS_CLUSTER_ID', '')
    
    # OAuth Configuration (for Databricks Apps)
    DATABRICKS_CLIENT_ID = os.getenv('DATABRICKS_CLIENT_ID', '')
    DATABRICKS_CLIENT_SECRET = os.getenv('DATABRICKS_CLIENT_SECRET', '')
    
    # App Configuration
    APP_NAME = os.getenv('APP_NAME', 'Order Management System')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Delta Table Configuration
    DELTA_TABLE_PATH = "/tmp/delta/order_invoices"
    ORDERS_TABLE_PATH = "/tmp/delta/orders"
    
    @classmethod
    def get_databricks_config(cls):
        """Get Databricks configuration with proper authentication method"""
        config = {'host': cls.DATABRICKS_HOST}
        
        # Prioritize OAuth if client credentials are available
        if cls.DATABRICKS_CLIENT_ID and cls.DATABRICKS_CLIENT_SECRET:
            config.update({
                'client_id': cls.DATABRICKS_CLIENT_ID,
                'client_secret': cls.DATABRICKS_CLIENT_SECRET
            })
            # Clear token to avoid conflicts
            if 'DATABRICKS_TOKEN' in os.environ:
                del os.environ['DATABRICKS_TOKEN']
        elif cls.DATABRICKS_TOKEN:
            config['token'] = cls.DATABRICKS_TOKEN
            # Clear OAuth to avoid conflicts
            for key in ['DATABRICKS_CLIENT_ID', 'DATABRICKS_CLIENT_SECRET']:
                if key in os.environ:
                    del os.environ[key]
        else:
            # Clear any authentication environment variables to avoid conflicts
            for key in ['DATABRICKS_CLIENT_ID', 'DATABRICKS_CLIENT_SECRET', 'DATABRICKS_TOKEN']:
                if key in os.environ:
                    del os.environ[key]
        
        return config

# Mock classes for when Databricks is not available
class MockSparkSession:
    """Mock Spark session for demonstration"""
    def createDataFrame(self, data, schema=None):
        return MockDataFrame(data)
    
    def sql(self, query):
        return MockDataFrame([])

class MockDataFrame:
    """Mock DataFrame for demonstration"""
    def __init__(self, data):
        self.data = data
    
    def write(self):
        return MockDataFrameWriter()
    
    def toPandas(self):
        return pd.DataFrame(self.data)

class MockDataFrameWriter:
    """Mock DataFrame writer for demonstration"""
    def format(self, fmt):
        return self
    
    def mode(self, mode):
        return self
    
    def option(self, key, value):
        return self
    
    def saveAsTable(self, table_name):
        print(f"Mock: Saved data to table {table_name}")
        return self
    
    def save(self):
        print("Mock: Saved data")
        return self

class MockConnection:
    """Mock connection for demonstration"""
    def close(self):
        pass

# Databricks Manager
try:
    from databricks.connect import DatabricksSession
    from pyspark.sql import SparkSession
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
    from delta.tables import DeltaTable
    DATABRICKS_AVAILABLE = True
except ImportError:
    DATABRICKS_AVAILABLE = False
    print("Warning: Databricks packages not available. Using mock implementation.")

class DatabricksManager:
    """Manager for Databricks operations"""
    
    def __init__(self):
        self.config = Config.get_databricks_config()
        self.host = Config.DATABRICKS_HOST
        self.token = Config.DATABRICKS_TOKEN
        self.cluster_id = Config.DATABRICKS_CLUSTER_ID
        self._spark = None
        self._connection = None
        self.mock_mode = not DATABRICKS_AVAILABLE
        self.mock_data = {
            "orders": [],
            "invoices": []
        }
    
    @property
    def spark(self):
        """Get or create Spark session"""
        if self.mock_mode:
            return MockSparkSession()
        
        if self._spark is None and DATABRICKS_AVAILABLE:
            try:
                # Use the proper configuration method
                if 'token' in self.config:
                    self._spark = DatabricksSession.builder \
                        .remote(host=self.config['host'], token=self.config['token'], cluster_id=self.cluster_id) \
                        .getOrCreate()
                elif 'client_id' in self.config:
                    self._spark = DatabricksSession.builder \
                        .remote(host=self.config['host'], client_id=self.config['client_id'], 
                               client_secret=self.config['client_secret'], cluster_id=self.cluster_id) \
                        .getOrCreate()
                else:
                    print("No valid authentication method found")
                    self.mock_mode = True
                    return MockSparkSession()
            except Exception as e:
                print(f"Failed to create Databricks session: {e}")
                print("Switching to mock mode")
                self.mock_mode = True
                return MockSparkSession()
        return self._spark
    
    def create_orders_table(self):
        """Create orders Delta table"""
        if self.mock_mode:
            print("Mock: Creating orders table")
            self.mock_data["orders"] = []
            return
        
        if not DATABRICKS_AVAILABLE:
            print("Databricks not available, using mock mode")
            self.mock_data["orders"] = []
            return
        
        try:
            schema = StructType([
                StructField("order_id", StringType(), False),
                StructField("customer_id", StringType(), False),
                StructField("customer_name", StringType(), True),
                StructField("order_date", TimestampType(), True),
                StructField("total_amount", DoubleType(), True),
                StructField("status", StringType(), True),
                StructField("items", StringType(), True),  # JSON string
                StructField("created_at", TimestampType(), True)
            ])
            
            # Create empty DataFrame with schema
            empty_df = self.spark.createDataFrame([], schema)
            
            # Write as Delta table
            empty_df.write \
                .format("delta") \
                .mode("overwrite") \
                .option("path", Config.ORDERS_TABLE_PATH) \
                .saveAsTable("orders")
            
            print(f"Orders table created at {Config.ORDERS_TABLE_PATH}")
        except Exception as e:
            print(f"Error creating orders table: {e}")
            print("Switching to mock mode")
            self.mock_mode = True
            self.mock_data["orders"] = []
    
    def create_invoices_table(self):
        """Create invoices Delta table"""
        if self.mock_mode:
            print("Mock: Creating invoices table")
            self.mock_data["invoices"] = []
            return
        
        if not DATABRICKS_AVAILABLE:
            print("Databricks not available, using mock mode")
            self.mock_data["invoices"] = []
            return
        
        try:
            schema = StructType([
                StructField("invoice_id", StringType(), False),
                StructField("order_id", StringType(), False),
                StructField("customer_id", StringType(), False),
                StructField("invoice_number", StringType(), True),
                StructField("invoice_date", TimestampType(), True),
                StructField("amount", DoubleType(), True),
                StructField("tax_amount", DoubleType(), True),
                StructField("total_amount", DoubleType(), True),
                StructField("file_path", StringType(), True),
                StructField("uploaded_at", TimestampType(), True),
                StructField("created_at", TimestampType(), True)
            ])
            
            # Create empty DataFrame with schema
            empty_df = self.spark.createDataFrame([], schema)
            
            # Write as Delta table
            empty_df.write \
                .format("delta") \
                .mode("overwrite") \
                .option("path", Config.DELTA_TABLE_PATH) \
                .saveAsTable("invoices")
            
            print(f"Invoices table created at {Config.DELTA_TABLE_PATH}")
        except Exception as e:
            print(f"Error creating invoices table: {e}")
            print("Switching to mock mode")
            self.mock_mode = True
            self.mock_data["invoices"] = []
    
    def save_invoice_to_delta(self, invoice_data: Dict) -> bool:
        """Save invoice data to Delta table"""
        if self.mock_mode:
            print("Mock: Saving invoice to Delta table")
            self.mock_data["invoices"].append(invoice_data)
            return True
        
        try:
            # Convert to DataFrame
            df = self.spark.createDataFrame([invoice_data])
            
            # Append to Delta table
            df.write \
                .format("delta") \
                .mode("append") \
                .option("path", Config.DELTA_TABLE_PATH) \
                .saveAsTable("invoices")
            
            return True
        except Exception as e:
            print(f"Error saving invoice to Delta: {e}")
            print("Switching to mock mode")
            self.mock_mode = True
            self.mock_data["invoices"].append(invoice_data)
            return True
    
    def get_orders_data(self, customer_id: Optional[str] = None) -> pd.DataFrame:
        """Get orders data from Delta table"""
        if self.mock_mode:
            print("Mock: Getting orders data")
            data = self.mock_data["orders"]
            if customer_id:
                data = [order for order in data if order.get("customer_id") == customer_id]
            return pd.DataFrame(data)
        
        try:
            if customer_id:
                query = f"SELECT * FROM orders WHERE customer_id = '{customer_id}'"
            else:
                query = "SELECT * FROM orders"
            
            df = self.spark.sql(query)
            return df.toPandas()
        except Exception as e:
            print(f"Error getting orders data: {e}")
            print("Switching to mock mode")
            self.mock_mode = True
            data = self.mock_data["orders"]
            if customer_id:
                data = [order for order in data if order.get("customer_id") == customer_id]
            return pd.DataFrame(data)
    
    def get_invoices_data(self, customer_id: Optional[str] = None) -> pd.DataFrame:
        """Get invoices data from Delta table"""
        if self.mock_mode:
            print("Mock: Getting invoices data")
            data = self.mock_data["invoices"]
            if customer_id:
                data = [invoice for invoice in data if invoice.get("customer_id") == customer_id]
            return pd.DataFrame(data)
        
        try:
            if customer_id:
                query = f"SELECT * FROM invoices WHERE customer_id = '{customer_id}'"
            else:
                query = "SELECT * FROM invoices"
            
            df = self.spark.sql(query)
            return df.toPandas()
        except Exception as e:
            print(f"Error getting invoices data: {e}")
            print("Switching to mock mode")
            self.mock_mode = True
            data = self.mock_data["invoices"]
            if customer_id:
                data = [invoice for invoice in data if invoice.get("customer_id") == customer_id]
            return pd.DataFrame(data)

# Lakebase Client (Mock Implementation)
class LakebaseClient:
    """Mock Lakebase Client for demonstration purposes"""
    
    def __init__(self):
        self.data_dir = "lakebase_data"
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _get_file_path(self, table_name: str) -> str:
        """Get the file path for a table"""
        return os.path.join(self.data_dir, f"{table_name}.json")
    
    def _load_table_data(self, table_name: str) -> List[Dict]:
        """Load data from a table file"""
        file_path = self._get_file_path(table_name)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return []
    
    def _save_table_data(self, table_name: str, data: List[Dict]):
        """Save data to a table file"""
        file_path = self._get_file_path(table_name)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def save_invoice(self, invoice_data: Dict) -> Dict:
        """Save invoice data to Lakebase"""
        print(f"Mock: Saving invoice to Lakebase")
        
        # Load existing data
        existing_data = self._load_table_data("invoices")
        
        # Add new data
        invoice_data["_id"] = f"invoice_{len(existing_data)}_{datetime.now().timestamp()}"
        invoice_data["_created_at"] = datetime.now().isoformat()
        existing_data.append(invoice_data)
        
        # Save updated data
        self._save_table_data("invoices", existing_data)
        
        return {
            "status": "success",
            "table_name": "invoices",
            "inserted_count": 1,
            "total_records": len(existing_data)
        }

# Page configuration
st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize managers
@st.cache_resource
def get_databricks_manager():
    return DatabricksManager()

@st.cache_resource
def get_lakebase_client():
    return LakebaseClient()

def main():
    st.title(f"🏢 {Config.APP_NAME}")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["📊 Dashboard", "📋 Orders", "📄 Invoices", "⬆️ Upload Invoice", "⚙️ Settings"]
    )
    
    # Initialize managers
    db_manager = get_databricks_manager()
    lakebase_client = get_lakebase_client()
    
    if page == "📊 Dashboard":
        show_dashboard(db_manager, lakebase_client)
    elif page == "📋 Orders":
        show_orders_page(db_manager, lakebase_client)
    elif page == "📄 Invoices":
        show_invoices_page(db_manager, lakebase_client)
    elif page == "⬆️ Upload Invoice":
        show_upload_page(db_manager, lakebase_client)
    elif page == "⚙️ Settings":
        show_settings_page(db_manager, lakebase_client)

def show_dashboard(db_manager: DatabricksManager, lakebase_client: LakebaseClient):
    """Display main dashboard with key metrics"""
    st.header("📊 Dashboard Overview")
    
    # Get data
    try:
        orders_df = db_manager.get_orders_data()
        invoices_df = db_manager.get_invoices_data()
        
        if orders_df.empty and invoices_df.empty:
            st.warning("No data available. Please upload some orders and invoices first.")
            return
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_orders = len(orders_df) if not orders_df.empty else 0
            st.metric("Total Orders", total_orders)
        
        with col2:
            total_invoices = len(invoices_df) if not invoices_df.empty else 0
            st.metric("Total Invoices", total_invoices)
        
        with col3:
            total_revenue = orders_df['total_amount'].sum() if not orders_df.empty else 0
            st.metric("Total Revenue", f"${total_revenue:,.2f}")
        
        with col4:
            avg_order_value = orders_df['total_amount'].mean() if not orders_df.empty else 0
            st.metric("Avg Order Value", f"${avg_order_value:,.2f}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if not orders_df.empty:
                st.subheader("📈 Orders Over Time")
                orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
                daily_orders = orders_df.groupby(orders_df['order_date'].dt.date).size().reset_index()
                daily_orders.columns = ['Date', 'Orders']
                
                fig = px.line(daily_orders, x='Date', y='Orders', title='Daily Orders')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if not orders_df.empty:
                st.subheader("💰 Revenue by Status")
                status_revenue = orders_df.groupby('status')['total_amount'].sum().reset_index()
                
                fig = px.pie(status_revenue, values='total_amount', names='status', 
                           title='Revenue by Order Status')
                st.plotly_chart(fig, use_container_width=True)
        
        # Recent orders table
        if not orders_df.empty:
            st.subheader("📋 Recent Orders")
            recent_orders = orders_df.head(10)
            st.dataframe(recent_orders, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")

def show_orders_page(db_manager: DatabricksManager, lakebase_client: LakebaseClient):
    """Display orders management page"""
    st.header("📋 Orders Management")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        customer_filter = st.text_input("Filter by Customer ID", placeholder="Enter customer ID")
    
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Completed", "Cancelled"])
    
    with col3:
        date_range = st.date_input("Date Range", value=[datetime.now().date() - timedelta(days=30), datetime.now().date()])
    
    # Get orders data
    try:
        orders_df = db_manager.get_orders_data(customer_filter if customer_filter else None)
        
        if orders_df.empty:
            st.info("No orders found. Create some sample orders or upload data.")
            
            # Sample data creation
            if st.button("Create Sample Orders"):
                create_sample_orders(db_manager)
                st.rerun()
        else:
            # Apply filters
            if status_filter != "All":
                orders_df = orders_df[orders_df['status'] == status_filter]
            
            if len(date_range) == 2:
                orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
                orders_df = orders_df[
                    (orders_df['order_date'].dt.date >= date_range[0]) &
                    (orders_df['order_date'].dt.date <= date_range[1])
                ]
            
            # Display orders
            st.subheader(f"Orders ({len(orders_df)} found)")
            st.dataframe(orders_df, use_container_width=True)
            
            # Order details
            if not orders_df.empty:
                selected_order = st.selectbox("Select Order for Details", orders_df['order_id'].tolist())
                if selected_order:
                    order_details = orders_df[orders_df['order_id'] == selected_order].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Order Information")
                        st.write(f"**Order ID:** {order_details['order_id']}")
                        st.write(f"**Customer ID:** {order_details['customer_id']}")
                        st.write(f"**Customer Name:** {order_details['customer_name']}")
                        st.write(f"**Order Date:** {order_details['order_date']}")
                        st.write(f"**Total Amount:** ${order_details['total_amount']:,.2f}")
                        st.write(f"**Status:** {order_details['status']}")
                    
                    with col2:
                        st.subheader("Order Items")
                        try:
                            items = json.loads(order_details['items']) if order_details['items'] else []
                            if items:
                                items_df = pd.DataFrame(items)
                                st.dataframe(items_df, use_container_width=True)
                            else:
                                st.info("No items found for this order")
                        except:
                            st.info("Unable to parse order items")
    
    except Exception as e:
        st.error(f"Error loading orders: {e}")

def show_invoices_page(db_manager: DatabricksManager, lakebase_client: LakebaseClient):
    """Display invoices page"""
    st.header("📄 Invoices")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        customer_filter = st.text_input("Filter by Customer ID", placeholder="Enter customer ID")
    
    with col2:
        invoice_filter = st.text_input("Filter by Invoice Number", placeholder="Enter invoice number")
    
    # Get invoices data
    try:
        invoices_df = db_manager.get_invoices_data(customer_filter if customer_filter else None)
        
        if invoices_df.empty:
            st.info("No invoices found. Upload some invoices first.")
        else:
            # Apply filters
            if invoice_filter:
                invoices_df = invoices_df[invoices_df['invoice_number'].str.contains(invoice_filter, na=False)]
            
            # Display invoices
            st.subheader(f"Invoices ({len(invoices_df)} found)")
            st.dataframe(invoices_df, use_container_width=True)
            
            # Invoice summary
            if not invoices_df.empty:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_invoice_amount = invoices_df['total_amount'].sum()
                    st.metric("Total Invoice Amount", f"${total_invoice_amount:,.2f}")
                
                with col2:
                    avg_invoice_amount = invoices_df['total_amount'].mean()
                    st.metric("Average Invoice Amount", f"${avg_invoice_amount:,.2f}")
                
                with col3:
                    total_tax = invoices_df['tax_amount'].sum()
                    st.metric("Total Tax Amount", f"${total_tax:,.2f}")
    
    except Exception as e:
        st.error(f"Error loading invoices: {e}")

def show_upload_page(db_manager: DatabricksManager, lakebase_client: LakebaseClient):
    """Display invoice upload page"""
    st.header("⬆️ Upload Customer Invoice")
    
    # Upload form
    with st.form("invoice_upload_form"):
        st.subheader("Invoice Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            order_id = st.text_input("Order ID *", placeholder="Enter order ID")
            customer_id = st.text_input("Customer ID *", placeholder="Enter customer ID")
            invoice_number = st.text_input("Invoice Number *", placeholder="Enter invoice number")
        
        with col2:
            invoice_date = st.date_input("Invoice Date *", value=datetime.now().date())
            amount = st.number_input("Amount *", min_value=0.0, step=0.01, format="%.2f")
            tax_amount = st.number_input("Tax Amount", min_value=0.0, step=0.01, format="%.2f")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Invoice File",
            type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
            help="Supported formats: PDF, PNG, JPG, JPEG, TXT"
        )
        
        submitted = st.form_submit_button("Upload Invoice", type="primary")
        
        if submitted:
            if not all([order_id, customer_id, invoice_number, amount]):
                st.error("Please fill in all required fields (marked with *)")
            else:
                # Process upload
                process_invoice_upload(
                    order_id, customer_id, invoice_number, invoice_date,
                    amount, tax_amount, uploaded_file, db_manager, lakebase_client
                )

def process_invoice_upload(order_id: str, customer_id: str, invoice_number: str,
                         invoice_date, amount: float, tax_amount: float,
                         uploaded_file, db_manager: DatabricksManager,
                         lakebase_client: LakebaseClient):
    """Process invoice upload"""
    try:
        # Generate unique invoice ID
        invoice_id = str(uuid.uuid4())
        
        # Calculate total amount
        total_amount = amount + tax_amount
        
        # Save file if uploaded
        file_path = None
        if uploaded_file:
            # Create uploads directory if it doesn't exist
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_dir, f"{invoice_id}_{uploaded_file.name}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        # Prepare invoice data
        invoice_data = {
            "invoice_id": invoice_id,
            "order_id": order_id,
            "customer_id": customer_id,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "amount": amount,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "file_path": file_path,
            "uploaded_at": datetime.now(),
            "created_at": datetime.now()
        }
        
        # Save to Delta table
        success = db_manager.save_invoice_to_delta(invoice_data)
        
        if success:
            # Also save to Lakebase
            try:
                lakebase_client.save_invoice(invoice_data)
            except Exception as e:
                st.warning(f"Invoice saved to Delta table but failed to save to Lakebase: {e}")
            
            st.success("✅ Invoice uploaded and saved successfully!")
            st.json(invoice_data)
        else:
            st.error("❌ Failed to save invoice")
    
    except Exception as e:
        st.error(f"Error processing invoice upload: {e}")

def show_settings_page(db_manager: DatabricksManager, lakebase_client: LakebaseClient):
    """Display settings page"""
    st.header("⚙️ Settings")
    
    # Database initialization
    st.subheader("Database Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Initialize Orders Table", type="primary"):
            try:
                db_manager.create_orders_table()
                st.success("✅ Orders table created successfully!")
            except Exception as e:
                st.error(f"❌ Error creating orders table: {e}")
    
    with col2:
        if st.button("Initialize Invoices Table", type="primary"):
            try:
                db_manager.create_invoices_table()
                st.success("✅ Invoices table created successfully!")
            except Exception as e:
                st.error(f"❌ Error creating invoices table: {e}")
    
    # Sample data
    st.subheader("Sample Data")
    
    if st.button("Create Sample Orders", type="secondary"):
        try:
            create_sample_orders(db_manager)
            st.success("✅ Sample orders created successfully!")
        except Exception as e:
            st.error(f"❌ Error creating sample orders: {e}")
    
    # Configuration info
    st.subheader("Configuration")
    
    config_info = {
        "Databricks Host": Config.DATABRICKS_HOST,
        "Delta Table Path": Config.DELTA_TABLE_PATH,
        "Orders Table Path": Config.ORDERS_TABLE_PATH,
        "Mock Mode": db_manager.mock_mode
    }
    
    for key, value in config_info.items():
        st.text(f"{key}: {value}")

def create_sample_orders(db_manager: DatabricksManager):
    """Create sample orders for testing"""
    sample_orders = [
        {
            "order_id": "ORD-001",
            "customer_id": "CUST-001",
            "customer_name": "John Doe",
            "order_date": datetime.now() - timedelta(days=5),
            "total_amount": 150.00,
            "status": "Completed",
            "items": json.dumps([
                {"item": "Laptop", "quantity": 1, "price": 120.00},
                {"item": "Mouse", "quantity": 1, "price": 30.00}
            ]),
            "created_at": datetime.now()
        },
        {
            "order_id": "ORD-002",
            "customer_id": "CUST-002",
            "customer_name": "Jane Smith",
            "order_date": datetime.now() - timedelta(days=3),
            "total_amount": 75.50,
            "status": "Pending",
            "items": json.dumps([
                {"item": "Keyboard", "quantity": 1, "price": 75.50}
            ]),
            "created_at": datetime.now()
        },
        {
            "order_id": "ORD-003",
            "customer_id": "CUST-001",
            "customer_name": "John Doe",
            "order_date": datetime.now() - timedelta(days=1),
            "total_amount": 200.00,
            "status": "Completed",
            "items": json.dumps([
                {"item": "Monitor", "quantity": 1, "price": 200.00}
            ]),
            "created_at": datetime.now()
        }
    ]
    
    # Save sample orders
    for order in sample_orders:
        if db_manager.mock_mode:
            db_manager.mock_data["orders"].append(order)
        else:
            try:
                df = db_manager.spark.createDataFrame([order])
                df.write \
                    .format("delta") \
                    .mode("append") \
                    .option("path", Config.ORDERS_TABLE_PATH) \
                    .saveAsTable("orders")
            except Exception as e:
                print(f"Error saving sample order: {e}")
                db_manager.mock_data["orders"].append(order)

if __name__ == "__main__":
    main()

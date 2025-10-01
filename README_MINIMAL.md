# 🚀 Minimal Databricks App - Order Management System

This is a streamlined version of the Order Management Databricks App with only the essential files needed for deployment.

## 📁 **Essential Files**

```
databricks_app_minimal.py    # Main app (consolidated)
requirements_minimal.txt     # Minimal dependencies
deploy_minimal.py           # Simple deployment script
README_MINIMAL.md          # This file
```

## 🚀 **Quick Deployment**

### **Step 1: Set Environment Variables**

**Option A: OAuth (Recommended)**
```bash
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_CLIENT_ID=your-client-id
export DATABRICKS_CLIENT_SECRET=your-client-secret
export DATABRICKS_CLUSTER_ID=your-cluster-id
```

**Option B: Personal Access Token**
```bash
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=your-token
export DATABRICKS_CLUSTER_ID=your-cluster-id
```

### **Step 2: Deploy**
```bash
python3 deploy_minimal.py
```

### **Step 3: Access App**
1. Go to your Databricks workspace
2. Navigate to Apps section
3. Find "Order Management System"
4. Click to launch

## 🎯 **Features**

- ✅ **Dashboard**: Overview with metrics and charts
- ✅ **Order Management**: View and manage orders
- ✅ **Invoice Management**: View and manage invoices
- ✅ **Invoice Upload**: Upload invoices with metadata
- ✅ **Delta Tables**: Automatic data persistence
- ✅ **Mock Mode**: Works without Databricks connection
- ✅ **OAuth Support**: Secure authentication

## 🔧 **What's Included**

The `databricks_app_minimal.py` file contains:
- Complete Streamlit application
- Databricks integration with fallback to mock mode
- Lakebase client (mock implementation)
- All UI components and functionality
- Configuration management
- Error handling and graceful degradation

## 📋 **Prerequisites**

- Databricks workspace access
- OAuth credentials OR Personal Access Token
- Running cluster (shared or single-user)
- Apps creation permissions

## 🛠️ **Manual Deployment (Alternative)**

If the automated deployment doesn't work:

1. **Upload files to Databricks**:
   - Go to your Databricks workspace
   - Navigate to Workspace → Users → [your-username]
   - Create folder: `order_management_app`
   - Upload: `databricks_app_minimal.py` and `requirements_minimal.txt`

2. **Create Databricks App**:
   - Go to Apps section in Databricks
   - Click "Create App"
   - Select "Streamlit"
   - Main file: `databricks_app_minimal.py`
   - Requirements: `requirements_minimal.txt`

## 🧪 **Testing Locally**

To test the app locally before deployment:

```bash
# Install dependencies
pip install -r requirements_minimal.txt

# Set environment variables (optional for mock mode)
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_CLIENT_ID=your-client-id
export DATABRICKS_CLIENT_SECRET=your-client-secret

# Run the app
streamlit run databricks_app_minimal.py
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **"No authentication method configured"**
   - Set environment variables for OAuth or PAT
   - Verify credentials are correct

2. **"Permission denied"**
   - Check Apps creation permissions
   - Verify cluster access permissions

3. **"Cluster not found"**
   - Verify cluster ID is correct
   - Ensure cluster is running

### **Debug Mode**

The app automatically falls back to mock mode if Databricks connection fails, so it will always work for demonstration purposes.

## 📊 **App Structure**

```
📱 Order Management System
├── 📊 Dashboard (metrics, charts, recent orders)
├── 📋 Orders (view, filter, manage orders)
├── 📄 Invoices (view, filter, manage invoices)
├── ⬆️ Upload Invoice (upload with metadata)
└── ⚙️ Settings (initialize tables, sample data)
```

## 🎉 **Success!**

Once deployed, you'll have a fully functional order management system running on Databricks with:
- Real-time data processing
- Interactive dashboards
- File upload capabilities
- Delta table integration
- Secure OAuth authentication

---

**Ready to deploy! 🚀**

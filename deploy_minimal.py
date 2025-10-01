#!/usr/bin/env python3
"""
Deploy Minimal Databricks App
This script deploys the consolidated Order Management app to Databricks
"""

import os
import sys
from pathlib import Path

def check_credentials():
    """Check if Databricks credentials are configured"""
    # Check environment variables
    host = os.getenv('DATABRICKS_HOST')
    token = os.getenv('DATABRICKS_TOKEN')
    client_id = os.getenv('DATABRICKS_CLIENT_ID')
    client_secret = os.getenv('DATABRICKS_CLIENT_SECRET')
    
    if not host or host == 'https://your-workspace.cloud.databricks.com':
        print("❌ DATABRICKS_HOST not configured")
        return False
    
    if not token and not (client_id and client_secret):
        print("❌ No authentication method configured")
        print("Please set either:")
        print("  - DATABRICKS_TOKEN (for Personal Access Token)")
        print("  - DATABRICKS_CLIENT_ID and DATABRICKS_CLIENT_SECRET (for OAuth)")
        return False
    
    if token and (client_id or client_secret):
        print("⚠️  Both PAT and OAuth configured. Using OAuth.")
    
    print("✅ Credentials configured")
    return True

def deploy_to_databricks():
    """Deploy the minimal app to Databricks"""
    print("🚀 Deploying Minimal Order Management App to Databricks...")
    
    if not check_credentials():
        print("\n📝 Please configure your Databricks credentials:")
        print("Option 1 (OAuth - Recommended):")
        print("  export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com")
        print("  export DATABRICKS_CLIENT_ID=your-client-id")
        print("  export DATABRICKS_CLIENT_SECRET=your-client-secret")
        print("  export DATABRICKS_CLUSTER_ID=your-cluster-id")
        print("\nOption 2 (Personal Access Token):")
        print("  export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com")
        print("  export DATABRICKS_TOKEN=your-token")
        print("  export DATABRICKS_CLUSTER_ID=your-cluster-id")
        return False
    
    try:
        from databricks.sdk import WorkspaceClient
        from databricks.sdk.service.apps import AppManifest, AppType
        
        # Create workspace client
        config = {}
        if os.getenv('DATABRICKS_CLIENT_ID') and os.getenv('DATABRICKS_CLIENT_SECRET'):
            config = {
                'host': os.getenv('DATABRICKS_HOST'),
                'client_id': os.getenv('DATABRICKS_CLIENT_ID'),
                'client_secret': os.getenv('DATABRICKS_CLIENT_SECRET')
            }
        else:
            config = {
                'host': os.getenv('DATABRICKS_HOST'),
                'token': os.getenv('DATABRICKS_TOKEN')
            }
        
        workspace_client = WorkspaceClient(**config)
        
        # Create app manifest
        manifest = AppManifest(
            name="Order Management System",
            app_type=AppType.STREAMLIT,
            description="Minimal Order Management System with Databricks Integration",
            version="1.0.0",
            main_file="databricks_app_minimal.py",
            requirements_file="requirements_minimal.txt"
        )
        
        # Deploy app
        app = workspace_client.apps.create(
            name="Order Management System",
            manifest=manifest
        )
        
        print(f"✅ App deployed successfully!")
        print(f"📱 App ID: {app.app_id}")
        print(f"🌐 Access your app in Databricks workspace under Apps section")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your Databricks credentials")
        print("2. Ensure you have Apps permissions in Databricks")
        print("3. Verify your cluster is running")
        print("4. Make sure you're using the correct workspace URL")
        return False

def main():
    """Main deployment function"""
    print("🏢 Minimal Order Management Databricks App - Deployment")
    print("=" * 60)
    
    if deploy_to_databricks():
        print("\n🎉 Deployment completed successfully!")
        print("📋 Next steps:")
        print("1. Go to your Databricks workspace")
        print("2. Navigate to Apps section")
        print("3. Find your deployed app")
        print("4. Click to launch the app")
    else:
        print("\n❌ Deployment failed. Please check the errors above.")

if __name__ == "__main__":
    main()

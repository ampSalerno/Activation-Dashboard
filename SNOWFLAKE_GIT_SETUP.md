# Snowflake Git Integration Setup Guide

This guide will help you connect your Snowflake Streamlit dashboard to your GitHub repository, so you can deploy updates automatically without manually uploading files.

## Prerequisites

- Admin or appropriate privileges in Snowflake
- GitHub repository with your dashboard code (already set up at: https://github.com/ampSalerno/Activation-Dashboard)
- A GitHub Personal Access Token (PAT) for authentication

---

## Step 1: Create a GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Direct link: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name like "Snowflake Streamlit Dashboard"
4. Set expiration (recommend 90 days or no expiration for production)
5. Select these scopes:
   - ✅ `repo` (Full control of private repositories)
6. Click "Generate token"
7. **IMPORTANT**: Copy the token immediately - you won't be able to see it again!

---

## Step 2: Create API Integration in Snowflake

Run this SQL in a Snowflake worksheet (as ACCOUNTADMIN or a role with CREATE INTEGRATION privilege):

```sql
-- Create API integration for GitHub
CREATE OR REPLACE API INTEGRATION git_api_integration
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/ampSalerno/')
  ENABLED = TRUE;

-- Verify it was created
SHOW API INTEGRATIONS;
```

---

## Step 3: Create Git Repository Object in Snowflake

Replace `<YOUR_GITHUB_TOKEN>` with the token you created in Step 1:

```sql
-- Create a database and schema for your Streamlit app if you haven't already
USE ROLE ACCOUNTADMIN;
CREATE DATABASE IF NOT EXISTS STREAMLIT_APPS;
CREATE SCHEMA IF NOT EXISTS STREAMLIT_APPS.ACTIVATION_DASHBOARD;

-- Create the Git repository object
CREATE OR REPLACE GIT REPOSITORY STREAMLIT_APPS.ACTIVATION_DASHBOARD.ACTIVATION_DASHBOARD_REPO
  API_INTEGRATION = git_api_integration
  ORIGIN = 'https://github.com/ampSalerno/Activation-Dashboard.git'
  GIT_CREDENTIALS = (USERNAME = 'ampSalerno', PASSWORD = '<YOUR_GITHUB_TOKEN>');

-- Fetch the latest code from GitHub
ALTER GIT REPOSITORY STREAMLIT_APPS.ACTIVATION_DASHBOARD.ACTIVATION_DASHBOARD_REPO FETCH;

-- Verify it worked
SHOW GIT REPOSITORIES IN SCHEMA STREAMLIT_APPS.ACTIVATION_DASHBOARD;

-- List files in the repository
LS @STREAMLIT_APPS.ACTIVATION_DASHBOARD.ACTIVATION_DASHBOARD_REPO/branches/master;
```

---

## Step 4: Create or Update Your Streamlit App

### Option A: Create a New Streamlit App from Git Repository

```sql
-- Create Streamlit app from the Git repository
USE ROLE ACCOUNTADMIN;
CREATE OR REPLACE STREAMLIT STREAMLIT_APPS.ACTIVATION_DASHBOARD.ACTIVATION_DASHBOARD_V3
  ROOT_LOCATION = '@STREAMLIT_APPS.ACTIVATION_DASHBOARD.ACTIVATION_DASHBOARD_REPO/branches/master'
  MAIN_FILE = '/streamlit_app.py'
  QUERY_WAREHOUSE = 'YOUR_WAREHOUSE_NAME';  -- Replace with your warehouse name

-- Grant permissions to run the app
GRANT USAGE ON STREAMLIT STREAMLIT_APPS.ACTIVATION_DASHBOARD.ACTIVATION_DASHBOARD_V3
  TO ROLE YOUR_ROLE_NAME;  -- Replace with your role
```

### Option B: Update Existing Streamlit App to Use Git

If you already have a Streamlit app and want to switch it to Git:

1. Go to Snowsight UI
2. Navigate to Projects → Streamlit
3. Find your existing dashboard
4. Click the three dots (...) menu
5. Select "Edit in Snowflake"
6. In the editor, click Settings (gear icon)
7. Under "App location", select "Git Repository"
8. Choose your repository and branch
9. Set Main file to `streamlit_app.py`
10. Save

---

## Step 5: Configure Automatic Updates (Optional)

To automatically pull latest changes from GitHub:

```sql
-- Set up a task to fetch from Git every hour (or your preferred schedule)
CREATE OR REPLACE TASK STREAMLIT_APPS.ACTIVATION_DASHBOARD.REFRESH_GIT_REPO
  WAREHOUSE = 'YOUR_WAREHOUSE_NAME'
  SCHEDULE = 'USING CRON 0 * * * * UTC'  -- Every hour
AS
  ALTER GIT REPOSITORY STREAMLIT_APPS.ACTIVATION_DASHBOARD.ACTIVATION_DASHBOARD_REPO FETCH;

-- Start the task
ALTER TASK STREAMLIT_APPS.ACTIVATION_DASHBOARD.REFRESH_GIT_REPO RESUME;
```

Or for manual updates, just run:
```sql
ALTER GIT REPOSITORY STREAMLIT_APPS.ACTIVATION_DASHBOARD.ACTIVATION_DASHBOARD_REPO FETCH;
```

---

## Step 6: Verify Everything Works

1. Go to Snowsight UI → Projects → Streamlit
2. Find your dashboard and click to open it
3. The app should now load from the Git repository
4. Make a small change to your code locally
5. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Test Git integration"
   git push
   ```
6. In Snowflake, run:
   ```sql
   ALTER GIT REPOSITORY STREAMLIT_APPS.ACTIVATION_DASHBOARD.ACTIVATION_DASHBOARD_REPO FETCH;
   ```
7. Refresh your Streamlit app - you should see the changes!

---

## Workflow After Git Integration

Once set up, your workflow becomes:

1. **Make changes locally** to your dashboard code
2. **Test locally** (optional): `streamlit run streamlit_app.py`
3. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Your change description"
   git push
   ```
4. **Update Snowflake** (one of these options):
   - Wait for automatic sync (if you set up the task in Step 5)
   - Or manually run in Snowflake:
     ```sql
     ALTER GIT REPOSITORY STREAMLIT_APPS.ACTIVATION_DASHBOARD.ACTIVATION_DASHBOARD_REPO FETCH;
     ```
5. **Refresh the Streamlit app** in Snowsight

---

## Current Update Required

The SQL query changes (52 weeks instead of 10) have already been committed to GitHub. After completing the Git integration setup, run:

```sql
ALTER GIT REPOSITORY STREAMLIT_APPS.ACTIVATION_DASHBOARD.ACTIVATION_DASHBOARD_REPO FETCH;
```

Then refresh your dashboard - you'll now see 12 months of data in the monthly view!

---

## Troubleshooting

### "Invalid credentials" error
- Regenerate your GitHub Personal Access Token
- Make sure the token has `repo` scope
- Update the Git repository credentials:
  ```sql
  ALTER GIT REPOSITORY STREAMLIT_APPS.ACTIVATION_DASHBOARD.ACTIVATION_DASHBOARD_REPO
    SET GIT_CREDENTIALS = (USERNAME = 'ampSalerno', PASSWORD = '<NEW_TOKEN>');
  ```

### Changes not appearing in Streamlit app
- Make sure you ran `ALTER GIT REPOSITORY ... FETCH;`
- Try clearing the Streamlit cache (menu → Clear cache → Rerun)
- Verify the files are in the repository:
  ```sql
  LS @STREAMLIT_APPS.ACTIVATION_DASHBOARD.ACTIVATION_DASHBOARD_REPO/branches/master;
  ```

### Permission errors
- Ensure your role has USAGE on the Streamlit app
- Verify your role has access to the warehouse, database, and schema

---

## References

- [Snowflake Git Integration Documentation](https://docs.snowflake.com/en/developer-guide/git/git-overview)
- [Snowflake Streamlit Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

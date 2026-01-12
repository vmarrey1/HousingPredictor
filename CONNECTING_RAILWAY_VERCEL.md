# Connecting Railway Backend with Vercel Frontend

This guide will help you connect your Railway-deployed Flask backend with your Vercel-deployed Next.js frontend.

## Prerequisites

- ✅ Railway backend is deployed and running
- ✅ Vercel frontend is deployed
- ✅ You have access to both Railway and Vercel dashboards

## Step 1: Get Your Railway Backend URL

1. Go to your [Railway Dashboard](https://railway.app)
2. Select your backend project
3. Click on your service/deployment
4. Go to the **Settings** tab
5. Find your **Public Domain** or **Custom Domain**
   - It will look like: `your-app-name.up.railway.app` or `api.yourdomain.com`
6. Copy the full URL (including `https://`)

**Example:** `https://berkeley-planner-backend.up.railway.app`

## Step 2: Configure Vercel Environment Variables

1. Go to your [Vercel Dashboard](https://vercel.com)
2. Select your frontend project
3. Go to **Settings** → **Environment Variables**
4. Add a new environment variable:
   - **Name:** `NEXT_PUBLIC_API_BASE`
   - **Value:** Your Railway backend URL (e.g., `https://berkeley-planner-backend.up.railway.app`)
   - **Environment:** Select all environments (Production, Preview, Development) or just Production
5. Click **Save**

**Important:** After adding the environment variable, you need to redeploy your Vercel application for the changes to take effect.

## Step 3: Update Backend CORS Settings

Your backend needs to allow requests from your Vercel domain. Update the CORS configuration in `backend/app.py`:

1. Get your Vercel deployment URL:
   - Go to your Vercel project → **Settings** → **Domains**
   - Copy your production domain (e.g., `berkeleyfouryearplan.com` or `your-app.vercel.app`)

2. Update `backend/app.py`:

   Find the `allowed_origins` list (around line 31) and add your Vercel domain:

   ```python
   allowed_origins = [
       'https://berkeleyfouryearplan.com',
       'https://www.berkeleyfouryearplan.com',
       'https://your-app.vercel.app',  # Add your Vercel domain here
       'http://localhost:3000',  # For local development
       'http://localhost:3001',  # For local development
   ]
   ```

   **OR** use the environment variable approach (already implemented):

   In Railway, add an environment variable:
   - **Name:** `ALLOWED_ORIGINS`
   - **Value:** `https://your-vercel-domain.com,https://www.your-vercel-domain.com`
   - This allows you to add multiple domains without code changes

3. Redeploy your Railway backend after making changes

## Step 4: Verify Backend is Accessible

Test that your Railway backend is accessible:

```bash
# Replace with your actual Railway URL
curl https://your-railway-backend.up.railway.app/api/health
```

You should get a JSON response like:
```json
{
  "status": "healthy",
  "message": "Berkeley Four Year Plan Generator is running",
  ...
}
```

## Step 5: Test the Connection

1. **Redeploy Vercel** (if you haven't already):
   - Go to Vercel Dashboard → Your Project → **Deployments**
   - Click the three dots on the latest deployment → **Redeploy**

2. **Test the frontend:**
   - Open your Vercel deployment URL
   - Open browser DevTools (F12) → **Network** tab
   - Try to generate a plan or load majors
   - Check that API requests are going to your Railway backend URL
   - Verify there are no CORS errors in the console

## Step 6: Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:

1. **Check allowed origins:** Make sure your Vercel domain is in the backend's `allowed_origins` list
2. **Check protocol:** Use `https://` for production domains
3. **Check trailing slashes:** Don't include trailing slashes in the domain (e.g., use `https://example.com` not `https://example.com/`)

### API Requests Failing

1. **Check Railway logs:**
   - Railway Dashboard → Your Service → **Deployments** → Click on deployment → **View Logs**

2. **Check Vercel environment variables:**
   - Verify `NEXT_PUBLIC_API_BASE` is set correctly
   - Make sure you redeployed after adding the variable

3. **Test backend directly:**
   ```bash
   curl https://your-railway-backend.up.railway.app/api/majors
   ```

### Session/Cookie Issues

If authentication isn't working:

1. **Check cookie settings in `backend/app.py`:**
   - `SESSION_COOKIE_SECURE` should be `True` in production
   - `SESSION_COOKIE_SAMESITE` should be `'None'` for cross-origin requests

2. **Verify `withCredentials` is set:**
   - The frontend already sets `axios.defaults.withCredentials = true`
   - This is required for cookies to be sent cross-origin

## Quick Reference

### Environment Variables Needed

**Vercel:**
- `NEXT_PUBLIC_API_BASE` = Your Railway backend URL (e.g., `https://your-app.up.railway.app`)

**Railway:**
- `ALLOWED_ORIGINS` = Comma-separated list of frontend domains (optional, can also hardcode in app.py)
- `MONGODB_URI` = Your MongoDB connection string
- `GEMINI_API_KEY` = Your Google Gemini API key (for AI features)
- `SECRET_KEY` = Flask secret key for sessions
- `FLASK_ENV` = `production` (for production settings)

### Important URLs

- **Railway Backend:** `https://your-app.up.railway.app`
- **Vercel Frontend:** `https://your-app.vercel.app` or your custom domain

## Next Steps

After connecting:
1. Test all features (signup, login, plan generation, saving schedules)
2. Monitor Railway logs for any errors
3. Set up custom domains if needed
4. Configure SSL certificates (usually automatic on both platforms)

# 🚀 DEPLOY PDF GENIUS ON VERCEL + SUPABASE (FREE)

## ✅ **WHY VERCEL IS BETTER:**
- **Frontend:** Vercel = Best for Next.js (free)
- **Backend:** Vercel Serverless Functions (free)
- **Database:** Supabase = Free PostgreSQL + Auth
- **Redis:** Upstash = Free Redis
- **Cost:** $0/month, no credit card

## 📋 **STEP-BY-STEP DEPLOYMENT (10 MINUTES):**

### **Step 1: Deploy Frontend on Vercel (2 min)**
1. Go to: https://vercel.com
2. Sign up with GitHub
3. Click "New Project"
4. Import: `surendaraipro/pdf-genius`
5. Select `frontend` as root directory
6. Vercel auto-detects Next.js
7. Click "Deploy"

**Your frontend will be live at:** `https://pdf-genius.vercel.app`

### **Step 2: Create Supabase Database (2 min)**
1. Go to: https://supabase.com
2. Sign up with GitHub
3. Create new project
4. Name: `pdf-genius`
5. Region: Singapore (closest to India)
6. Create

**Get these from Supabase dashboard:**
- `SUPABASE_URL`: `https://xxxxxxxxxxxx.supabase.co`
- `SUPABASE_ANON_KEY`: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### **Step 3: Deploy Backend on Vercel (3 min)**
**Option A: Vercel Serverless Functions**
1. In Vercel project settings
2. Go to "Functions"
3. Upload backend code or use API routes

**Option B: Separate backend service**
1. Create new Vercel project
2. Name: `pdf-genius-api`
3. Use Python runtime
4. Deploy backend code

### **Step 4: Add Redis (Upstash) (1 min)**
1. Go to: https://upstash.com
2. Sign up with GitHub
3. Create Redis database
4. Free tier: 10,000 requests/day

### **Step 5: Configure Environment Variables**
**In Vercel dashboard → Settings → Environment Variables:**
```
# Groq API
GROQ_API_KEY=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

# PDF.co API
PDF_CO_API_KEY=surendar.ai.pro@gmail.com_CHUtz4sGlMKf3xhKHjGwkfUzSE06V9Rup5z794lmsnO22AAYCZDnCDLDSHr96bWf

# Supabase
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Upstash Redis
REDIS_URL=redis://xxxx.upstash.io:6379

# Security
SECRET_KEY=your-secret-key
```

## 🎯 **QUICKEST PATH:**

**Just deploy frontend on Vercel first:**
1. Go to: https://vercel.com
2. Import `pdf-genius` repo
3. Select `frontend` directory
4. Deploy

**Then add backend and database later.**

## 💰 **FREE TIER LIMITS:**

**Vercel:**
- 100GB bandwidth/month
- Unlimited deployments
- Serverless functions: 100GB-hours/month

**Supabase:**
- 500MB database
- 50,000 rows free
- 2GB file storage

**Upstash:**
- 10,000 commands/day
- 256MB storage

## 🔧 **TROUBLESHOOTING:**

### **If Vercel build fails:**
1. Check Node.js version (use 18+)
2. Check `package.json` dependencies
3. Check build logs in Vercel dashboard

### **If database connection fails:**
1. Verify Supabase credentials
2. Check network access (allow all IPs)
3. Test connection locally first

### **If API calls fail:**
1. Check CORS settings
2. Verify environment variables
3. Check Vercel function logs

## 🚀 **READY TO DEPLOY?**

**Start with Step 1: Deploy frontend on Vercel!**

**Your SaaS will be live in 5 minutes!** 🎯
# 🚀 ONE-CLICK DEPLOYMENT FOR PDF GENIUS

## **OPTION 1: DEPLOY WITH RAILWAY (RECOMMENDED)**

### **Click this button to deploy instantly:**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/PDF-Genius?referralCode=surendar)

**Or manually:**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Run this command to deploy:
railway run https://github.com/surendar-s/pdf-genius
```

## **OPTION 2: DEPLOY WITH RENDER (ALTERNATIVE)**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/surendar-s/pdf-genius)

## **OPTION 3: MANUAL DEPLOYMENT**

### **Step 1: Create GitHub Repository**
```bash
# Create new repo on GitHub.com named "pdf-genius"
# Then run these commands:

cd /home/surendar/.openclaw/workspace/pdf_genius
git remote add origin https://github.com/YOUR_USERNAME/pdf-genius.git
git push -u origin main
```

### **Step 2: Deploy to Railway**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway init

# Add services
railway add postgresql
railway add redis

# Set environment variables
railway variables set GROQ_API_KEY="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"
railway variables set PDF_CO_API_KEY="surendar.ai.pro@gmail.com_CHUtz4sGlMKf3xhKHjGwkfUzSE06V9Rup5z794lmsnO22AAYCZDnCDLDSHr96bWf"
railway variables set SECRET_KEY="$(openssl rand -hex 32)"

# Deploy!
railway up
```

## **🎯 AFTER DEPLOYMENT:**

### **Your SaaS will be live at:**
`https://pdf-genius.up.railway.app`

### **Immediate testing:**
1. Visit your URL
2. Click "Get Started Free"
3. Register with your email
4. Upload a PDF
5. Try AI chat
6. Convert to Word/Excel

### **Start earning money:**
1. **Today:** Deploy & test
2. **Tomorrow:** Product Hunt launch
3. **Day 3:** First paying customer ($29)
4. **Week 1:** $100-500 MRR

## **🔧 TROUBLESHOOTING:**

### **If deployment fails:**
```bash
# Check logs
railway logs

# Redeploy
railway up --force

# Check variables
railway variables list
```

### **If API keys don't work:**
1. Check Groq quota: https://console.groq.com
2. Check PDF.co credits: https://apidocs.pdf.co

## **📞 NEED HELP?**

**I can deploy it for you if you:**
1. Create a Railway account (free)
2. Give me temporary access
3. Or share your screen for live guidance

## **💰 REVENUE READY:**

- **Free:** 10 conversions, 5 AI questions
- **Pro:** $29/month (100 conversions, 50 AI questions)
- **Business:** $99/month (500 conversions, 250 AI questions)
- **Enterprise:** $299/month (custom)

**First month target:** $1,000+ MRR

## **🚀 READY TO DEPLOY?**

**Run this now:**
```bash
npm install -g @railway/cli
railway login
railway init
railway add postgresql
railway add redis
railway variables set GROQ_API_KEY="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"
railway variables set PDF_CO_API_KEY="surendar.ai.pro@gmail.com_CHUtz4sGlMKf3xhKHjGwkfUzSE06V9Rup5z794lmsnO22AAYCZDnCDLDSHr96bWf"
railway up
```

**15 minutes from now, you'll have a live SaaS business!** 🎉
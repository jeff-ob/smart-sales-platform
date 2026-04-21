# ⚡ Quick Start Guide

## 🚀 Deploy in 20 Minutes

### Prerequisites
- Python 3.11+
- Git installed
- GitHub account

---

## 📋 Step-by-Step

### 1. Verify Everything is Ready

```bash
python verify_deployment.py
```

Expected: ✅ 19/19 checks passed

---

### 2. Initialize Git

```bash
git init
git add .
git commit -m "Initial commit - Smart Sales Platform ready for deployment"
```

---

### 3. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `smart-sales-platform`
3. Description: "End-to-end sales analytics platform with ML"
4. Choose Public or Private
5. **DO NOT** check "Add README"
6. Click "Create repository"

---

### 4. Push to GitHub

```bash
# Replace [username] with your GitHub username
git remote add origin https://github.com/[username]/smart-sales-platform.git
git branch -M main
git push -u origin main
```

**If "file too large" error:**
```bash
git lfs install
git lfs track "*.pkl"
git lfs track "*.db"
git lfs track "*.csv"
git add .gitattributes
git commit -m "Add Git LFS"
git push
```

---

### 5. Deploy to Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click "Sign up" → Connect with GitHub
3. Click "New app"
4. Fill in:
   - **Repository**: `[username]/smart-sales-platform`
   - **Branch**: `main`
   - **Main file path**: `dashboard/app.py`
5. Click "Deploy" 🚀

Wait 5-10 minutes for deployment.

---

## ✅ Done!

Your app is now live at:
`https://[username]-smart-sales-platform.streamlit.app`

---

## 🔄 Update Your App

After any changes:

```bash
git add .
git commit -m "Description of changes"
git push
```

Streamlit Cloud will automatically redeploy! ⚡

---

## 📚 More Guides

- **French Guide**: `COMMENCER_ICI.md`
- **Detailed Checklist**: `DEPLOYMENT_CHECKLIST.md`
- **Complete Guide**: `DEPLOIEMENT.md`

---

## 🐛 Troubleshooting

**Error: file too large**
→ Use Git LFS (see step 4)

**App not loading**
→ Check logs in Streamlit Cloud (Manage app → Logs)

**Missing files**
→ Verify all files are on GitHub

---

## 📞 Need Help?

- **Issues**: https://github.com/[username]/smart-sales-platform/issues
- **Documentation**: See `DEPLOIEMENT.md`

---

**Ready? Let's go! 🚀**


# 🚀 Quick Start Checklist

Use this checklist to set up Supabase for your EvalIA app.

## ☑️ Setup Checklist

### Phase 1: Supabase Account Setup
- [ ] Create account at [supabase.com](https://supabase.com)
- [ ] Create new project (name: `evalia` or any name)
- [ ] Wait for project to be ready (2-3 minutes)
- [ ] Copy Project URL from Project Settings → API
- [ ] Copy anon/public API key from Project Settings → API

### Phase 2: Database Setup
- [ ] Go to SQL Editor in Supabase dashboard
- [ ] Create new query
- [ ] Copy SQL from `SUPABASE_SETUP.md` (Step 2)
- [ ] Run the SQL query
- [ ] Verify tables created in Table Editor:
  - [ ] `users` table exists
  - [ ] `submissions` table exists
  - [ ] Default users inserted (teacher, student1, student2, student3)

### Phase 3: Local Configuration
- [ ] Create file `.streamlit/secrets.toml` in your project
- [ ] Add Supabase URL to secrets.toml
- [ ] Add Supabase KEY to secrets.toml
- [ ] Add Gemini API key to secrets.toml (if not already there)
- [ ] Verify no extra spaces or quotes in secrets.toml

### Phase 4: Dependencies
- [x] ✅ Supabase package already installed
- [ ] Test import: `python -c "import supabase; print('OK')"`

### Phase 5: Testing
- [ ] Run app: `streamlit run app.py`
- [ ] Login as teacher (teacher / teacher123)
- [ ] Logout
- [ ] Login as student1 (student1 / student123)
- [ ] Submit an answer as student
- [ ] Logout
- [ ] Login as teacher again
- [ ] Check if submission appears in Statistics tab
- [ ] Go to Supabase dashboard → Table Editor → submissions
- [ ] Verify the submission is in the database

### Phase 6: New User Registration
- [ ] Click "Registrarse" on login page
- [ ] Create new student account
- [ ] Login with new account
- [ ] Submit an answer
- [ ] Verify it works

### Phase 7: Verification
- [ ] Supabase Table Editor shows data
- [ ] Teacher can see all students' submissions
- [ ] Students only see their own submissions
- [ ] New users can register successfully
- [ ] No errors in Streamlit console

---

## ✅ Success Criteria

Your setup is successful if:
1. ✅ App runs without errors
2. ✅ You can login with default users
3. ✅ Students can submit answers
4. ✅ Data appears in Supabase dashboard
5. ✅ Teacher sees all submissions
6. ✅ Students see only their own submissions
7. ✅ New users can register

---

## 🆘 If Something Goes Wrong

1. Check `.streamlit/secrets.toml` exists and has correct values
2. Verify Supabase project is active (not paused)
3. Check browser console for errors (F12)
4. Look at Streamlit terminal for Python errors
5. Verify SQL was executed successfully
6. Check Supabase dashboard logs

---

## 📚 Reference Documents

- **Setup Guide:** `SUPABASE_SETUP.md` - Detailed setup instructions
- **Migration Info:** `SUPABASE_MIGRATION.md` - What changed and why
- **Secrets Template:** `.streamlit/secrets.toml.template` - Configuration template

---

## 🎉 All Done?

Once all checkboxes are checked, your app is fully migrated to Supabase! 

**No more JSON files needed!** 🚀

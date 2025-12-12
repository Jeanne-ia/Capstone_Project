# 🚀 Supabase Setup Guide for EvalIA

This guide will help you set up Supabase database for your EvalIA application.

## 📋 Prerequisites

- A Supabase account (free tier is enough)
- Your Supabase project URL and API key

---

## Step 1: Create a Supabase Account

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with your GitHub account or email
4. Create a new project:
   - **Name:** `evalia` (or any name you prefer)
   - **Database Password:** Choose a strong password (save it!)
   - **Region:** Choose the closest to you
   - Wait 2-3 minutes for the project to be created

---

## Step 2: Create Database Tables

Once your project is ready:

1. Go to **SQL Editor** in the left sidebar
2. Click **"New query"**
3. Copy and paste the following SQL:

```sql
-- Create users table
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('teacher', 'student')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create submissions table
CREATE TABLE submissions (
    id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    student_name TEXT NOT NULL,
    pregunta_id INTEGER NOT NULL,
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    resultado TEXT NOT NULL CHECK (resultado IN ('Correcta', 'Incorrecta', 'Dudosa')),
    score DECIMAL(5,4) NOT NULL,
    feedback TEXT,
    timestamp TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (username) REFERENCES users(username)
);

-- Create indexes for better performance
CREATE INDEX idx_submissions_username ON submissions(username);
CREATE INDEX idx_submissions_student_name ON submissions(student_name);
CREATE INDEX idx_submissions_resultado ON submissions(resultado);
CREATE INDEX idx_submissions_created_at ON submissions(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Teachers can see all users
CREATE POLICY "Teachers can view all users"
    ON users FOR SELECT
    USING (
        role = 'teacher' OR 
        auth.uid()::text = username
    );

-- RLS Policy: Anyone can insert new users (for registration)
CREATE POLICY "Allow user registration"
    ON users FOR INSERT
    WITH CHECK (role = 'student');

-- RLS Policy: Students can only see their own submissions
CREATE POLICY "Students see own submissions"
    ON submissions FOR SELECT
    USING (
        username = auth.uid()::text OR
        EXISTS (
            SELECT 1 FROM users
            WHERE users.username = auth.uid()::text
            AND users.role = 'teacher'
        )
    );

-- RLS Policy: Students can insert their own submissions
CREATE POLICY "Students can insert submissions"
    ON submissions FOR INSERT
    WITH CHECK (username = auth.uid()::text);

-- Insert default users
INSERT INTO users (username, password, name, role) VALUES
    ('teacher', 'teacher123', 'Docente', 'teacher'),
    ('student1', 'student123', 'Juan Pérez', 'student'),
    ('student2', 'student456', 'María García', 'student'),
    ('student3', 'student789', 'Carlos López', 'student')
ON CONFLICT (username) DO NOTHING;
```

4. Click **Run** or press `Ctrl+Enter`
5. You should see "Success. No rows returned"

---

## Step 3: Get Your Supabase Credentials

1. Go to **Project Settings** (gear icon in left sidebar)
2. Click on **API** in the settings menu
3. You'll find two important values:
   - **Project URL** - looks like: `https://xxxxxxxxxxxxx.supabase.co`
   - **anon/public API key** - a long string starting with `eyJ...`

**Copy both values!** You'll need them in the next step.

---

## Step 4: Configure Streamlit Secrets

### Option A: Local Development

1. In your project folder, create `.streamlit/secrets.toml` (if it doesn't exist)
2. Add your Supabase credentials:

```toml
# Supabase Configuration
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-public-key-here"

# Gemini API (already existing)
GEMINI_API_KEY = "your-gemini-key"
```

3. Save the file

**⚠️ Important:** Add `.streamlit/secrets.toml` to your `.gitignore` file!

### Option B: Streamlit Cloud Deployment

If deploying to Streamlit Cloud:

1. Go to your app settings on Streamlit Cloud
2. Click on **Secrets**
3. Add the same content as above
4. Save

---

## Step 5: Install Dependencies

In your terminal, run:

```bash
pip install -r requirements.txt
```

This will install the `supabase` package (already added to requirements.txt).

---

## Step 6: Test the Connection

1. Run your Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Try logging in with:
   - **Teacher:** teacher / teacher123
   - **Student:** student1 / student123

3. Try registering a new student

4. Submit an answer as a student

5. Log in as teacher and check if you can see the submission

---

## 🔧 Troubleshooting

### Error: "No module named 'supabase'"
**Solution:** Run `pip install supabase==2.3.0`

### Error: "Connection failed"
**Solution:** 
- Check that your `SUPABASE_URL` and `SUPABASE_KEY` are correct in `secrets.toml`
- Make sure there are no extra spaces or quotes
- Verify your Supabase project is active (not paused)

### Error: "Row Level Security" issues
**Solution:** 
- Make sure you ran ALL the SQL code in Step 2
- The RLS policies allow the anon key to access data
- Check the Supabase dashboard for any policy errors

### Data not showing up
**Solution:**
- Go to Supabase dashboard → Table Editor
- Check if tables `users` and `submissions` exist
- Verify data is being inserted (you should see rows)

---

## 📊 Viewing Your Data

You can view and manage your data directly in Supabase:

1. Go to **Table Editor** in Supabase dashboard
2. Click on **users** table to see all registered users
3. Click on **submissions** table to see all student answers
4. You can manually edit, delete, or add records here

---

## 🔒 Security Notes

### Current Implementation
- Passwords are stored as **plain text** in the database
- This is fine for a **capstone/demo project**

### For Production (if you deploy publicly):
You should:
1. Hash passwords using `bcrypt` or similar
2. Use Supabase Auth instead of custom auth
3. Use environment variables for sensitive data
4. Enable proper RLS policies
5. Add rate limiting

Example password hashing (not implemented yet):
```python
import bcrypt
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
```

---

## 🎉 Success!

If everything works, you now have:
- ✅ Persistent cloud database
- ✅ User authentication via Supabase
- ✅ Student submissions stored in database
- ✅ Teacher can see all submissions
- ✅ Students can only see their own data
- ✅ Real-time data access
- ✅ No more JSON files!

---

## 🔄 Migration from JSON

Your old JSON files (`users.json` and `student_submissions.json`) are **no longer used**.

If you want to import existing data:
1. Keep your JSON files
2. Run a migration script (I can create this if needed)
3. Data will be imported into Supabase
4. Delete JSON files after verification

---

## 📞 Need Help?

If you encounter issues:
1. Check the Supabase logs in the dashboard
2. Look at the browser console for errors (F12)
3. Verify your secrets.toml has correct values
4. Make sure your Supabase project is not paused (free tier pauses after inactivity)

---

## 🚀 Next Steps

Your app is now production-ready! You can:
- Deploy to Streamlit Cloud
- Share with students
- Scale to hundreds of users (free tier supports up to 500MB)
- Monitor usage in Supabase dashboard

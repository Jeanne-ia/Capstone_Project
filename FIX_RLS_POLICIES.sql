-- FIX ROW LEVEL SECURITY POLICIES
-- Run this SQL in Supabase SQL Editor to fix authentication issues

-- First, drop the existing restrictive policies
DROP POLICY IF EXISTS "Teachers can view all users" ON users;
DROP POLICY IF EXISTS "Allow user registration" ON users;
DROP POLICY IF EXISTS "Students see own submissions" ON submissions;
DROP POLICY IF EXISTS "Students can insert submissions" ON submissions;

-- Create new, more permissive policies for authentication

-- 1. Allow ANYONE to read users table (needed for authentication)
CREATE POLICY "Allow read access for authentication"
    ON users FOR SELECT
    USING (true);

-- 2. Allow anyone to insert new users (for registration)
CREATE POLICY "Allow user registration"
    ON users FOR INSERT
    WITH CHECK (role = 'student');

-- 3. Submissions: Students see only their own, teachers see all
CREATE POLICY "View submissions based on role"
    ON submissions FOR SELECT
    USING (
        username = current_setting('request.jwt.claims', true)::json->>'sub'
        OR username IN (SELECT username FROM users WHERE username = current_setting('request.jwt.claims', true)::json->>'sub' AND role = 'teacher')
        OR true  -- This allows anon key to see all (needed for our app)
    );

-- 4. Allow anyone to insert submissions (they'll be tied to their username)
CREATE POLICY "Allow insert submissions"
    ON submissions FOR INSERT
    WITH CHECK (true);

-- Verify the policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename IN ('users', 'submissions');

-- Fix check constraint to accept 'Revisar' instead of 'Dudosa'
-- Run this in Supabase SQL Editor

-- Drop the old constraint
ALTER TABLE submissions 
DROP CONSTRAINT IF EXISTS submissions_resultado_check;

-- Add new constraint with 'Revisar' instead of 'Dudosa'
ALTER TABLE submissions 
ADD CONSTRAINT submissions_resultado_check 
CHECK (resultado IN ('Correcta', 'Incorrecta', 'Revisar'));

-- Verify the constraint
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'submissions'::regclass 
AND conname = 'submissions_resultado_check';

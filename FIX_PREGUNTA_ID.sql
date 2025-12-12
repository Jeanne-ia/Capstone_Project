-- Change pregunta_id from INTEGER to TEXT to accept question IDs like "Q001"
ALTER TABLE submissions 
ALTER COLUMN pregunta_id TYPE TEXT;

-- Verify the change
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'submissions' 
AND column_name = 'pregunta_id';

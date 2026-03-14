-- Creates the dev and test databases.
-- Run with: psql -f create_db.sql
--
-- Note: if either database already exists Postgres will return an error.
-- This is safe to ignore -- no data will be affected.

CREATE DATABASE sheffield_assessment;
CREATE DATABASE sheffield_assessment_test;

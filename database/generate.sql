-- Create the appropriate Database and connect
CREATE DATABASE podcasting;
\c podcasting;

-- Create the extension required for UUID's
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Remove the table if it already exists
DROP TABLE IF EXISTS Podcast;

-- Create the required table
CREATE TABLE Podcast
(
    id uuid NOT NULL DEFAULT uuid_generate_v1(),
    title text NOT NULL,
    media text NOT NULL,
    posterkey text NOT NULL,
    date timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT podcast_pkey PRIMARY KEY (id)
);
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';
CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.edited = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;
ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;
SET default_tablespace = '';
SET default_table_access_method = heap;
CREATE TABLE public.accesses (
    category_id integer NOT NULL,
    user_id integer NOT NULL,
    role integer NOT NULL
);
-- Role: belongs to the interval [0, 4]
-- - 0: Viewer: can only read tasks
-- - 1: Doer: can change the status of tasks
-- - 2: Writer: can create, delete and edit tasks
-- - 3: Administrator: can give roles and manage users with a role of at most 2
-- - 4: Owner: Can also manage administrators (all permissions)
ALTER TABLE public.accesses OWNER TO postgres;
CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    color character varying(6) NOT NULL
);
ALTER TABLE public.categories OWNER TO postgres;
CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.categories_id_seq OWNER TO postgres;
ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;
CREATE TABLE public.status (
    id integer NOT NULL,
    name character varying(20) NOT NULL,
    description text
);
ALTER TABLE public.status OWNER TO postgres;
CREATE SEQUENCE public.status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.status_id_seq OWNER TO postgres;
ALTER SEQUENCE public.status_id_seq OWNED BY public.status.id;
CREATE TABLE public.tasks (
    id integer NOT NULL,
    name character text NOT NULL,
    parent integer,
    status_id integer,
    category_id integer,
    creation timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    edited timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
);
ALTER TABLE public.tasks OWNER TO postgres;
CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.tasks_id_seq OWNER TO postgres;
ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;
CREATE TABLE public.tokens (
    token character varying(32) NOT NULL,
    user_id integer,
    expiration timestamp without time zone DEFAULT (CURRENT_TIMESTAMP + '01:00:00'::interval)
);
ALTER TABLE public.tokens OWNER TO postgres;
CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(15) NOT NULL,
    password character varying(64) NOT NULL
);
ALTER TABLE public.users OWNER TO postgres;
CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.users_id_seq OWNER TO postgres;
ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);
ALTER TABLE ONLY public.status ALTER COLUMN id SET DEFAULT nextval('public.status_id_seq'::regclass);
ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);
ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
ALTER TABLE ONLY public.accesses
    ADD CONSTRAINT accesses_pkey PRIMARY KEY (category_id, user_id);
ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.status
    ADD CONSTRAINT status_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.tokens
    ADD CONSTRAINT tokens_pkey PRIMARY KEY (token);
ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_name_unique UNIQUE (name);
ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
CREATE TRIGGER update_my_table_updated_at BEFORE UPDATE ON public.tasks FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
ALTER TABLE ONLY public.accesses
    ADD CONSTRAINT accesses_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.accesses
    ADD CONSTRAINT accesses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.tokens
    ADD CONSTRAINT tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
GRANT ALL ON SCHEMA public TO goapi;
GRANT ALL ON TABLE public.accesses TO goapi;
GRANT ALL ON TABLE public.categories TO goapi;
GRANT ALL ON SEQUENCE public.categories_id_seq TO goapi;
GRANT ALL ON TABLE public.status TO goapi;
GRANT ALL ON SEQUENCE public.status_id_seq TO goapi;
GRANT ALL ON TABLE public.tasks TO goapi;
GRANT ALL ON SEQUENCE public.tasks_id_seq TO goapi;
GRANT ALL ON TABLE public.tokens TO goapi;
GRANT ALL ON TABLE public.users TO goapi;
GRANT ALL ON SEQUENCE public.users_id_seq TO goapi;
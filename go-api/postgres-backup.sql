--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13 (Debian 15.13-0+deb12u1)
-- Dumped by pg_dump version 15.13 (Debian 15.13-0+deb12u1)

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

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

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

--
-- Name: accesses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accesses (
    category_id integer NOT NULL,
    user_id integer NOT NULL,
    role integer NOT NULL
);


ALTER TABLE public.accesses OWNER TO postgres;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    color character varying(6) NOT NULL
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.categories_id_seq OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.status (
    id integer NOT NULL,
    name character varying(20) NOT NULL,
    description text
);


ALTER TABLE public.status OWNER TO postgres;

--
-- Name: status_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.status_id_seq OWNER TO postgres;

--
-- Name: status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.status_id_seq OWNED BY public.status.id;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    name text NOT NULL,
    parent integer,
    status_id integer,
    category_id integer,
    creation timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    edited timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.tasks OWNER TO postgres;

--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tasks_id_seq OWNER TO postgres;

--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tokens (
    token character varying(32) NOT NULL,
    user_id integer,
    expiration timestamp without time zone DEFAULT (CURRENT_TIMESTAMP + '01:00:00'::interval)
);


ALTER TABLE public.tokens OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(15) NOT NULL,
    password character varying(64) NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: status id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.status ALTER COLUMN id SET DEFAULT nextval('public.status_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: accesses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accesses (category_id, user_id, role) FROM stdin;
1	1	4
1	2	2
2	2	4
2	3	1
3	3	4
3	1	2
4	1	4
4	2	0
5	2	4
5	3	1
6	3	4
6	1	2
7	1	4
7	3	1
8	2	4
8	1	0
9	3	4
9	2	1
10	1	4
11	5	4
12	5	4
13	5	4
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (id, name, color) FROM stdin;
1	Marketing Campaigns	FF5733
2	Software Development	33FF57
3	Financial Reports	3357FF
4	Human Resources	F39C12
5	Customer Support	1ABC9C
6	IT Infrastructure	2ECC71
7	Supply Chain Management	16A085
8	Legal Documents	9B59B6
9	Product Design	3498DB
10	Operations	2980B9
11	My Unique Test Category	0000FF
12	Testing	FF0000
13	Testing	FF0000
\.


--
-- Data for Name: status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.status (id, name, description) FROM stdin;
1	Not Started	The Task Has Not Yet Been Initiated.
2	In Progress	The Task Is Currently Being Worked On.
3	Done	The Task Has Been Successfully Completed.
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (id, name, parent, status_id, category_id, creation, edited) FROM stdin;
1	Design Marketing Flyer	\N	1	1	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
2	Develop Login Page	\N	2	2	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
3	Compile Q4 Financial Report	\N	3	3	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
4	Onboard New HR Members	\N	1	4	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
5	Respond to Customer Queries	\N	2	5	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
6	Set Up New Server	\N	1	6	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
7	Optimize Supply Chain Routes	\N	3	7	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
8	Revise Legal Contract	\N	1	8	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
9	Sketch Product Prototype	\N	2	9	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
10	Plan Monthly Operations Meeting	\N	1	10	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
11	Finalize Marketing Strategy	1	1	1	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
12	Code Review	2	3	2	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
13	Validate Financial Data	3	2	3	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
14	Prepare Training Material	4	1	4	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
15	Escalate High Priority Tickets	5	3	5	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
16	Configure Firewall Settings	6	2	6	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
17	Negotiate with Suppliers	7	1	7	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
18	Draft Contract Terms	8	3	8	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
19	Model Design Changes	9	2	9	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
20	Update Operations Plan	10	1	10	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
21	Create Social Media Ads	\N	1	1	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
22	Refactor Codebase	\N	2	2	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
23	Update Budget Projections	\N	3	3	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
24	Conduct Performance Reviews	\N	1	4	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
25	Handle Complaints	\N	2	5	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
26	Backup Database	\N	1	6	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
27	Streamline Inventory	\N	3	7	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
28	Proofread Contract	\N	1	8	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
29	Test Product Prototype	\N	2	9	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
30	Organize Team Lunch	\N	1	10	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
31	Schedule Launch	21	1	1	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
32	Fix Bugs	22	2	2	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
33	Review Cash Flow	23	3	3	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
34	Schedule Training Sessions	24	1	4	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
35	Follow Up on Tickets	25	3	5	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
36	Perform Security Audit	26	2	6	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
37	Audit Supplier Costs	27	1	7	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
38	Negotiate Clause	28	3	8	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
39	Improve Usability	29	2	9	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
40	Arrange Venue	30	1	10	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
41	Design Email Template	\N	1	1	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
42	Implement API Documentation	\N	2	2	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
43	Prepare Revenue Report	\N	3	3	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
44	Recruit Junior Staff	\N	1	4	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
45	Provide Technical Assistance	\N	2	5	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
46	Restore from Backup	\N	1	6	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
47	Forecast Sales	\N	3	7	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
48	Revise Compliance Documents	\N	1	8	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
49	Design Prototype Interface	\N	2	9	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
50	Coordinate Logistics	\N	1	10	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
51	Write Content	41	1	1	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
52	Document Endpoints	42	2	2	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
53	Analyze Metrics	43	3	3	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
54	Conduct Interviews	44	1	4	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
55	Answer FAQs	45	3	5	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
56	Identify Issues	46	2	6	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
57	Gather Data	47	1	7	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
58	Update Regulations	48	3	8	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
59	Mock User Scenarios	49	2	9	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
60	Plan Transport	50	1	10	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
61	Create Landing Page	\N	1	1	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
62	Write Unit Tests	\N	2	2	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
63	Prepare Income Statement	\N	3	3	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
64	Manage Recruitment Process	\N	1	4	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
65	Maintain Customer Portal	\N	2	5	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
66	Patch Vulnerabilities	\N	1	6	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
67	Evaluate Supplier Performance	\N	3	7	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
68	Review Legal Compliance	\N	1	8	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
69	Refine Prototype Layout	\N	2	9	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
70	Arrange Shipping	\N	1	10	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
71	Optimize SEO	61	1	1	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
72	Debug Code	62	2	2	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
73	Forecast Expenses	63	3	3	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
74	Schedule Interviews	64	1	4	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
75	Update Knowledge Base	65	3	5	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
76	Monitor Network Traffic	66	2	6	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
77	Audit Supplier Agreements	67	1	7	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
78	Prepare Legal Brief	68	3	8	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
79	User Testing	69	2	9	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
80	Plan Delivery Schedule	70	1	10	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
81	Launch Campaign	71	1	1	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
82	Refactor Functions	72	2	2	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
83	Prepare Balance Sheet	73	3	3	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
84	Provide Onboarding Materials	74	1	4	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
85	Update FAQ Section	75	3	5	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
86	Secure Systems	76	2	6	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
87	Review Supplier Deliverables	77	1	7	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
88	Prepare Legal Pleading	78	3	8	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
89	Iterate on Design	79	2	9	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
90	Coordinate Distribution	80	1	10	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
91	Create Blog Post	\N	1	1	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
92	Write Integration Tests	\N	2	2	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
93	Prepare Profit Loss Statement	\N	3	3	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
94	Hire Freelancers	\N	1	4	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
95	Support Technical Issues	\N	2	5	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
96	Upgrade Server Hardware	\N	1	6	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
97	Forecast Trends	\N	3	7	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
98	Update Legal Notices	\N	1	8	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
99	Design UI Mockups	\N	2	9	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
100	Plan Route Optimization	\N	1	10	2025-06-13 10:18:46.35704	2025-06-13 10:18:46.35704
\.


--
-- Data for Name: tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tokens (token, user_id, expiration) FROM stdin;
L2mDQhRY5zqTCcEHwSK8txp0rABeEkaQ	2	2025-07-11 13:34:16.193995
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, name, password) FROM stdin;
1	alice	$2a$10$EiwWJ27MfEA6rvyYKm5ahOVpIiywZi5mRCo63pmDRoS52deGk4CiG
2	bob	$2a$10$EiwWJ27MfEA6rvyYKm5ahOVpIiywZi5mRCo63pmDRoS52deGk4CiG
3	charlie	$2a$10$EiwWJ27MfEA6rvyYKm5ahOVpIiywZi5mRCo63pmDRoS52deGk4CiG
4	testAA	$2a$10$EiwWJ27MfEA6rvyYKm5ahOVpIiywZi5mRCo63pmDRoS52deGk4CiG
5	toto	$2a$10$EiwWJ27MfEA6rvyYKm5ahOVpIiywZi5mRCo63pmDRoS52deGk4CiG
\.


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_id_seq', 13, true);


--
-- Name: status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.status_id_seq', 1, false);


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- Name: accesses accesses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accesses
    ADD CONSTRAINT accesses_pkey PRIMARY KEY (category_id, user_id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: status status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.status
    ADD CONSTRAINT status_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: tokens tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tokens
    ADD CONSTRAINT tokens_pkey PRIMARY KEY (token);


--
-- Name: users users_name_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_name_unique UNIQUE (name);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: tasks update_my_table_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_my_table_updated_at BEFORE UPDATE ON public.tasks FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: accesses accesses_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accesses
    ADD CONSTRAINT accesses_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE CASCADE;


--
-- Name: accesses accesses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accesses
    ADD CONSTRAINT accesses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: tasks tasks_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE CASCADE;


--
-- Name: tasks tasks_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status(id) ON DELETE CASCADE;


--
-- Name: tokens tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tokens
    ADD CONSTRAINT tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO goapi;


--
-- Name: TABLE accesses; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.accesses TO goapi;


--
-- Name: TABLE categories; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.categories TO goapi;


--
-- Name: SEQUENCE categories_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.categories_id_seq TO goapi;


--
-- Name: TABLE status; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.status TO goapi;


--
-- Name: SEQUENCE status_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.status_id_seq TO goapi;


--
-- Name: TABLE tasks; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.tasks TO goapi;


--
-- Name: SEQUENCE tasks_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.tasks_id_seq TO goapi;


--
-- Name: TABLE tokens; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.tokens TO goapi;


--
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.users TO goapi;


--
-- Name: SEQUENCE users_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.users_id_seq TO goapi;


--
-- PostgreSQL database dump complete
--


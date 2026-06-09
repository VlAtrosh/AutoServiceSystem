--
-- PostgreSQL database dump
--

\restrict XgbB1XBmmIITYlgMpg4pxvXNIa4dEx3yMO3dGcrVsaFNLBhjwEtJ9UQYpX0vOgE

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg13+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg13+1)

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
-- Name: paymentmethod; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.paymentmethod AS ENUM (
    'CASH',
    'CARD',
    'ONLINE',
    'BANK_TRANSFER'
);


ALTER TYPE public.paymentmethod OWNER TO postgres;

--
-- Name: paymentstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.paymentstatus AS ENUM (
    'PENDING',
    'PAID',
    'PARTIAL',
    'REFUNDED',
    'CANCELLED'
);


ALTER TYPE public.paymentstatus OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cars; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cars (
    id character varying NOT NULL,
    client_id character varying NOT NULL,
    brand character varying NOT NULL,
    model character varying NOT NULL,
    year integer,
    vin character varying,
    license_plate character varying NOT NULL,
    engine_type character varying,
    engine_volume double precision,
    horsepower integer,
    transmission character varying,
    drive_unit character varying,
    color character varying,
    mileage integer,
    purchase_date timestamp without time zone,
    last_service_date timestamp without time zone,
    next_service_date timestamp without time zone,
    comment character varying,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.cars OWNER TO postgres;

--
-- Name: clients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clients (
    id character varying NOT NULL,
    user_id character varying,
    discount double precision,
    total_spent double precision,
    total_orders integer,
    last_visit timestamp without time zone,
    status character varying,
    created_at timestamp without time zone
);


ALTER TABLE public.clients OWNER TO postgres;

--
-- Name: mechanics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mechanics (
    id character varying NOT NULL,
    user_id character varying,
    specialization character varying,
    experience_years double precision,
    education character varying,
    certificates character varying,
    status character varying,
    rating double precision,
    completed_orders_count integer,
    total_hours_worked double precision,
    total_earned double precision,
    schedule character varying,
    phone character varying,
    email character varying,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.mechanics OWNER TO postgres;

--
-- Name: order_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_items (
    id character varying NOT NULL,
    order_id character varying,
    client_id character varying,
    item_type character varying,
    item_id character varying,
    name character varying,
    quantity double precision,
    price double precision,
    total double precision
);


ALTER TABLE public.order_items OWNER TO postgres;

--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id character varying NOT NULL,
    number character varying NOT NULL,
    client_id character varying NOT NULL,
    car_id character varying NOT NULL,
    car_info character varying NOT NULL,
    mechanic_id character varying,
    status character varying,
    total double precision,
    created_at timestamp without time zone,
    completed_at timestamp without time zone
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: parts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parts (
    id character varying NOT NULL,
    code character varying,
    article character varying,
    name character varying NOT NULL,
    description text,
    price double precision NOT NULL,
    purchase_price double precision,
    quantity integer,
    reserved integer,
    warehouse character varying,
    category character varying,
    brand character varying,
    is_active integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.parts OWNER TO postgres;

--
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    id character varying NOT NULL,
    order_id character varying NOT NULL,
    client_id character varying NOT NULL,
    amount double precision NOT NULL,
    method public.paymentmethod,
    status public.paymentstatus,
    payment_date timestamp without time zone,
    confirmed_at timestamp without time zone,
    transaction_id character varying,
    payment_system character varying,
    receipt_url character varying,
    receipt_number character varying,
    received_by character varying,
    comment character varying
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- Name: posts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.posts (
    id integer NOT NULL,
    name character varying NOT NULL,
    status character varying,
    current_order_id character varying
);


ALTER TABLE public.posts OWNER TO postgres;

--
-- Name: posts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.posts_id_seq OWNER TO postgres;

--
-- Name: posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id character varying NOT NULL,
    username character varying NOT NULL,
    email character varying NOT NULL,
    last_name character varying NOT NULL,
    first_name character varying NOT NULL,
    middle_name character varying,
    passport_data character varying,
    inn character varying,
    phone character varying,
    address character varying,
    registration_address character varying,
    hashed_password character varying NOT NULL,
    is_active boolean,
    role character varying,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    comment character varying
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: works; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.works (
    id character varying NOT NULL,
    code character varying,
    name character varying NOT NULL,
    description text,
    price_per_hour double precision NOT NULL,
    min_hours double precision,
    max_hours double precision,
    category character varying,
    subcategory character varying,
    times_performed integer,
    average_rating double precision,
    is_active integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.works OWNER TO postgres;

--
-- Name: posts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);


--
-- Data for Name: cars; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cars (id, client_id, brand, model, year, vin, license_plate, engine_type, engine_volume, horsepower, transmission, drive_unit, color, mileage, purchase_date, last_service_date, next_service_date, comment, created_at, updated_at) FROM stdin;
4057d971-efba-433e-b9a3-d1d8cb91a50f	116b7792-5b8b-46d2-8dde-c8f2a4cb10a0	BMW	X5	2022	WBAXX123456789012	A123BC77	\N	\N	\N	\N	\N	Черный	\N	\N	\N	\N	\N	2026-06-09 14:52:58.470522	2026-06-09 14:53:44.948743
d71f24b8-fbbf-4ae7-ad4a-36bfebe07c4f	de081c9a-89e7-40cf-b11d-c64a4bb2fc7a	Camry	2	2021	WBAXX123456789011	A123BC76	\N	\N	\N	\N	\N	Черный	\N	\N	\N	\N	\N	2026-06-09 14:56:05.656143	2026-06-09 16:47:35.336158
\.


--
-- Data for Name: clients; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clients (id, user_id, discount, total_spent, total_orders, last_visit, status, created_at) FROM stdin;
cc0e4887-764e-4e04-86f4-e6d1870d0577	116b7792-5b8b-46d2-8dde-c8f2a4cb10a0	0	0	0	\N	active	2026-06-09 14:50:43.806576
f352ae5c-df4a-42ab-a4a2-9a15a4785133	de081c9a-89e7-40cf-b11d-c64a4bb2fc7a	0	0	0	\N	active	2026-06-09 16:46:55.185138
\.


--
-- Data for Name: mechanics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mechanics (id, user_id, specialization, experience_years, education, certificates, status, rating, completed_orders_count, total_hours_worked, total_earned, schedule, phone, email, created_at, updated_at) FROM stdin;
726d9127-ff1f-4f02-86f7-536509b10860	9b73fc12-f720-4736-b1ed-f5d3aac78953	engine	5	\N	\N	free	5	0	0	0	\N	\N	\N	2026-06-09 14:45:36.890829	\N
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_items (id, order_id, client_id, item_type, item_id, name, quantity, price, total) FROM stdin;
7dc66339	26c4dc73	\N	work	77748b2a-5ee2-4b39-a983-a4cf08ef581f	Диагностика двигателя	2	1500	3000
e083c5ab	26c4dc73	\N	work	d77b2282-1528-4398-b637-c8d83eba45ea	Замена масла	1	1000	1000
39e6b6e5	26c4dc73	\N	work	77748b2a-5ee2-4b39-a983-a4cf08ef581f	Диагностика двигателя	1	1500	1500
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (id, number, client_id, car_id, car_info, mechanic_id, status, total, created_at, completed_at) FROM stdin;
26c4dc73	ЗН-26c4dc73	cc0e4887-764e-4e04-86f4-e6d1870d0577	4057d971-efba-433e-b9a3-d1d8cb91a50f	BMW X5 2022	726d9127-ff1f-4f02-86f7-536509b10860	diagnostics	5500	2026-06-09 15:39:22.744119	2026-06-09 16:34:49.925638
\.


--
-- Data for Name: parts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parts (id, code, article, name, description, price, purchase_price, quantity, reserved, warehouse, category, brand, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payments (id, order_id, client_id, amount, method, status, payment_date, confirmed_at, transaction_id, payment_system, receipt_url, receipt_number, received_by, comment) FROM stdin;
\.


--
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.posts (id, name, status, current_order_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, last_name, first_name, middle_name, passport_data, inn, phone, address, registration_address, hashed_password, is_active, role, created_at, updated_at, comment) FROM stdin;
2a37d3d0-f125-472d-b82c-5c29cac46393	admin	admin@example.com	Admin	Admin	\N	\N	\N	\N	\N	\N	$2b$12$BkVW9Q7Zrq4ni44NKLPjTePUJlxzoByQ4xIcyG5YbI5nXU1S6LmBW	t	director	2026-06-09 14:25:21.799107	\N	\N
9b73fc12-f720-4736-b1ed-f5d3aac78953	mechanic_ivan	mechanic@example.com	Механиков	Иван	\N	\N	\N	+7 999 111 22 33	\N	\N	$2b$12$VgzPko0hPkRuIviwWLiFS.xE6iriD4HQiZS8ornjHYrGVWNy6rtly	t	mechanic	2026-06-09 14:42:23.099693	\N	\N
116b7792-5b8b-46d2-8dde-c8f2a4cb10a0	ivan_petrov	ivan@example.com	Петров	Иван	\N	\N	\N	+7 999 123 45 67	\N	\N	$2b$12$aFnmlAFSZHxrtEjbP9iTAe5C6BfqK/.4SUgRp8bO8fRNdzedtNRGW	t	client	2026-06-09 14:50:43.800147	\N	\N
de081c9a-89e7-40cf-b11d-c64a4bb2fc7a	Pavel	Pavel@example.com	Волков	Павел	\N	\N	\N	+7 999 152 10 67	\N	\N	$2b$12$FQyPNlRUWzik.fIeNkmyPONjEg0CVN5s1QIO3LzRC8Hvk3X6YuVWC	t	client	2026-06-09 16:46:55.176973	\N	\N
\.


--
-- Data for Name: works; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.works (id, code, name, description, price_per_hour, min_hours, max_hours, category, subcategory, times_performed, average_rating, is_active, created_at, updated_at) FROM stdin;
d77b2282-1528-4398-b637-c8d83eba45ea	OIL-001	Замена масла	Замена моторного масла и масляного фильтра	1000	1	1	ТО	\N	0	0	1	2026-06-09 15:41:17.701726	\N
77748b2a-5ee2-4b39-a983-a4cf08ef581f	DIAG-001	Диагностика двигателя	Компьютерная диагностика	1500	0.5	2	Диагностика	\N	0	0	1	2026-06-09 15:41:40.737362	\N
a69ecf9b-cdcb-4fb1-8168-16166f74a69c	BRAKE-001	Замена тормозных колодок	Замена передних и задних колодок	800	1	1.5	Тормозная система	\N	0	0	1	2026-06-09 15:41:51.833364	\N
b64bc17c-76b1-411b-aaf8-4381db60c2e2	SUSP-001	Ремонт подвески	Диагностика и ремонт ходовой части	1200	2	4	Подвеска	\N	0	0	1	2026-06-09 15:41:59.973701	\N
826405be-3a54-4161-b50b-2516aa027121	TIMING-001	Замена ремня ГРМ	Замена ремня газораспределительного механизма	2000	3	5	Двигатель	\N	0	0	1	2026-06-09 15:42:08.192422	\N
\.


--
-- Name: posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.posts_id_seq', 1, false);


--
-- Name: cars cars_license_plate_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cars
    ADD CONSTRAINT cars_license_plate_key UNIQUE (license_plate);


--
-- Name: cars cars_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cars
    ADD CONSTRAINT cars_pkey PRIMARY KEY (id);


--
-- Name: cars cars_vin_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cars
    ADD CONSTRAINT cars_vin_key UNIQUE (vin);


--
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- Name: clients clients_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_user_id_key UNIQUE (user_id);


--
-- Name: mechanics mechanics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mechanics
    ADD CONSTRAINT mechanics_pkey PRIMARY KEY (id);


--
-- Name: mechanics mechanics_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mechanics
    ADD CONSTRAINT mechanics_user_id_key UNIQUE (user_id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: orders orders_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_number_key UNIQUE (number);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: parts parts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parts
    ADD CONSTRAINT parts_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: works works_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.works
    ADD CONSTRAINT works_pkey PRIMARY KEY (id);


--
-- Name: ix_parts_article; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_parts_article ON public.parts USING btree (article);


--
-- Name: ix_parts_brand; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_parts_brand ON public.parts USING btree (brand);


--
-- Name: ix_parts_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_parts_category ON public.parts USING btree (category);


--
-- Name: ix_parts_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_parts_code ON public.parts USING btree (code);


--
-- Name: ix_parts_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_parts_name ON public.parts USING btree (name);


--
-- Name: ix_works_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_works_category ON public.works USING btree (category);


--
-- Name: ix_works_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_works_code ON public.works USING btree (code);


--
-- Name: ix_works_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_works_name ON public.works USING btree (name);


--
-- Name: cars cars_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cars
    ADD CONSTRAINT cars_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.users(id);


--
-- Name: clients clients_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: mechanics mechanics_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mechanics
    ADD CONSTRAINT mechanics_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: order_items order_items_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.users(id);


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- Name: orders orders_car_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_car_id_fkey FOREIGN KEY (car_id) REFERENCES public.cars(id);


--
-- Name: orders orders_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- Name: orders orders_mechanic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_mechanic_id_fkey FOREIGN KEY (mechanic_id) REFERENCES public.mechanics(id);


--
-- Name: payments payments_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- Name: payments payments_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- Name: payments payments_received_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_received_by_fkey FOREIGN KEY (received_by) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict XgbB1XBmmIITYlgMpg4pxvXNIa4dEx3yMO3dGcrVsaFNLBhjwEtJ9UQYpX0vOgE


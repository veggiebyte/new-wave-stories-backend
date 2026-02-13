--
-- PostgreSQL database dump
--

\restrict 3zvHPzO0ioYI3gAIEbNpKtslV1fg2f88SnkDopjqaW66fvsisWnh0IqCIg6kdaD

-- Dumped from database version 16.11 (Homebrew)
-- Dumped by pg_dump version 16.11 (Homebrew)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: board_items; Type: TABLE; Schema: public; Owner: cindys
--

CREATE TABLE public.board_items (
    id integer NOT NULL,
    board_id integer NOT NULL,
    catalog_item_id integer NOT NULL,
    sort_index integer DEFAULT 0
);


ALTER TABLE public.board_items OWNER TO cindys;

--
-- Name: board_items_id_seq; Type: SEQUENCE; Schema: public; Owner: cindys
--

CREATE SEQUENCE public.board_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.board_items_id_seq OWNER TO cindys;

--
-- Name: board_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cindys
--

ALTER SEQUENCE public.board_items_id_seq OWNED BY public.board_items.id;


--
-- Name: boards; Type: TABLE; Schema: public; Owner: cindys
--

CREATE TABLE public.boards (
    id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying(100) NOT NULL,
    city character varying(100),
    vibe character varying(100),
    song character varying(150),
    story text,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.boards OWNER TO cindys;

--
-- Name: boards_id_seq; Type: SEQUENCE; Schema: public; Owner: cindys
--

CREATE SEQUENCE public.boards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.boards_id_seq OWNER TO cindys;

--
-- Name: boards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cindys
--

ALTER SEQUENCE public.boards_id_seq OWNED BY public.boards.id;


--
-- Name: catalog_items; Type: TABLE; Schema: public; Owner: cindys
--

CREATE TABLE public.catalog_items (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    category character varying(50) NOT NULL,
    image_url text
);


ALTER TABLE public.catalog_items OWNER TO cindys;

--
-- Name: catalog_items_id_seq; Type: SEQUENCE; Schema: public; Owner: cindys
--

CREATE SEQUENCE public.catalog_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.catalog_items_id_seq OWNER TO cindys;

--
-- Name: catalog_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cindys
--

ALTER SEQUENCE public.catalog_items_id_seq OWNED BY public.catalog_items.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: cindys
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(255) NOT NULL
);


ALTER TABLE public.users OWNER TO cindys;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: cindys
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO cindys;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cindys
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: board_items id; Type: DEFAULT; Schema: public; Owner: cindys
--

ALTER TABLE ONLY public.board_items ALTER COLUMN id SET DEFAULT nextval('public.board_items_id_seq'::regclass);


--
-- Name: boards id; Type: DEFAULT; Schema: public; Owner: cindys
--

ALTER TABLE ONLY public.boards ALTER COLUMN id SET DEFAULT nextval('public.boards_id_seq'::regclass);


--
-- Name: catalog_items id; Type: DEFAULT; Schema: public; Owner: cindys
--

ALTER TABLE ONLY public.catalog_items ALTER COLUMN id SET DEFAULT nextval('public.catalog_items_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: cindys
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: board_items board_items_pkey; Type: CONSTRAINT; Schema: public; Owner: cindys
--

ALTER TABLE ONLY public.board_items
    ADD CONSTRAINT board_items_pkey PRIMARY KEY (id);


--
-- Name: boards boards_pkey; Type: CONSTRAINT; Schema: public; Owner: cindys
--

ALTER TABLE ONLY public.boards
    ADD CONSTRAINT boards_pkey PRIMARY KEY (id);


--
-- Name: catalog_items catalog_items_pkey; Type: CONSTRAINT; Schema: public; Owner: cindys
--

ALTER TABLE ONLY public.catalog_items
    ADD CONSTRAINT catalog_items_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: cindys
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: board_items board_items_board_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cindys
--

ALTER TABLE ONLY public.board_items
    ADD CONSTRAINT board_items_board_id_fkey FOREIGN KEY (board_id) REFERENCES public.boards(id) ON DELETE CASCADE;


--
-- Name: board_items board_items_catalog_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cindys
--

ALTER TABLE ONLY public.board_items
    ADD CONSTRAINT board_items_catalog_item_id_fkey FOREIGN KEY (catalog_item_id) REFERENCES public.catalog_items(id) ON DELETE CASCADE;


--
-- Name: boards boards_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cindys
--

ALTER TABLE ONLY public.boards
    ADD CONSTRAINT boards_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 3zvHPzO0ioYI3gAIEbNpKtslV1fg2f88SnkDopjqaW66fvsisWnh0IqCIg6kdaD


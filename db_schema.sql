--
-- PostgreSQL database dump
--

-- Dumped from database version 11.7 (Ubuntu 11.7-2.pgdg16.04+1)
-- Dumped by pg_dump version 11.7 (Ubuntu 11.7-2.pgdg16.04+1)

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
-- Name: translations; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA translations;


ALTER SCHEMA translations OWNER TO postgres;

--
-- Name: get_default_notetype(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_default_notetype() RETURNS uuid
    LANGUAGE plpgsql
    AS $$BEGIN
	RETURN (select uid from notetypes where name = 'draft');
END
$$;


ALTER FUNCTION public.get_default_notetype() OWNER TO postgres;

--
-- Name: uuid_generate_v1(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.uuid_generate_v1() RETURNS uuid
    LANGUAGE c STRICT
    AS '$libdir/uuid-ossp', 'uuid_generate_v1';


ALTER FUNCTION public.uuid_generate_v1() OWNER TO postgres;

--
-- Name: uuid_generate_v1mc(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.uuid_generate_v1mc() RETURNS uuid
    LANGUAGE c STRICT
    AS '$libdir/uuid-ossp', 'uuid_generate_v1mc';


ALTER FUNCTION public.uuid_generate_v1mc() OWNER TO postgres;

--
-- Name: uuid_generate_v3(uuid, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.uuid_generate_v3(namespace uuid, name text) RETURNS uuid
    LANGUAGE c IMMUTABLE STRICT
    AS '$libdir/uuid-ossp', 'uuid_generate_v3';


ALTER FUNCTION public.uuid_generate_v3(namespace uuid, name text) OWNER TO postgres;

--
-- Name: uuid_generate_v4(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.uuid_generate_v4() RETURNS uuid
    LANGUAGE c STRICT
    AS '$libdir/uuid-ossp', 'uuid_generate_v4';


ALTER FUNCTION public.uuid_generate_v4() OWNER TO postgres;

--
-- Name: uuid_generate_v5(uuid, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.uuid_generate_v5(namespace uuid, name text) RETURNS uuid
    LANGUAGE c IMMUTABLE STRICT
    AS '$libdir/uuid-ossp', 'uuid_generate_v5';


ALTER FUNCTION public.uuid_generate_v5(namespace uuid, name text) OWNER TO postgres;

--
-- Name: uuid_nil(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.uuid_nil() RETURNS uuid
    LANGUAGE c IMMUTABLE STRICT
    AS '$libdir/uuid-ossp', 'uuid_nil';


ALTER FUNCTION public.uuid_nil() OWNER TO postgres;

--
-- Name: uuid_ns_dns(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.uuid_ns_dns() RETURNS uuid
    LANGUAGE c IMMUTABLE STRICT
    AS '$libdir/uuid-ossp', 'uuid_ns_dns';


ALTER FUNCTION public.uuid_ns_dns() OWNER TO postgres;

--
-- Name: uuid_ns_oid(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.uuid_ns_oid() RETURNS uuid
    LANGUAGE c IMMUTABLE STRICT
    AS '$libdir/uuid-ossp', 'uuid_ns_oid';


ALTER FUNCTION public.uuid_ns_oid() OWNER TO postgres;

--
-- Name: uuid_ns_url(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.uuid_ns_url() RETURNS uuid
    LANGUAGE c IMMUTABLE STRICT
    AS '$libdir/uuid-ossp', 'uuid_ns_url';


ALTER FUNCTION public.uuid_ns_url() OWNER TO postgres;

--
-- Name: uuid_ns_x500(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.uuid_ns_x500() RETURNS uuid
    LANGUAGE c IMMUTABLE STRICT
    AS '$libdir/uuid-ossp', 'uuid_ns_x500';


ALTER FUNCTION public.uuid_ns_x500() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: channels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.channels (
    uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.channels OWNER TO postgres;

--
-- Name: intentions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.intentions (
    uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text NOT NULL,
    description uuid,
    important boolean DEFAULT false NOT NULL,
    recurrent boolean DEFAULT false NOT NULL,
    parent uuid,
    created timestamp(6) without time zone DEFAULT timezone('MSK'::text, now()) NOT NULL,
    finished timestamp(6) without time zone,
    startdate timestamp(6) without time zone,
    frequency integer,
    reminder integer,
    oldstartdate timestamp(6) without time zone
);


ALTER TABLE public.intentions OWNER TO postgres;

--
-- Name: COLUMN intentions.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.intentions.name IS 'The task itself';


--
-- Name: COLUMN intentions.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.intentions.description IS 'Link to the associated post with details';


--
-- Name: COLUMN intentions.important; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.intentions.important IS 'Whether task is recurrent (completion resets the timer)';


--
-- Name: COLUMN intentions.parent; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.intentions.parent IS 'For subtasks (defines higher-order task)';


--
-- Name: COLUMN intentions.created; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.intentions.created IS 'Creation date';


--
-- Name: COLUMN intentions.finished; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.intentions.finished IS 'Completion date';


--
-- Name: COLUMN intentions.startdate; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.intentions.startdate IS 'For recurrent tasks: time of resetting';


--
-- Name: COLUMN intentions.frequency; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.intentions.frequency IS 'For recurrent tasks: days since resetting until deadline';


--
-- Name: COLUMN intentions.reminder; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.intentions.reminder IS 'For recurrent tasks: days before deadline when task becomes visible';


--
-- Name: COLUMN intentions.oldstartdate; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.intentions.oldstartdate IS 'For recurrent tasks: time of previous resetting (for undo purposes)';


--
-- Name: notes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notes (
    uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    maintext text,
    created timestamp(6) without time zone DEFAULT timezone('MSK'::text, now()) NOT NULL,
    changed timestamp(6) without time zone,
    important boolean DEFAULT false NOT NULL,
    url text,
    type uuid DEFAULT public.get_default_notetype() NOT NULL
);


ALTER TABLE public.notes OWNER TO postgres;

--
-- Name: COLUMN notes.type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.notes.type IS 'Link to the "notetypes" table';


--
-- Name: notes_topics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notes_topics (
    uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    note uuid NOT NULL,
    topic uuid NOT NULL
);


ALTER TABLE public.notes_topics OWNER TO postgres;

--
-- Name: notetypes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notetypes (
    uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text NOT NULL,
    fullname text NOT NULL
);


ALTER TABLE public.notetypes OWNER TO postgres;

--
-- Name: people; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.people (
    uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text NOT NULL,
    my_interest smallint,
    their_interest smallint,
    description text,
    birthdate date
);


ALTER TABLE public.people OWNER TO postgres;

--
-- Name: people_channels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.people_channels (
    uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    person uuid NOT NULL,
    channel uuid NOT NULL
);


ALTER TABLE public.people_channels OWNER TO postgres;

--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- Name: topics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.topics (
    uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.topics OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text,
    login text,
    password text
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users_permissions (
    uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    userid uuid NOT NULL,
    permissionid uuid NOT NULL
);


ALTER TABLE public.users_permissions OWNER TO postgres;

--
-- Name: translations; Type: TABLE; Schema: translations; Owner: postgres
--

CREATE TABLE translations.translations (
    uid uuid NOT NULL,
    engname text,
    runame text,
    original text,
    translation text,
    link text
);


ALTER TABLE translations.translations OWNER TO postgres;

--
-- Name: channels channels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.channels
    ADD CONSTRAINT channels_pkey PRIMARY KEY (uid);


--
-- Name: intentions intentions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intentions
    ADD CONSTRAINT intentions_pkey PRIMARY KEY (uid);


--
-- Name: notes notes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY (uid);


--
-- Name: notes_topics notes_topics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes_topics
    ADD CONSTRAINT notes_topics_pkey PRIMARY KEY (uid);


--
-- Name: notetypes notetypes_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notetypes
    ADD CONSTRAINT notetypes_name_key UNIQUE (name);


--
-- Name: notetypes notetypes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notetypes
    ADD CONSTRAINT notetypes_pkey PRIMARY KEY (uid);


--
-- Name: people_channels people_channels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people_channels
    ADD CONSTRAINT people_channels_pkey PRIMARY KEY (uid);


--
-- Name: people people_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT people_pkey PRIMARY KEY (uid);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (uid);


--
-- Name: topics topics_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.topics
    ADD CONSTRAINT topics_name_key UNIQUE (name);


--
-- Name: topics topics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.topics
    ADD CONSTRAINT topics_pkey PRIMARY KEY (uid);


--
-- Name: users_permissions users_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_permissions
    ADD CONSTRAINT users_permissions_pkey PRIMARY KEY (uid);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (uid);


--
-- Name: intentions intentions_description_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intentions
    ADD CONSTRAINT intentions_description_fkey FOREIGN KEY (description) REFERENCES public.notes(uid) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: intentions intentions_parent_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intentions
    ADD CONSTRAINT intentions_parent_fkey FOREIGN KEY (parent) REFERENCES public.intentions(uid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: notes_topics notes_topics_note_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes_topics
    ADD CONSTRAINT notes_topics_note_fkey FOREIGN KEY (note) REFERENCES public.notes(uid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: notes_topics notes_topics_topic_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes_topics
    ADD CONSTRAINT notes_topics_topic_fkey FOREIGN KEY (topic) REFERENCES public.topics(uid) ON UPDATE CASCADE;


--
-- Name: people_channels people_channels_channel_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people_channels
    ADD CONSTRAINT people_channels_channel_fkey FOREIGN KEY (channel) REFERENCES public.channels(uid) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: people_channels people_channels_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people_channels
    ADD CONSTRAINT people_channels_person_fkey FOREIGN KEY (person) REFERENCES public.people(uid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--


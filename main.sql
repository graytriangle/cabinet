-- SQL Manager for PostgreSQL 5.6.2.46690
-- ---------------------------------------
-- Host      : localhost
-- Database  : main
-- Version   : PostgreSQL 9.6.2 on x86_64-pc-mingw64, compiled by gcc.exe (Rev5, Built by MSYS2 project) 4.9.2, 64-bit



--
-- Definition for function uuid_generate_v1 (OID = 16385) : 
--
SET search_path = public, pg_catalog;
SET check_function_bodies = false;
CREATE FUNCTION public.uuid_generate_v1 (
)
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_generate_v1'
LANGUAGE c
STRICT;
--
-- Definition for function uuid_generate_v1mc (OID = 16386) : 
--
CREATE FUNCTION public.uuid_generate_v1mc (
)
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_generate_v1mc'
LANGUAGE c
STRICT;
--
-- Definition for function uuid_generate_v3 (OID = 16387) : 
--
CREATE FUNCTION public.uuid_generate_v3 (
  namespace uuid,
  name text
)
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_generate_v3'
LANGUAGE c
IMMUTABLE STRICT;
--
-- Definition for function uuid_generate_v4 (OID = 16388) : 
--
CREATE FUNCTION public.uuid_generate_v4 (
)
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_generate_v4'
LANGUAGE c
STRICT;
--
-- Definition for function uuid_generate_v5 (OID = 16389) : 
--
CREATE FUNCTION public.uuid_generate_v5 (
  namespace uuid,
  name text
)
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_generate_v5'
LANGUAGE c
IMMUTABLE STRICT;
--
-- Definition for function uuid_nil (OID = 16390) : 
--
CREATE FUNCTION public.uuid_nil (
)
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_nil'
LANGUAGE c
IMMUTABLE STRICT;
--
-- Definition for function uuid_ns_dns (OID = 16391) : 
--
CREATE FUNCTION public.uuid_ns_dns (
)
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_ns_dns'
LANGUAGE c
IMMUTABLE STRICT;
--
-- Definition for function uuid_ns_oid (OID = 16392) : 
--
CREATE FUNCTION public.uuid_ns_oid (
)
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_ns_oid'
LANGUAGE c
IMMUTABLE STRICT;
--
-- Definition for function uuid_ns_url (OID = 16393) : 
--
CREATE FUNCTION public.uuid_ns_url (
)
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_ns_url'
LANGUAGE c
IMMUTABLE STRICT;
--
-- Definition for function uuid_ns_x500 (OID = 16394) : 
--
CREATE FUNCTION public.uuid_ns_x500 (
)
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_ns_x500'
LANGUAGE c
IMMUTABLE STRICT;
--
-- Structure for table notes (OID = 16395) : 
--
CREATE TABLE public.notes (
    uid uuid DEFAULT uuid_generate_v4() NOT NULL,
    maintext text,
    created timestamp without time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    changed timestamp without time zone,
    important boolean DEFAULT false NOT NULL,
    url text
)
WITH (oids = false);
--
-- Structure for table notes_topics (OID = 16404) : 
--
CREATE TABLE public.notes_topics (
    uid uuid DEFAULT uuid_generate_v4() NOT NULL,
    note uuid NOT NULL,
    topic uuid NOT NULL
)
WITH (oids = false);
--
-- Structure for table topics (OID = 16408) : 
--
CREATE TABLE public.topics (
    uid uuid DEFAULT uuid_generate_v4() NOT NULL,
    name text NOT NULL
)
WITH (oids = false);
--
-- Structure for table tasks (OID = 24633) : 
--
CREATE TABLE public.tasks (
    uid uuid DEFAULT uuid_generate_v4() NOT NULL,
    name text NOT NULL,
    description text,
    important boolean DEFAULT false NOT NULL,
    status boolean DEFAULT true NOT NULL,
    parent uuid,
    created timestamp without time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    finished timestamp without time zone
)
WITH (oids = false);
--
-- Definition for index notes_pkey (OID = 16415) : 
--
ALTER TABLE ONLY notes
    ADD CONSTRAINT notes_pkey
    PRIMARY KEY (uid);
--
-- Definition for index notes_topics_pkey (OID = 16417) : 
--
ALTER TABLE ONLY notes_topics
    ADD CONSTRAINT notes_topics_pkey
    PRIMARY KEY (uid);
--
-- Definition for index topics_name_key (OID = 16419) : 
--
ALTER TABLE ONLY topics
    ADD CONSTRAINT topics_name_key
    UNIQUE (name);
--
-- Definition for index topics_pkey (OID = 16421) : 
--
ALTER TABLE ONLY topics
    ADD CONSTRAINT topics_pkey
    PRIMARY KEY (uid);
--
-- Definition for index notes_topics_fk (OID = 16423) : 
--
ALTER TABLE ONLY notes_topics
    ADD CONSTRAINT notes_topics_fk
    FOREIGN KEY (note) REFERENCES notes(uid) ON DELETE CASCADE;
--
-- Definition for index notes_topics_fk1 (OID = 16428) : 
--
ALTER TABLE ONLY notes_topics
    ADD CONSTRAINT notes_topics_fk1
    FOREIGN KEY (topic) REFERENCES topics(uid);
--
-- Definition for index tasks_pkey (OID = 24643) : 
--
ALTER TABLE ONLY tasks
    ADD CONSTRAINT tasks_pkey
    PRIMARY KEY (uid);
--
-- Definition for index tasks_fk (OID = 24645) : 
--
ALTER TABLE ONLY tasks
    ADD CONSTRAINT tasks_fk
    FOREIGN KEY (parent) REFERENCES tasks(uid) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Comments
--
COMMENT ON SCHEMA public IS 'standard public schema';
COMMENT ON COLUMN public.tasks.name IS 'The task itself';
COMMENT ON COLUMN public.tasks.description IS 'Optional short description/details';
COMMENT ON COLUMN public.tasks.important IS 'Whether task is important (defines order of view)';
COMMENT ON COLUMN public.tasks.status IS 'Whether task is active (true is for active)';
COMMENT ON COLUMN public.tasks.parent IS 'For subtasks (defines higher-order task)';
COMMENT ON COLUMN public.tasks.created IS 'Creation date';
COMMENT ON COLUMN public.tasks.finished IS 'Completion date';

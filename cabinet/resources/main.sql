/*
Navicat PGSQL Data Transfer

Source Server         : cabinet-heroku
Source Server Version : 90601
Source Host           : ec2-54-247-177-33.eu-west-1.compute.amazonaws.com:5432
Source Database       : d3g15d5rjd0b42
Source Schema         : public

Target Server Type    : PGSQL
Target Server Version : 90601
File Encoding         : 65001

Date: 2017-08-06 23:55:26
*/


-- ----------------------------
-- Table structure for intentions
-- ----------------------------
DROP TABLE IF EXISTS "intentions";
CREATE TABLE "intentions" (
"uid" uuid DEFAULT uuid_generate_v4() NOT NULL,
"name" text COLLATE "default" NOT NULL,
"description" uuid,
"important" bool DEFAULT false NOT NULL,
"recurrent" bool DEFAULT false NOT NULL,
"parent" uuid,
"created" timestamp(6) DEFAULT timezone('MSK'::text, now()) NOT NULL,
"finished" timestamp(6),
"startdate" timestamp(6),
"frequency" int4,
"reminder" int4,
"oldstartdate" timestamp(6)
)
WITH (OIDS=FALSE)

;
COMMENT ON COLUMN "intentions"."name" IS 'The task itself';
COMMENT ON COLUMN "intentions"."description" IS 'Link to the associated post with details';
COMMENT ON COLUMN "intentions"."important" IS 'Whether task is recurrent (completion resets the timer)';
COMMENT ON COLUMN "intentions"."parent" IS 'For subtasks (defines higher-order task)';
COMMENT ON COLUMN "intentions"."created" IS 'Creation date';
COMMENT ON COLUMN "intentions"."finished" IS 'Completion date';
COMMENT ON COLUMN "intentions"."startdate" IS 'For recurrent tasks: time of resetting';
COMMENT ON COLUMN "intentions"."frequency" IS 'For recurrent tasks: days since resetting until deadline';
COMMENT ON COLUMN "intentions"."reminder" IS 'For recurrent tasks: days before deadline when task becomes visible';
COMMENT ON COLUMN "intentions"."oldstartdate" IS 'For recurrent tasks: time of previous resetting (for undo purposes)';

-- ----------------------------
-- Table structure for notes
-- ----------------------------
DROP TABLE IF EXISTS "notes";
CREATE TABLE "notes" (
"uid" uuid DEFAULT uuid_generate_v4() NOT NULL,
"maintext" text COLLATE "default",
"created" timestamp(6) DEFAULT timezone('MSK'::text, now()) NOT NULL,
"changed" timestamp(6),
"important" bool DEFAULT false NOT NULL,
"url" text COLLATE "default",
"type" uuid DEFAULT get_default_notetype() NOT NULL
)
WITH (OIDS=FALSE)

;
COMMENT ON COLUMN "notes"."type" IS 'Link to the "notetypes" table';

-- ----------------------------
-- Table structure for notes_topics
-- ----------------------------
DROP TABLE IF EXISTS "notes_topics";
CREATE TABLE "notes_topics" (
"uid" uuid DEFAULT uuid_generate_v4() NOT NULL,
"note" uuid NOT NULL,
"topic" uuid NOT NULL
)
WITH (OIDS=FALSE)

;

-- ----------------------------
-- Table structure for notetypes
-- ----------------------------
DROP TABLE IF EXISTS "notetypes";
CREATE TABLE "notetypes" (
"uid" uuid DEFAULT uuid_generate_v4() NOT NULL,
"name" text COLLATE "default" NOT NULL,
"fullname" text COLLATE "default" NOT NULL
)
WITH (OIDS=FALSE)

;

-- ----------------------------
-- Table structure for topics
-- ----------------------------
DROP TABLE IF EXISTS "topics";
CREATE TABLE "topics" (
"uid" uuid DEFAULT uuid_generate_v4() NOT NULL,
"name" text COLLATE "default" NOT NULL
)
WITH (OIDS=FALSE)

;

-- ----------------------------
-- Function structure for get_default_notetype
-- ----------------------------
CREATE OR REPLACE FUNCTION "get_default_notetype"()
  RETURNS "pg_catalog"."uuid" AS $BODY$BEGIN
	RETURN (select uid from notetypes where name = 'draft');
END
$BODY$
  LANGUAGE 'plpgsql' VOLATILE COST 100
;

-- ----------------------------
-- Function structure for uuid_generate_v1
-- ----------------------------
CREATE OR REPLACE FUNCTION "uuid_generate_v1"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_generate_v1'
  LANGUAGE 'c' VOLATILE STRICT  COST 1
;

-- ----------------------------
-- Function structure for uuid_generate_v1mc
-- ----------------------------
CREATE OR REPLACE FUNCTION "uuid_generate_v1mc"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_generate_v1mc'
  LANGUAGE 'c' VOLATILE STRICT  COST 1
;

-- ----------------------------
-- Function structure for uuid_generate_v3
-- ----------------------------
CREATE OR REPLACE FUNCTION "uuid_generate_v3"("namespace" uuid, "name" text)
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_generate_v3'
  LANGUAGE 'c' IMMUTABLE STRICT  COST 1
;

-- ----------------------------
-- Function structure for uuid_generate_v4
-- ----------------------------
CREATE OR REPLACE FUNCTION "uuid_generate_v4"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_generate_v4'
  LANGUAGE 'c' VOLATILE STRICT  COST 1
;

-- ----------------------------
-- Function structure for uuid_generate_v5
-- ----------------------------
CREATE OR REPLACE FUNCTION "uuid_generate_v5"("namespace" uuid, "name" text)
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_generate_v5'
  LANGUAGE 'c' IMMUTABLE STRICT  COST 1
;

-- ----------------------------
-- Function structure for uuid_nil
-- ----------------------------
CREATE OR REPLACE FUNCTION "uuid_nil"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_nil'
  LANGUAGE 'c' IMMUTABLE STRICT  COST 1
;

-- ----------------------------
-- Function structure for uuid_ns_dns
-- ----------------------------
CREATE OR REPLACE FUNCTION "uuid_ns_dns"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_ns_dns'
  LANGUAGE 'c' IMMUTABLE STRICT  COST 1
;

-- ----------------------------
-- Function structure for uuid_ns_oid
-- ----------------------------
CREATE OR REPLACE FUNCTION "uuid_ns_oid"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_ns_oid'
  LANGUAGE 'c' IMMUTABLE STRICT  COST 1
;

-- ----------------------------
-- Function structure for uuid_ns_url
-- ----------------------------
CREATE OR REPLACE FUNCTION "uuid_ns_url"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_ns_url'
  LANGUAGE 'c' IMMUTABLE STRICT  COST 1
;

-- ----------------------------
-- Function structure for uuid_ns_x500
-- ----------------------------
CREATE OR REPLACE FUNCTION "uuid_ns_x500"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_ns_x500'
  LANGUAGE 'c' IMMUTABLE STRICT  COST 1
;

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Primary Key structure for table intentions
-- ----------------------------
ALTER TABLE "intentions" ADD PRIMARY KEY ("uid");

-- ----------------------------
-- Primary Key structure for table notes
-- ----------------------------
ALTER TABLE "notes" ADD PRIMARY KEY ("uid");

-- ----------------------------
-- Primary Key structure for table notes_topics
-- ----------------------------
ALTER TABLE "notes_topics" ADD PRIMARY KEY ("uid");

-- ----------------------------
-- Uniques structure for table notetypes
-- ----------------------------
ALTER TABLE "notetypes" ADD UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table notetypes
-- ----------------------------
ALTER TABLE "notetypes" ADD PRIMARY KEY ("uid");

-- ----------------------------
-- Uniques structure for table topics
-- ----------------------------
ALTER TABLE "topics" ADD UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table topics
-- ----------------------------
ALTER TABLE "topics" ADD PRIMARY KEY ("uid");

-- ----------------------------
-- Foreign Key structure for table "intentions"
-- ----------------------------
ALTER TABLE "intentions" ADD FOREIGN KEY ("description") REFERENCES "notes" ("uid") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "intentions" ADD FOREIGN KEY ("parent") REFERENCES "intentions" ("uid") ON DELETE CASCADE ON UPDATE CASCADE;

-- ----------------------------
-- Foreign Key structure for table "notes_topics"
-- ----------------------------
ALTER TABLE "notes_topics" ADD FOREIGN KEY ("topic") REFERENCES "topics" ("uid") ON DELETE NO ACTION ON UPDATE CASCADE;
ALTER TABLE "notes_topics" ADD FOREIGN KEY ("note") REFERENCES "notes" ("uid") ON DELETE CASCADE ON UPDATE CASCADE;

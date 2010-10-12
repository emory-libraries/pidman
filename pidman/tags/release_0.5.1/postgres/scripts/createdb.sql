--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'Standard public schema';


--
-- Name: plperlu; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: 
--

CREATE PROCEDURAL LANGUAGE plperlu;


--
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: 
--

CREATE PROCEDURAL LANGUAGE plpgsql;


SET search_path = public, pg_catalog;

--
-- Name: archive_pids(); Type: FUNCTION; Schema: public; Owner: croddy
--

CREATE FUNCTION archive_pids() RETURNS "trigger"
    AS $$BEGIN
        INSERT INTO archive_pids (pid_id, pid, domain_id, active, name, last_modified, ext_system_id, ext_system_key, creator_id, created_at, modified_by) VALUES (
          OLD.id,
          OLD.pid,
          OLD.domain_id,
          OLD.active,
          OLD.name,
          OLD.last_modified,
          OLD.ext_system_id,
          OLD.ext_system_key,
          OLD.creator_id,
          OLD.created_at,
          OLD.modified_by
        ) ;
      RETURN NULL ;
      END ;$$
    LANGUAGE plpgsql STRICT;


ALTER FUNCTION public.archive_pids() OWNER TO croddy;

--
-- Name: archive_targets(); Type: FUNCTION; Schema: public; Owner: croddy
--

CREATE FUNCTION archive_targets() RETURNS "trigger"
    AS $$BEGIN
        INSERT INTO archive_targets (pid_id, pid, uri, qualify, proxy_id) VALUES (
          OLD.pid_id,
          OLD.pid,
          OLD.uri,
          OLD.qualify,
          OLD.proxy_id
        ) ;
        RETURN NULL ;
      END ;$$
    LANGUAGE plpgsql STRICT;


ALTER FUNCTION public.archive_targets() OWNER TO croddy;

--
-- Name: mint_noid(character varying); Type: FUNCTION; Schema: public; Owner: croddy
--

CREATE FUNCTION mint_noid(character varying) RETURNS character varying
    AS $_X$

use Noid;

$noid = Noid::dbopen($_[0], 0);
$id = Noid::mint($noid, "", "");
Noid::dbclose($noid);

return $id;

$_X$
    LANGUAGE plperlu;


ALTER FUNCTION public.mint_noid(character varying) OWNER TO croddy;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: archive_pids; Type: TABLE; Schema: public; Owner: persis; Tablespace: 
--

CREATE TABLE archive_pids (
    pid_id integer NOT NULL,
    pid character varying(255),
    domain_id integer NOT NULL,
    active boolean,
    name character varying(1023),
    ext_system_id integer,
    ext_system_key character varying(1023),
    creator_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    modified_by integer NOT NULL,
    updated_at timestamp without time zone,
    id bigserial NOT NULL
);


ALTER TABLE public.archive_pids OWNER TO persis;

--
-- Name: archive_targets; Type: TABLE; Schema: public; Owner: persis; Tablespace: 
--

CREATE TABLE archive_targets (
    pid_id integer,
    pid character varying(255),
    uri character varying(2048) NOT NULL,
    qualify character varying(255),
    sort_order integer NOT NULL,
    proxy_id integer,
    id bigserial NOT NULL
);


ALTER TABLE public.archive_targets OWNER TO persis;

--
-- Name: domains; Type: TABLE; Schema: public; Owner: persis; Tablespace: 
--

CREATE TABLE domains (
    id serial NOT NULL,
    name character varying(255) NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.domains OWNER TO persis;

--
-- Name: ext_systems; Type: TABLE; Schema: public; Owner: persis; Tablespace: 
--

CREATE TABLE ext_systems (
    id serial NOT NULL,
    name character varying(127) NOT NULL,
    key_field character varying(127) NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.ext_systems OWNER TO persis;

--
-- Name: permissions; Type: TABLE; Schema: public; Owner: persis; Tablespace: 
--

CREATE TABLE permissions (
    id serial NOT NULL,
    user_id integer NOT NULL,
    domain_id integer NOT NULL,
    role_id integer NOT NULL
);


ALTER TABLE public.permissions OWNER TO persis;

--
-- Name: pids; Type: TABLE; Schema: public; Owner: persis; Tablespace: 
--

CREATE TABLE pids (
    pid character varying(255),
    domain_id integer DEFAULT 0 NOT NULL,
    active boolean DEFAULT true NOT NULL,
    name character varying(1023) NOT NULL,
    ext_system_id integer,
    ext_system_key character varying(1023),
    creator_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    modified_by integer NOT NULL,
    "type" character varying(25) DEFAULT 'Purl'::character varying,
    updated_at timestamp without time zone,
    id bigserial NOT NULL
);


ALTER TABLE public.pids OWNER TO persis;

--
-- Name: proxies; Type: TABLE; Schema: public; Owner: persis; Tablespace: 
--

CREATE TABLE proxies (
    id serial NOT NULL,
    name character varying(127) NOT NULL,
    transform character varying(127) NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.proxies OWNER TO persis;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: persis; Tablespace: 
--

CREATE TABLE roles (
    id serial NOT NULL,
    "role" character varying(64) NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.roles OWNER TO persis;

--
-- Name: schema_info; Type: TABLE; Schema: public; Owner: croddy; Tablespace: 
--

CREATE TABLE schema_info (
    version integer
);


ALTER TABLE public.schema_info OWNER TO croddy;

--
-- Name: targets; Type: TABLE; Schema: public; Owner: persis; Tablespace: 
--

CREATE TABLE targets (
    pid_id integer NOT NULL,
    pid character varying(255) NOT NULL,
    uri character varying(2048) NOT NULL,
    qualify character varying(255),
    proxy_id integer,
    id bigserial NOT NULL
);


ALTER TABLE public.targets OWNER TO persis;

--
-- Name: users; Type: TABLE; Schema: public; Owner: persis; Tablespace: 
--

CREATE TABLE users (
    id serial NOT NULL,
    username character varying(32) NOT NULL,
    "first" character varying(127),
    "last" character varying(127),
    email character varying(320) NOT NULL,
    "password" character varying(150),
    is_superuser boolean DEFAULT false NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.users OWNER TO persis;

--
-- Name: domains_pkey; Type: CONSTRAINT; Schema: public; Owner: persis; Tablespace: 
--

ALTER TABLE ONLY domains
    ADD CONSTRAINT domains_pkey PRIMARY KEY (id);


--
-- Name: ext_systems_pkey; Type: CONSTRAINT; Schema: public; Owner: persis; Tablespace: 
--

ALTER TABLE ONLY ext_systems
    ADD CONSTRAINT ext_systems_pkey PRIMARY KEY (id);


--
-- Name: permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: persis; Tablespace: 
--

ALTER TABLE ONLY permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: proxies_pkey; Type: CONSTRAINT; Schema: public; Owner: persis; Tablespace: 
--

ALTER TABLE ONLY proxies
    ADD CONSTRAINT proxies_pkey PRIMARY KEY (id);


--
-- Name: roles_pkey; Type: CONSTRAINT; Schema: public; Owner: persis; Tablespace: 
--

ALTER TABLE ONLY roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: persis; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: domains_name_key; Type: INDEX; Schema: public; Owner: persis; Tablespace: 
--

CREATE UNIQUE INDEX domains_name_key ON domains USING btree (name);


--
-- Name: ext_systems_name_key; Type: INDEX; Schema: public; Owner: persis; Tablespace: 
--

CREATE UNIQUE INDEX ext_systems_name_key ON ext_systems USING btree (name);


--
-- Name: pid_index; Type: INDEX; Schema: public; Owner: persis; Tablespace: 
--

CREATE INDEX pid_index ON pids USING btree (pid);


--
-- Name: pids_pid_key; Type: INDEX; Schema: public; Owner: persis; Tablespace: 
--

CREATE UNIQUE INDEX pids_pid_key ON pids USING btree (pid);


--
-- Name: proxies_name_key; Type: INDEX; Schema: public; Owner: persis; Tablespace: 
--

CREATE UNIQUE INDEX proxies_name_key ON proxies USING btree (name);


--
-- Name: users_email_key; Type: INDEX; Schema: public; Owner: persis; Tablespace: 
--

CREATE UNIQUE INDEX users_email_key ON users USING btree (email);


--
-- Name: users_username_key; Type: INDEX; Schema: public; Owner: persis; Tablespace: 
--

CREATE UNIQUE INDEX users_username_key ON users USING btree (username);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO persis;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: archive_pids; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE archive_pids FROM PUBLIC;
REVOKE ALL ON TABLE archive_pids FROM persis;
GRANT ALL ON TABLE archive_pids TO persis;


--
-- Name: archive_targets; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE archive_targets FROM PUBLIC;
REVOKE ALL ON TABLE archive_targets FROM persis;
GRANT ALL ON TABLE archive_targets TO persis;


--
-- Name: domains; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE domains FROM PUBLIC;
REVOKE ALL ON TABLE domains FROM persis;
GRANT ALL ON TABLE domains TO persis;


--
-- Name: domains_id_seq; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE domains_id_seq FROM PUBLIC;
REVOKE ALL ON TABLE domains_id_seq FROM persis;
GRANT ALL ON TABLE domains_id_seq TO persis;


--
-- Name: ext_systems; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE ext_systems FROM PUBLIC;
REVOKE ALL ON TABLE ext_systems FROM persis;
GRANT ALL ON TABLE ext_systems TO persis;


--
-- Name: ext_systems_id_seq; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE ext_systems_id_seq FROM PUBLIC;
REVOKE ALL ON TABLE ext_systems_id_seq FROM persis;
GRANT ALL ON TABLE ext_systems_id_seq TO persis;


--
-- Name: permissions; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE permissions FROM PUBLIC;
REVOKE ALL ON TABLE permissions FROM persis;
GRANT ALL ON TABLE permissions TO persis;


--
-- Name: permissions_id_seq; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE permissions_id_seq FROM PUBLIC;
REVOKE ALL ON TABLE permissions_id_seq FROM persis;
GRANT ALL ON TABLE permissions_id_seq TO persis;


--
-- Name: pids; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE pids FROM PUBLIC;
REVOKE ALL ON TABLE pids FROM persis;
GRANT ALL ON TABLE pids TO persis;


--
-- Name: proxies; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE proxies FROM PUBLIC;
REVOKE ALL ON TABLE proxies FROM persis;
GRANT ALL ON TABLE proxies TO persis;


--
-- Name: proxies_id_seq; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE proxies_id_seq FROM PUBLIC;
REVOKE ALL ON TABLE proxies_id_seq FROM persis;
GRANT ALL ON TABLE proxies_id_seq TO persis;


--
-- Name: roles; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE roles FROM PUBLIC;
REVOKE ALL ON TABLE roles FROM persis;
GRANT ALL ON TABLE roles TO persis;


--
-- Name: roles_id_seq; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE roles_id_seq FROM PUBLIC;
REVOKE ALL ON TABLE roles_id_seq FROM persis;
GRANT ALL ON TABLE roles_id_seq TO persis;


--
-- Name: schema_info; Type: ACL; Schema: public; Owner: croddy
--

REVOKE ALL ON TABLE schema_info FROM PUBLIC;
REVOKE ALL ON TABLE schema_info FROM croddy;
GRANT ALL ON TABLE schema_info TO croddy;
GRANT ALL ON TABLE schema_info TO jbwhite;
GRANT SELECT,UPDATE ON TABLE schema_info TO PUBLIC;
GRANT ALL ON TABLE schema_info TO persis;


--
-- Name: targets; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE targets FROM PUBLIC;
REVOKE ALL ON TABLE targets FROM persis;
GRANT ALL ON TABLE targets TO persis;


--
-- Name: users; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE users FROM PUBLIC;
REVOKE ALL ON TABLE users FROM persis;
GRANT ALL ON TABLE users TO persis;


--
-- Name: users_id_seq; Type: ACL; Schema: public; Owner: persis
--

REVOKE ALL ON TABLE users_id_seq FROM PUBLIC;
REVOKE ALL ON TABLE users_id_seq FROM persis;
GRANT ALL ON TABLE users_id_seq TO persis;


--
-- PostgreSQL database dump complete
--


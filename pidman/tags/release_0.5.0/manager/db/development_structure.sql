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
    AS $$	BEGIN
		INSERT INTO archive_pids (pid_id, pid, proxy_id, domain_id, active, name, last_modified, ext_system_id, ext_system_key, creator_id, created_at, modified_by) VALUES (
			OLD.id,
			OLD.pid,
			OLD.proxy_id,
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
	END ;
$$
    LANGUAGE plpgsql STRICT;


--
-- Name: archive_targets(); Type: FUNCTION; Schema: public; Owner: jbwhite
--

CREATE FUNCTION archive_targets() RETURNS "trigger"
    AS $$	BEGIN
  INSERT INTO archive_targets (pid_id, pid, uri, qualify) VALUES (
        OLD.pid_id,
  	OLD.pid,
  	OLD.uri,
  	OLD.qualify
  ) ;
  RETURN NULL ;
  END ;
  $$
    LANGUAGE plpgsql STRICT;


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


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: archive_pids; Type: TABLE; Schema: public; Owner: jbwhite; Tablespace: 
--

CREATE TABLE archive_pids (
    id serial NOT NULL,
    pid_id integer NOT NULL,
    pid character varying(255),
    proxy_id integer DEFAULT 0 NOT NULL,
    domain_id integer NOT NULL,
    active boolean,
    name character varying(1023),
    last_modified timestamp with time zone NOT NULL,
    ext_system_id integer,
    ext_system_key character varying(1023),
    creator_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    modified_by integer NOT NULL
);


--
-- Name: archive_targets; Type: TABLE; Schema: public; Owner: persis; Tablespace: 
--

CREATE TABLE archive_targets (
    id serial NOT NULL,
    pid_id integer,
    pid character varying(255),
    uri character varying(2048) NOT NULL,
    qualify character varying(255),
    sort_order serial NOT NULL
);


SET default_with_oids = true;

--
-- Name: domains; Type: TABLE; Schema: public; Owner: jbwhite; Tablespace: 
--

CREATE TABLE domains (
    id serial NOT NULL,
    name character varying(255) NOT NULL,
    last_modified timestamp with time zone DEFAULT now() NOT NULL,
    nickname character varying(20) NOT NULL
);


--
-- Name: TABLE domains; Type: COMMENT; Schema: public; Owner: jbwhite
--

COMMENT ON TABLE domains IS 'domains for grouping pids';


--
-- Name: COLUMN domains.id; Type: COMMENT; Schema: public; Owner: jbwhite
--

COMMENT ON COLUMN domains.id IS 'primary key';


--
-- Name: COLUMN domains.name; Type: COMMENT; Schema: public; Owner: jbwhite
--

COMMENT ON COLUMN domains.name IS 'human-readable description of domain';


--
-- Name: COLUMN domains.last_modified; Type: COMMENT; Schema: public; Owner: jbwhite
--

COMMENT ON COLUMN domains.last_modified IS 'timestamp of last modification';


--
-- Name: COLUMN domains.nickname; Type: COMMENT; Schema: public; Owner: jbwhite
--

COMMENT ON COLUMN domains.nickname IS 'short lookup name';


--
-- Name: ext_systems; Type: TABLE; Schema: public; Owner: croddy; Tablespace: 
--

CREATE TABLE ext_systems (
    id serial NOT NULL,
    name character varying(127) NOT NULL,
    key_field character varying(127) NOT NULL,
    last_modified timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE ext_systems; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON TABLE ext_systems IS 'external systems containing additional data relating to pids';


--
-- Name: COLUMN ext_systems.id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN ext_systems.id IS 'primary key';


--
-- Name: COLUMN ext_systems.name; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN ext_systems.name IS 'human-readable description of external system';


--
-- Name: COLUMN ext_systems.key_field; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN ext_systems.key_field IS 'human-readable description of field referenced in external system';


--
-- Name: COLUMN ext_systems.last_modified; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN ext_systems.last_modified IS 'timestamp of last modification';


SET default_with_oids = false;

--
-- Name: permissions; Type: TABLE; Schema: public; Owner: jbwhite; Tablespace: 
--

CREATE TABLE permissions (
    id serial NOT NULL,
    user_id integer NOT NULL,
    domain_id integer NOT NULL,
    role_id integer NOT NULL
);


--
-- Name: TABLE permissions; Type: COMMENT; Schema: public; Owner: jbwhite
--

COMMENT ON TABLE permissions IS 'defines user role for each domain';


--
-- Name: COLUMN permissions.id; Type: COMMENT; Schema: public; Owner: jbwhite
--

COMMENT ON COLUMN permissions.id IS 'primary key';


--
-- Name: COLUMN permissions.user_id; Type: COMMENT; Schema: public; Owner: jbwhite
--

COMMENT ON COLUMN permissions.user_id IS 'foreign key to user table';


--
-- Name: COLUMN permissions.domain_id; Type: COMMENT; Schema: public; Owner: jbwhite
--

COMMENT ON COLUMN permissions.domain_id IS 'foreign key to domains table';


--
-- Name: COLUMN permissions.role_id; Type: COMMENT; Schema: public; Owner: jbwhite
--

COMMENT ON COLUMN permissions.role_id IS 'foreign key to roles table';


SET default_with_oids = true;

--
-- Name: pids; Type: TABLE; Schema: public; Owner: persis; Tablespace: 
--

CREATE TABLE pids (
    id serial NOT NULL,
    pid character varying(255) DEFAULT mint_noid('/home/noid/NOID/noid.bdb'::character varying),
    proxy_id integer DEFAULT 0 NOT NULL,
    domain_id integer DEFAULT 0 NOT NULL,
    active boolean DEFAULT true NOT NULL,
    name character varying(1023) NOT NULL,
    ext_system_id integer,
    ext_system_key character varying(1023),
    creator_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    last_modified timestamp without time zone DEFAULT now() NOT NULL,
    modified_by integer NOT NULL,
    "type" character varying(25) DEFAULT 'Purl'::character varying
);


--
-- Name: TABLE pids; Type: COMMENT; Schema: public; Owner: persis
--

COMMENT ON TABLE pids IS 'persistent identifiers';


--
-- Name: COLUMN pids.id; Type: COMMENT; Schema: public; Owner: persis
--

COMMENT ON COLUMN pids.id IS 'primary key';


--
-- Name: COLUMN pids.pid; Type: COMMENT; Schema: public; Owner: persis
--

COMMENT ON COLUMN pids.pid IS 'identifier minted by noid';


--
-- Name: COLUMN pids.proxy_id; Type: COMMENT; Schema: public; Owner: persis
--

COMMENT ON COLUMN pids.proxy_id IS 'id of proxy';


--
-- Name: COLUMN pids.domain_id; Type: COMMENT; Schema: public; Owner: persis
--

COMMENT ON COLUMN pids.domain_id IS 'domain of this pid';


--
-- Name: COLUMN pids.active; Type: COMMENT; Schema: public; Owner: persis
--

COMMENT ON COLUMN pids.active IS 'pid is currently enabled';


--
-- Name: COLUMN pids.name; Type: COMMENT; Schema: public; Owner: persis
--

COMMENT ON COLUMN pids.name IS 'human-readable description of this pid';


--
-- Name: COLUMN pids.ext_system_id; Type: COMMENT; Schema: public; Owner: persis
--

COMMENT ON COLUMN pids.ext_system_id IS 'external system associated with this pid';


--
-- Name: COLUMN pids.ext_system_key; Type: COMMENT; Schema: public; Owner: persis
--

COMMENT ON COLUMN pids.ext_system_key IS 'associated key in external system';


--
-- Name: COLUMN pids.creator_id; Type: COMMENT; Schema: public; Owner: persis
--

COMMENT ON COLUMN pids.creator_id IS 'creating user id';


--
-- Name: proxies; Type: TABLE; Schema: public; Owner: croddy; Tablespace: 
--

CREATE TABLE proxies (
    id serial NOT NULL,
    name character varying(127) NOT NULL,
    transform character varying(127) NOT NULL,
    last_modified timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE proxies; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON TABLE proxies IS 'links pids to rules for transforming urls for use with proxy servers';


--
-- Name: COLUMN proxies.id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN proxies.id IS 'primary key';


--
-- Name: COLUMN proxies.name; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN proxies.name IS 'human-readable description of proxy server';


--
-- Name: COLUMN proxies.transform; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN proxies.transform IS 'Regular expression applied to the target url, transforming it to the proxied url';


--
-- Name: COLUMN proxies.last_modified; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN proxies.last_modified IS 'timestamp of last modification';


--
-- Name: roles; Type: TABLE; Schema: public; Owner: croddy; Tablespace: 
--

CREATE TABLE roles (
    id serial NOT NULL,
    "role" character varying(64) NOT NULL,
    last_modified timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE roles; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON TABLE roles IS 'user authorization roles';


--
-- Name: COLUMN roles.id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN roles.id IS 'primary key';


--
-- Name: COLUMN roles."role"; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN roles."role" IS 'human-readable description of role';


--
-- Name: COLUMN roles.last_modified; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN roles.last_modified IS 'timestamp of last modification';


SET default_with_oids = false;

--
-- Name: schema_info; Type: TABLE; Schema: public; Owner: jbwhite; Tablespace: 
--

CREATE TABLE schema_info (
    version integer
);


--
-- Name: targets; Type: TABLE; Schema: public; Owner: persis; Tablespace: 
--

CREATE TABLE targets (
    id serial NOT NULL,
    pid_id integer NOT NULL,
    pid character varying(255) NOT NULL,
    uri character varying(2048) NOT NULL,
    qualify character varying(255)
);


SET default_with_oids = true;

--
-- Name: users; Type: TABLE; Schema: public; Owner: croddy; Tablespace: 
--

CREATE TABLE users (
    id serial NOT NULL,
    username character varying(32) NOT NULL,
    "first" character varying(127),
    "last" character varying(127),
    email character varying(320) NOT NULL,
    last_modified timestamp with time zone DEFAULT now() NOT NULL,
    "password" character varying(150),
    is_superuser boolean DEFAULT false NOT NULL
);


--
-- Name: TABLE users; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON TABLE users IS 'data for users of the application';


--
-- Name: COLUMN users.id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users.id IS 'primary key';


--
-- Name: COLUMN users.username; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users.username IS 'user''s netid/LDAP username/etc.';


--
-- Name: COLUMN users."first"; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users."first" IS 'first name';


--
-- Name: COLUMN users."last"; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users."last" IS 'last name';


--
-- Name: COLUMN users.email; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users.email IS 'email address (RFC2821, RFC2822)';


--
-- Name: COLUMN users.last_modified; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users.last_modified IS 'timestamp of last modification';


--
-- Name: COLUMN users."password"; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users."password" IS 'user password';


--
-- Name: COLUMN users.is_superuser; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users.is_superuser IS 'if true use is added to all Domains';


--
-- Name: archive_targets_pkey; Type: CONSTRAINT; Schema: public; Owner: persis; Tablespace: 
--

ALTER TABLE ONLY archive_targets
    ADD CONSTRAINT archive_targets_pkey PRIMARY KEY (id);


--
-- Name: domains_name_key; Type: CONSTRAINT; Schema: public; Owner: jbwhite; Tablespace: 
--

ALTER TABLE ONLY domains
    ADD CONSTRAINT domains_name_key UNIQUE (name);


--
-- Name: domains_pkey; Type: CONSTRAINT; Schema: public; Owner: jbwhite; Tablespace: 
--

ALTER TABLE ONLY domains
    ADD CONSTRAINT domains_pkey PRIMARY KEY (id);


--
-- Name: ext_systems_name_key; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
--

ALTER TABLE ONLY ext_systems
    ADD CONSTRAINT ext_systems_name_key UNIQUE (name);


--
-- Name: ext_systems_pkey; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
--

ALTER TABLE ONLY ext_systems
    ADD CONSTRAINT ext_systems_pkey PRIMARY KEY (id);


--
-- Name: permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: jbwhite; Tablespace: 
--

ALTER TABLE ONLY permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: pids_pid_key; Type: CONSTRAINT; Schema: public; Owner: persis; Tablespace: 
--

ALTER TABLE ONLY pids
    ADD CONSTRAINT pids_pid_key UNIQUE (pid);


--
-- Name: proxies_name_key; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
--

ALTER TABLE ONLY proxies
    ADD CONSTRAINT proxies_name_key UNIQUE (name);


--
-- Name: proxies_pkey; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
--

ALTER TABLE ONLY proxies
    ADD CONSTRAINT proxies_pkey PRIMARY KEY (id);


--
-- Name: roles_pkey; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
--

ALTER TABLE ONLY roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: targets_pkey; Type: CONSTRAINT; Schema: public; Owner: persis; Tablespace: 
--

ALTER TABLE ONLY targets
    ADD CONSTRAINT targets_pkey PRIMARY KEY (id);


--
-- Name: users_email_key; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users_username_key; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: pid_index; Type: INDEX; Schema: public; Owner: persis; Tablespace: 
--

CREATE INDEX pid_index ON pids USING btree (pid);


--
-- Name: archive_pids; Type: TRIGGER; Schema: public; Owner: persis
--

CREATE TRIGGER archive_pids
    AFTER DELETE OR UPDATE ON pids
    FOR EACH ROW
    EXECUTE PROCEDURE archive_pids();


--
-- Name: archive_targets; Type: TRIGGER; Schema: public; Owner: persis
--

CREATE TRIGGER archive_targets
    AFTER DELETE OR UPDATE ON targets
    FOR EACH ROW
    EXECUTE PROCEDURE archive_targets();


--
-- PostgreSQL database dump complete
--

INSERT INTO schema_info (version) VALUES (3)
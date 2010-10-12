--
-- PostgreSQL database dump
--

SET client_encoding = 'SQL_ASCII';
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


SET search_path = public, pg_catalog;

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

SET default_with_oids = true;

--
-- Name: domains; Type: TABLE; Schema: public; Owner: croddy; Tablespace: 
--

CREATE TABLE domains (
    id serial NOT NULL,
    name character varying(255) NOT NULL,
    last_modified timestamp with time zone DEFAULT now() NOT NULL
);


INSERT INTO domains (id, name, last_modified) VALUES (0, 'default', NOW());

--
-- Name: TABLE domains; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON TABLE domains IS 'domains for grouping pids';


--
-- Name: COLUMN domains.id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN domains.id IS 'primary key';


--
-- Name: COLUMN domains.name; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN domains.name IS 'human-readable description of domain';


--
-- Name: COLUMN domains.last_modified; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN domains.last_modified IS 'timestamp of last modification';


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


--
-- Name: pids; Type: TABLE; Schema: public; Owner: croddy; Tablespace: 
--

CREATE TABLE pids (
    id serial NOT NULL,
    pid character varying(255) DEFAULT mint_noid('/var/local/noid/NOID/noid.bdb'::character varying) NOT NULL,
    target character varying(1023),
    proxy_id integer,
    domain_id integer DEFAULT 0 NOT NULL,
    active boolean DEFAULT true,
    name character varying(1023),
    last_modified timestamp with time zone DEFAULT now() NOT NULL,
    ext_system_id integer,
    ext_system_key character varying(1023)
);



--
-- Name: TABLE pids; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON TABLE pids IS 'persistent identifiers';


--
-- Name: COLUMN pids.id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN pids.id IS 'primary key';


--
-- Name: COLUMN pids.pid; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN pids.pid IS 'identifier minted by noid';


--
-- Name: COLUMN pids.target; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN pids.target IS 'current URL for pid';


--
-- Name: COLUMN pids.proxy_id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN pids.proxy_id IS 'id of proxy';


--
-- Name: COLUMN pids.domain_id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN pids.domain_id IS 'domain of this pid';


--
-- Name: COLUMN pids.active; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN pids.active IS 'pid is currently enabled';


--
-- Name: COLUMN pids.name; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN pids.name IS 'human-readable description of this pid';


--
-- Name: COLUMN pids.last_modified; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN pids.last_modified IS 'timestamp of last modification';


--
-- Name: COLUMN pids.ext_system_id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN pids.ext_system_id IS 'external system associated with this pid';


--
-- Name: COLUMN pids.ext_system_key; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN pids.ext_system_key IS 'associated key in external system';


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

COMMENT ON COLUMN proxies.transform IS 'CHANGEME how the hell are we going to do this?';


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


--
-- Name: users; Type: TABLE; Schema: public; Owner: croddy; Tablespace: 
--

CREATE TABLE users (
    id serial NOT NULL,
    username character varying(32),
    "first" character varying(127) NOT NULL,
    "last" character varying(127) NOT NULL,
    email character varying(320),
    role_id integer,
    proxy_id integer,
    last_modified timestamp with time zone DEFAULT now() NOT NULL
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
-- Name: COLUMN users.role_id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users.role_id IS 'user''s role';


--
-- Name: COLUMN users.proxy_id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users.proxy_id IS 'user''s default proxy';


--
-- Name: COLUMN users.last_modified; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users.last_modified IS 'timestamp of last modification';


--
-- Name: users_domains; Type: TABLE; Schema: public; Owner: croddy; Tablespace: 
--

CREATE TABLE users_domains (
    user_id integer NOT NULL,
    domain_id integer NOT NULL,
    role_id integer NOT NULL,
    last_modified timestamp with time zone DEFAULT now() NOT NULL
);



--
-- Name: TABLE users_domains; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON TABLE users_domains IS 'links users to domains';


--
-- Name: COLUMN users_domains.user_id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users_domains.user_id IS 'link to users table';


--
-- Name: COLUMN users_domains.domain_id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users_domains.domain_id IS 'link to domains table';


--
-- Name: COLUMN users_domains.role_id; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users_domains.role_id IS 'link to roles table';


--
-- Name: COLUMN users_domains.last_modified; Type: COMMENT; Schema: public; Owner: croddy
--

COMMENT ON COLUMN users_domains.last_modified IS 'timestamp of last modification';


--
-- Name: domains_name_key; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
--

ALTER TABLE ONLY domains
    ADD CONSTRAINT domains_name_key UNIQUE (name);


--
-- Name: domains_pkey; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
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
-- Name: pids_pid_key; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
--

ALTER TABLE ONLY pids
    ADD CONSTRAINT pids_pid_key UNIQUE (pid);


--
-- Name: pids_pid_key1; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
--

ALTER TABLE ONLY pids
    ADD CONSTRAINT pids_pid_key1 UNIQUE (pid);


--
-- Name: pids_pkey; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
--

ALTER TABLE ONLY pids
    ADD CONSTRAINT pids_pkey PRIMARY KEY (id);


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
-- Name: users_domains_user_id_key; Type: CONSTRAINT; Schema: public; Owner: croddy; Tablespace: 
--

ALTER TABLE ONLY users_domains
    ADD CONSTRAINT users_domains_user_id_key UNIQUE (user_id, domain_id, role_id);


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
-- Name: pid_index; Type: INDEX; Schema: public; Owner: croddy; Tablespace: 
--

CREATE INDEX pid_index ON pids USING btree (pid);


--
-- Name: target_index; Type: INDEX; Schema: public; Owner: croddy; Tablespace: 
--

CREATE INDEX target_index ON pids USING btree (target);


--
-- Name: pids_domain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: croddy
--

ALTER TABLE ONLY pids
    ADD CONSTRAINT pids_domain_id_fkey FOREIGN KEY (domain_id) REFERENCES domains(id);


--
-- Name: pids_ext_system_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: croddy
--

ALTER TABLE ONLY pids
    ADD CONSTRAINT pids_ext_system_id_fkey FOREIGN KEY (ext_system_id) REFERENCES ext_systems(id);


--
-- Name: pids_proxy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: croddy
--

ALTER TABLE ONLY pids
    ADD CONSTRAINT pids_proxy_id_fkey FOREIGN KEY (proxy_id) REFERENCES proxies(id);


--
-- Name: users_domains_domain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: croddy
--

ALTER TABLE ONLY users_domains
    ADD CONSTRAINT users_domains_domain_id_fkey FOREIGN KEY (domain_id) REFERENCES domains(id);


--
-- Name: users_domains_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: croddy
--

ALTER TABLE ONLY users_domains
    ADD CONSTRAINT users_domains_role_id_fkey FOREIGN KEY (role_id) REFERENCES roles(id);


--
-- Name: users_domains_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: croddy
--

ALTER TABLE ONLY users_domains
    ADD CONSTRAINT users_domains_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);


--
-- Name: users_proxy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: croddy
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_proxy_id_fkey FOREIGN KEY (proxy_id) REFERENCES proxies(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--


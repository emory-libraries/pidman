
  CREATE PROCEDURAL LANGUAGE plperlu;
  CREATE PROCEDURAL LANGUAGE plpgsql;


CREATE FUNCTION mint_noid(character varying) RETURNS character varying
    AS $_X$

use Noid;

$noid = Noid::dbopen($_[0], 0);
$id = Noid::mint($noid, "", "");
Noid::dbclose($noid);

return $id;

$_X$
LANGUAGE plperlu;  
  

  CREATE FUNCTION archive_pids() RETURNS "trigger"
  AS $$	BEGIN
  INSERT INTO archive_pids VALUES (
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

  CREATE FUNCTION archive_targets() RETURNS "trigger"
  AS $$	BEGIN
  INSERT INTO archive_targets VALUES (
  	OLD.id,
  	OLD.pid,
  	OLD.uri,
  	OLD.qualify
  ) ;
  RETURN NULL ;
  END ;
  $$
  LANGUAGE plpgsql STRICT;

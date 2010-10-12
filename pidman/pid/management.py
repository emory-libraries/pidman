import pidman.pid.models
from django.db import connection, transaction
from django.db.models import signals

CREATE_PLPERLU_SQL = '''
CREATE PROCEDURAL LANGUAGE plperlu;
'''

MINT_NOID_SQL = '''
    CREATE FUNCTION mint_noid(character varying) RETURNS character varying
        AS $_X$

    use Noid;

    $noid = Noid::dbopen($_[0], 0);
    $id = Noid::mint($noid, "", "");
    Noid::dbclose($noid);

    return $id;

    $_X$
        LANGUAGE plperlu;
'''

# Try to execute some sql, letting it slide if it fails. I'd really rather
# not ignore errors here, but I haven't found a way to do something exactly
# once per database ever, so we do it here once per invocation and just let
# it slide if it was already done in another invocation.
def execute_or_ok(sql):
    cursor = connection.cursor()
    try:
        cursor.execute(sql)
    except:
        transaction.rollback_unless_managed()
    else:
        transaction.commit_unless_managed()
    finally:
        cursor.close()


# Do this only once per database. There's probably a better way to do this,
# but I haven't found it yet.
PROCEDURE_CREATED = False
def init_noid_db_environment(app, verbosity, **kwargs):
    global PROCEDURE_CREATED
    if not PROCEDURE_CREATED:
        execute_or_ok(CREATE_PLPERLU_SQL)
        execute_or_ok(MINT_NOID_SQL)

signals.post_syncdb.connect(init_noid_db_environment)

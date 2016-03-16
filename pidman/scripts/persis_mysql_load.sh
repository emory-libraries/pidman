
set -x
while getopts ":h:p:u:" option;do
   case $option in
     h) host=$OPTARG;;
     p) password=$OPTARG;;
     u) user=$OPTARG;;
     ?) exit;;
   esac
done

[ -n "$host" ] && host_param="-h $host"
[ -z "$user" ] && quit
[ -z "$password" ] && quit

mysql $host_param -u${user} -p${password} < pidman_schema_mysql.sql
mysql $host_param -u${user} -p${password} persis < auth_group_dump.sql
mysql $host_param -u${user} -p${password} persis < auth_group_permissions_dump.sql
mysql $host_param -u${user} -p${password} persis < auth_permission_dump.sql
mysql $host_param -u${user} -p${password} persis < auth_user_dump.sql
mysql $host_param -u${user} -p${password} persis < auth_user_groups_dump.sql
mysql $host_param -u${user} -p${password} persis < auth_user_user_permissions_dump.sql
mysql $host_param -u${user} -p${password} persis < django_admin_log_dump.sql
mysql $host_param -u${user} -p${password} persis < django_content_type_dump.sql
mysql $host_param -u${user} -p${password} persis < django_session_dump.sql
mysql $host_param -u${user} -p${password} persis < django_site_dump.sql
mysql $host_param -u${user} -p${password} persis < emory_ldap_emoryldapuserprofile_dump.sql
mysql $host_param -u${user} -p${password} persis < pid_domain_dump.sql
mysql $host_param -u${user} -p${password} persis < pid_extsystem_dump.sql
mysql $host_param -u${user} -p${password} persis < pid_pid_dump.sql
mysql $host_param -u${user} -p${password} persis < pid_policy_dump.sql
mysql $host_param -u${user} -p${password} persis < pid_proxy_dump.sql
mysql $host_param -u${user} -p${password} persis < pid_target_dump.sql
mysql $host_param -u${user} -p${password} persis < south_migrationhistory_dump.sql
mysql $host_param -u${user} -p${password} persis < delete_orphans.mysql
mysql $host_param -u${user} -p${password} persis < alter-pid_pid.mysql
mysql $host_param -u${user} -p${password} < constraints.mysql

# MySQL 9.x Auth Plugin Error — Full Transcript

## Error

```
ERROR 2059 (HY000): Authentication plugin 'mysql_native_password' cannot be loaded:
dlopen(/opt/homebrew/Cellar/mysql/9.6.0_2/lib/plugin/mysql_native_password.so, 0x0002):
tried: '/opt/homebrew/Cellar/mysql/9.6.0_2/lib/plugin/mysql_native_password.so' (no such file),
'/System/Volumes/Preboot/Cryptexes/OS/opt/homebrew/Cellar/mysql/9.6.0_2/lib/plugin/mysql_native_password.so' (no such file),
'/opt/homebrew/Cellar/mysql/9.6.0_2/lib/plugin/mysql_native_password.so' (no such file)
```

## Root Cause

MySQL 9.x (Homebrew ARM) removed the `mysql_native_password` authentication plugin entirely. The `.so` file no longer ships. Both the `mysql` CLI and legacy JDBC connectors that default to this plugin will fail.

## Resolution Path

1. Stop MySQL: `brew services stop mysql`
2. Start in `--skip-grant-tables` mode (auth bypassed)
3. Connect and `ALTER USER` to reset auth to the server default (`caching_sha2_password`)
4. Restart MySQL normally
5. Verify: `mysql -u root -p<PASSWORD> -e "SELECT 1"`

## Socket Discovery

When MySQL starts in safe mode with `--user=$(whoami)`, it may create the socket at `/tmp/mysql.sock` instead of the default `/opt/homebrew/var/mysql/mysql.sock`. Check the startup log or use `ls /tmp/mysql.sock` to confirm.

## Compatibility Note

MySQL Connector/J 8.0+ (e.g., 8.0.33) supports `caching_sha2_password` natively — the JDBC connection works without changes. The error only affects the CLI client and very old JDBC drivers.

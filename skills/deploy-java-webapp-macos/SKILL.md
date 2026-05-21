---
name: deploy-java-webapp-macos
description: Deploy Java web applications (Spring Boot, JSP, etc.) on macOS Apple Silicon — JDK, MySQL, Redis, frontend build, and common pitfalls.
category: devops
tags: [java, spring-boot, mysql, redis, macos, deployment, apple-silicon]
---

# Deploy Java Webapp on macOS (Apple Silicon)

Trigger: user asks to deploy a Java/Spring Boot web application on macOS, especially from a Git repo (GitHub, Gitee, etc.) with MySQL + Redis + frontend.

## Pre-flight

```bash
java -version          # >= 17 on Apple Silicon
mvn --version          # or ./mvnw
node -v                # >= 16 for Vue projects
mysql --version
redis-cli ping
```

If any are missing, install via `brew install openjdk@17 maven node mysql redis`.

## Deployment Steps

1. Clone repo, read README, identify backend/frontend directories and config files
2. Read `application.yml` / `application.properties` — note DB name, credentials, ports
3. **MySQL setup** — see [pitfalls](#mysql-auth-issues-on-macos)
4. **Redis setup** — set password in `/opt/homebrew/etc/redis.conf`: uncomment `requirepass` and set the value from app config
5. **Backend build** — update `pom.xml` if needed, then `mvn clean package -DskipTests`
6. **Frontend build** — `npm install` then `npm run dev` (or `npm run build` for prod)
7. Start services and verify

## Pitfalls

### MySQL Auth Issues on macOS

MySQL 9.x (Homebrew ARM) **removed the `mysql_native_password` auth plugin**. Legacy apps or the `mysql` CLI may fail with:

```
ERROR 2059 (HY000): Authentication plugin 'mysql_native_password' cannot be loaded
```

**Fix**: reset root password to use the default `caching_sha2_password`:

```bash
# Stop MySQL
brew services stop mysql

# Start in skip-grant-tables mode
nohup /opt/homebrew/opt/mysql/bin/mysqld --skip-grant-tables --skip-networking \
  --user=$(whoami) --datadir=/opt/homebrew/var/mysql > /tmp/mysql-safe.log 2>&1 &

# Wait 2-3 seconds, then connect (socket may be at /tmp/mysql.sock)
sleep 3
/opt/homebrew/opt/mysql/bin/mysql -u root --socket=/tmp/mysql.sock \
  -e "FLUSH PRIVILEGES; ALTER USER 'root'@'localhost' IDENTIFIED BY 'newpassword';"

# Shutdown safe-mode instance and restart normally
/opt/homebrew/opt/mysql/bin/mysqladmin -u root --socket=/tmp/mysql.sock shutdown
brew services start mysql
```

For the app's JDBC connection: MySQL Connector/J 8.0+ handles `caching_sha2_password` natively — no code changes needed.

### Conflicting MySQL Instances

Old Intel-based MySQL at `/usr/local/mysql/` can conflict with ARM Homebrew MySQL at `/opt/homebrew/`. Check with:

```bash
ps aux | grep mysqld | grep -v grep
```

Stop the old instance: `mysqladmin -u root --socket=/tmp/mysql.sock shutdown` (no sudo needed for mysqladmin).

### JDK Version Mismatch

Legacy projects targeting Java 1.8 won't compile on JDK 17. Update `pom.xml`:

```xml
<java.version>17</java.version>
<!-- and in maven-compiler-plugin: -->
<source>17</source>
<target>17</target>
```

Spring Boot 2.0.x usually works on JDK 17 without further changes.

### Docker Hub Unreachable (China)

If `docker pull` times out, install services natively via `brew install mysql redis` instead of Docker Compose.

### Redis Password

Homebrew Redis config at `/opt/homebrew/etc/redis.conf`. Uncomment and set `requirepass`. After changing, restart: `brew services restart redis`.

## Verification

```bash
# MySQL
mysql -u root -p<PASSWORD> -e "SELECT VERSION(); SHOW DATABASES;"

# Redis
redis-cli -a <PASSWORD> ping

# Backend (after start)
curl http://localhost:9999/

# Frontend (after start)
curl http://localhost:9528/
```

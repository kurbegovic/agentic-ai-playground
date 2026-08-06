import json

SYSTEM_PROMPT = (
    "You are an expert DevOps AI agent. You will receive an error log entry. "
    "Use the search tool to find the exact root cause, troubleshooting steps, and code fixes. "
    "Output your final response in clean Markdown optimized for a GitHub issue. "
    "Include sections: ## Error Summary, ## Root Cause Analysis, and ## Step-by-Step Resolution."
)

# Creating the core storage list for our profile data chunks
error_profiles = []

# --- PROFILE 1 ---
error_profiles.append({
    "error": "StandardInitLinux.go:228: exec user process caused: exec format error",
    "query": "StandardInitLinux.go exec user process caused exec format error docker",
    "results": "Docker build architecture mismatch. Image built on ARM64 (Apple Silicon) trying to run on AMD64 Linux architecture. Fix: Use docker buildx with --platform linux/amd64 flag.",
    "summary": "The container failed to start due to a CPU architecture mismatch (`exec format error`) within the Docker runtime environment.",
    "root_cause": "The Docker image was built on an ARM64-based host machine (such as an Apple Silicon Mac) but was deployed to an AMD64/x86_64 host system. Standard container binaries cannot execute natively across contrasting CPU instruction sets without dynamic emulation architectures.",
    "resolution": "1. **Identify Host Architecture:** Run `uname -m` on the deployment target to confirm the required architecture.\n2. **Rebuild with Buildx:** Modify your CI/CD pipeline or build command to target the host system:\n   ```bash\n   docker buildx build --platform linux/amd64 -t my-app:latest --push .\n   ```\n3. **Redeploy:** Pull the newly multi-platform aligned container image to your target node."
})

# --- PROFILE 2 ---
error_profiles.append({
    "error": "java.lang.OutOfMemoryError: Metaspace",
    "query": "java lang OutOfMemoryError Metaspace troubleshooting spring boot",
    "results": "JVM Metaspace exhaustion. Class loading limit reached. Fix: Increase -XX:MaxMetaspaceSize or investigate class loader leaks.",
    "summary": "The Java Virtual Machine (JVM) crashed unexpectedly after exhausting its allocated Metaspace memory segment.",
    "root_cause": "Metaspace stores class definitions and metadata. This error occurs when the number of dynamically loaded classes exceeds the allocated memory block. It is typically triggered by large applications or dynamic proxy generation frameworks.",
    "resolution": "1. **Adjust JVM Flags:** Increase the native memory ceiling by appending or modifying execution arguments in your startup profile:\n   ```bash\n   -XX:MaxMetaspaceSize=512m\n   ```\n2. **Analyze Classloaders:** Profile the heap using tools like Eclipse MAT to pinpoint potential leaks if memory spikes consistently persist.\n3. **Restart the Service:** Perform a clean application node bounce to release dynamic space allocations."
})

# --- PROFILE 3 ---
error_profiles.append({
    "error": "AWS::S3::Errors::AccessDenied: Access Denied",
    "query": "AWS S3 Errors AccessDenied Access Denied iam policy s3 bucket",
    "results": "S3 Access Denied. Missing s3:GetObject or s3:PutObject in IAM Policy, or Bucket Policy blocks public/cross-account access.",
    "summary": "The application service was denied write/read operational requests directed toward the designated Amazon S3 bucket storage system.",
    "root_cause": "The IAM Role attached to the application cluster does not possess explicit permission mappings for actions like `s3:PutObject` or `s3:GetObject`. Alternatively, an explicit 'Deny' rule exists within the Amazon S3 Bucket Policy or AWS Organizations Service Control Policies (SCPs).",
    "resolution": "1. **Review IAM Statement:** Inspect the policy attached to the active worker node role and ensure permissions are configured:\n   ```json\n   {\n     \"Effect\": \"Allow\",\n     \"Action\": [\"s3:GetObject\", \"s3:PutObject\"],\n     \"Resource\": \"arn:aws:s3:::my-bucket-name/*\"\n   }\n   ```\n2. **Audit Bucket Block Settings:** Ensure that 'Block Public Access' configurations or explicit Bucket Policies are not conflicting with cross-account access requests.\n3. **Verify Local Environment:** Refresh application credentials to guarantee the correct access keys are in use."
})

# --- PROFILE 4 ---
error_profiles.append({
    "error": "Nginx: [emerg] open() \"/etc/nginx/nginx.conf\" failed (13: Permission denied)",
    "query": "nginx emerg open nginx conf failed 13 Permission denied",
    "results": "Nginx lacks permission to read its configuration file. Caused by incorrect file ownership, restricted chmod permissions, or SELinux policies blocking access.",
    "summary": "The Nginx daemon failed to boot because it could not open its core configuration layout file due to OS-level permission restrictions.",
    "root_cause": "The configuration file or its parent directories are owned by a different user group (e.g., `root`) and lack read permissions for the lower-privilege `nginx` worker account. This barrier can also be actively triggered by SELinux security module enforcement contexts.",
    "resolution": "1. **Fix File Ownership:** Reassign appropriate reading ownership contexts to the server paths:\n   ```bash\n   sudo chown -R root:nginx /etc/nginx\n   sudo chmod 640 /etc/nginx/nginx.conf\n   ```\n2. **Check Security Modules:** If using RedHat/CentOS systems, ensure SELinux permits reading by setting explicit contexts:\n   ```bash\n   sudo restorecon -v /etc/nginx/nginx.conf\n   ```\n3. **Validate and Boot:** Test config syntax using `sudo nginx -t` before re-triggering engine initialization."
})

# --- PROFILE 5 ---
error_profiles.append({
    "error": "psycopg2.OperationalError: FATAL: remaining connection slots are reserved for non-replication superuser connections",
    "query": "psycopg2 OperationalError FATAL remaining connection slots are reserved postgresql",
    "results": "PostgreSQL max_connections limit hit. Application is leaking connections or needs connection pooling like PgBouncer.",
    "summary": "The database adapter could not establish a session because PostgreSQL has exhausted its maximum concurrent connection capacity.",
    "root_cause": "The application or backend background workers are failing to properly close database sessions upon completing query operations. Once active pool allocations breach the `max_connections` configuration baseline, Postgres rejects all subsequent incoming non-superuser handshakes.",
    "resolution": "1. **Implement Connection Pooling:** Deploy an intermediate proxy layer like PgBouncer to efficiently reuse active system sockets.\n2. **Scale DB Limits:** Safely elevate operational baselines temporarily inside `/var/lib/pgsql/data/postgresql.conf`:\n   ```ini\n   max_connections = 250\n   ```\n3. **Audit Active Pools:** Run `SELECT * FROM pg_stat_activity;` to locate unclosed abandoned client instances and terminate them."
})

# --- PROFILE 6 ---
error_profiles.append({
    "error": "Error: ENOSPC: no space left on device, watch",
    "query": "Error ENOSPC no space left on device watch system max_user_watches",
    "results": "Linux inotify watch limit reached. Node runtime cannot monitor file changes. Fix: Increase fs.inotify.max_user_watches.",
    "summary": "The Node.js file watcher framework crashed with an unexpected `ENOSPC` file system error on the host instance OS layer.",
    "root_cause": "This error does not typically stem from physical storage drive constraints. Rather, the application's recursive directory watching requirements have broken past the maximum system setting for concurrent `inotify` user watch allocations.",
    "resolution": "1. **Increase Dynamic System Watch Limits:** Elevate kernel watch parameter values within `/etc/sysctl.conf`:\n   ```ini\n   fs.inotify.max_user_watches=524288\n   ```\n2. **Apply Active Kernel Changes:** Reload active sysctl instructions immediately without resetting the container host:\n   ```bash\n   sudo sysctl -p\n   ```\n3. **Relaunch Process:** Restart the workspace tracking task routine to restore standard runtime capabilities."
})

# --- PROFILE 7 ---
error_profiles.append({
    "error": "fatal: [web_server]: FAILED! => {\"changed\": false, \"msg\": \"Failed to lock apt for exclusive operation\"}",
    "query": "ansible FAILED Failed to lock apt for exclusive operation dpkg lock",
    "results": "Another process is running apt-get or automatic updates are locking /var/lib/dpkg/lock. Fix: Wait for automatic updates or kill the process.",
    "summary": "The Ansible provisioning playbook failed on a Debian/Ubuntu node because the system configuration deployment lock was already engaged.",
    "root_cause": "A background operating system utility routine (like an automated security unattended-upgrades cycle) is actively managing packages, holding the exclusive `/var/lib/dpkg/lock-frontend` socket file hostage.",
    "resolution": "1. **Gracefully Await Releases:** Allow background automated security patches to finalize execution steps safely.\n2. **Identify Contending Processes:** Pinpoint background system updates holding active locks if hung indefinitely:\n   ```bash\n   sudo lsof /var/lib/dpkg/lock-frontend\n   ```\n3. **Terminate Locked Actions:** Force release paths only if verified safe to bypass corrupted loops:\n   ```bash\n   sudo kill -9 <PID>\n   sudo dpkg --configure -a\n   ```"
})
# --- PROFILE 8 ---
error_profiles.append({
    "error": "CrashLoopBackOff: Back-off restarting failed container",
    "query": "kubernetes crashloopbackoff debugging steps logs",
    "results": "Kubernetes pod is crashing immediately on start. Run kubectl logs and kubectl describe pod to find application panic/error.",
    "summary": "A Kubernetes pod entered a persistent `CrashLoopBackOff` state, repeatedly failing immediately after initialization loops.",
    "root_cause": "The main process inside the container returned a non-zero termination code. Common catalysts include incorrect configuration files, missing environment variables, failing network health-check dependencies, or binary file runtime panics.",
    "resolution": "1. **Inspect Application Output logs:** Extensively extract stdout logs to uncover inner service stack traces:\n   ```bash\n   kubectl logs <pod-name> --previous\n   ```\n2. **Examine Cluster Events:** Review standard configuration properties and recent lifecycle transitions:\n   ```bash\n   kubectl describe pod <pod-name>\n   ```\n3. **Fix Variables:** Remediate missing file pointers or variables discovered inside the trace, and re-trigger deployment."
})

# --- PROFILE 9 ---
error_profiles.append({
    "error": "Error: Redis connection to 127.0.0.1:6379 failed - connect ECONNREFUSED",
    "query": "Redis connection failed connect ECONNREFUSED 127.0.0.1 6379 troubleshooting",
    "results": "Redis server not running, bound to wrong interface, or port blocked by firewall. Fix: check systemctl status redis, update redis.conf bind address.",
    "summary": "The application layer failed to establish a communication socket with the local Redis caching layer server.",
    "root_cause": "No active process is listening on local port `6379`. This occurs if the Redis engine crashed, failed to start on boot, or is explicitly bound to a network interface configuration that does not encompass `127.0.0.1`.",
    "resolution": "1. **Verify Daemon State:** Evaluate daemon run metrics via native linux monitoring facilities:\n   ```bash\n   sudo systemctl status redis-server\n   ```\n2. **Start Service Engine:** Fire up the caching engine if found sitting dormant:\n   ```bash\n   sudo systemctl start redis-server\n   ```\n3. **Inspect Active Bindings:** Audit `/etc/redis/redis.conf` to check that the service accepts local loopback traffic: `bind 127.0.0.1`."
})

# --- PROFILE 10 ---
error_profiles.append({
    "error": "curl: (35) error:14094438:SSL routines:ssl3_read_bytes:tlsv1 alert internal error",
    "query": "curl 35 error 14094438 SSL routines ssl3_read_bytes tlsv1 alert internal error",
    "results": "SSL/TLS handshake failure. Target server cipher mismatch, domain name mismatch, or unsupported SNI mapping.",
    "summary": "The client networking interface aborted operations during an encrypted SSL/TLS secure communication handshake phase.",
    "root_cause": "The requesting client engine cannot align on a shared cryptographic cipher or protocol version with the hosting endpoint. This can also indicate an invalid Server Name Indication (SNI) or missing upstream certificates.",
    "resolution": "1. **Isolate Cryptographic Formats:** Run verbose networking execution scans to witness raw cryptographic configuration negotiations:\n   ```bash\n   curl -v https://example.com\n   ```\n2. **Test Explicit Targets:** Validate server capabilities using remote analysis packages:\n   ```bash\n   openssl s_client -connect example.com:443 -tls1_2\n   ```\n3. **Upgrade Security Modules:** Patch underlying outdated systems to inherit contemporary cipher combinations (`sudo apt update && sudo apt install openssl`)."
})

# --- PROFILE 11 ---
error_profiles.append({
    "error": "Error: Dynamic Linker: Shared object \"libcrypto.so.1.1\" not found",
    "query": "Shared object libcrypto so 1 1 not found dynamic linker error linux",
    "results": "Missing dependency libssl/libcrypto 1.1. Upstream package removed it or app needs symbolic link/LD_LIBRARY_PATH updated.",
    "summary": "The application executable was terminated abruptly because a critical shared library dependency (`libcrypto.so.1.1`) was completely missing.",
    "root_cause": "The dynamic runtime linker on the Linux distribution cannot locate the file version pathing requested by the binary. This happens frequently on newer operating systems where outdated OpenSSL 1.1 environments were fully replaced with newer OpenSSL 3.0 frameworks.",
    "resolution": "1. **Locate Present Library Paths:** Search if alternative system instances exist:\n   ```bash\n   find /usr/lib -name \"libcrypto.so*\"\n   ```\n2. **Expose Library Environment Targets:** Inject paths dynamically using environment directives:\n   ```bash\n   export LD_LIBRARY_PATH=/usr/local/lib:\$LD_LIBRARY_PATH\n   ```\n3. **Install Target Legacy Binaries:** Fetch legacy fallback compatibility packages or build the requested OpenSSL dependency from source archives directly."
})

# --- PROFILE 12 ---
error_profiles.append({
    "error": "gke-cluster-1 Error creating load balancer (will retry): failed to ensure load balancer for service: Quota 'INUSE_ADDRESSES' exceeded",
    "query": "gke Error creating load balancer Quota INUSE_ADDRESSES exceeded gcp",
    "results": "GCP project ran out of static IP addresses or forwarding rules. Request quota increase or delete unused external IP allocations.",
    "summary": "Google Kubernetes Engine (GKE) failed to provision an external Ingress Load Balancer due to GCP resource account caps.",
    "root_cause": "The targeted Google Cloud Platform project allocation parameters have breached their limit for `INUSE_ADDRESSES`. No additional external networking IP components can be created without exceeding project thresholds.",
    "resolution": "1. **Locate Stranded IPs:** Clean up orphaned external addresses via CLI commands:\n   ```bash\n   gcloud compute addresses list --filter=\"status=RESERVED AND purpose=EXTERNAL\"\n   ```\n2. **Purge Abandoned Artifacts:** Release confirmed dead configurations:\n   ```bash\n   gcloud compute addresses delete <ip-name> --region=<my-region>\n   ```\n3. **Submit Extension Form:** Request an immediate standard limit expansion from the GCP console IAM Quotas center."
})

# --- PROFILE 13 ---
error_profiles.append({
    "error": "terraform error: ResourceInUseException: Replica clusters must be deleted before the primary cluster can be deleted",
    "query": "terraform ResourceInUseException Replica clusters must be deleted primary rds aws",
    "results": "AWS RDS deletion ordering issue. Terraform is attempting to drop the primary instance before secondary replicas are fully destroyed. Fix: Add depends_on or check deletion order.",
    "summary": "Terraform provisioning tasks failed during infrastructure teardown phases because an upstream dependency constraint was triggered on an AWS database resource.",
    "root_cause": "Terraform attempted to remove a primary Amazon RDS instance while attached read-replica instances were still online. AWS API policies enforce complete replica removal before allowing access to clean up a primary node tier.",
    "resolution": "1. **Adjust Module Dependencies:** Force strict logical provisioning structures using structural constraints within your `.tf` scripts:\n   ```hcl\n   resource \"aws_db_instance\" \"replica\" {\n     depends_on = [aws_db_instance.primary]\n   }\n   ```\n2. **Manually Target Takedowns:** Instruct target execution boundaries to tear down sub-components first:\n   ```bash\n   terraform destroy -target=aws_db_instance.replica\n   ```\n3. **Execute Global Destroy:** Once isolated dependencies are stripped, invoke general teardown scripts safely: `terraform destroy`."
})

# --- PROFILE 14 ---
error_profiles.append({
    "error": "Error response from daemon: cgroups: cgroup mountpoint does not exist: unknown",
    "query": "docker cgroups cgroup mountpoint does not exist unknown wsl2 ubuntu",
    "results": "WSL2 environment missing unified cgroup v2 mounts after updating Docker Desktop. Fix: Add systemd support or run update command.",
    "summary": "The Docker service engine could not execute or orchestrate local container configurations because Linux cgroups configuration profiles are missing.",
    "root_cause": "This error occurs often in WSL2 (Windows Subsystem for Linux) environments following engine platform upgrades. The internal Linux virtual container shell expects standard control group (cgroups v2) mounts that are not instantiated at kernel boot.",
    "resolution": "1. **Enable Systemd Features:** Add explicit system tracking parameters within the `/etc/wsl.conf` layout path:\n   ```ini\n   [boot]\n   systemd=true\n   ```\n2. **Reboot Virtual Layer:** Shut down the active subsystem environment using an administrative host PowerShell console shell:\n   ```powershell\n   wsl --shutdown\n   ```\n3. **Boot Application Container:** Reload your Linux bash shell terminal configuration and launch Docker cleanly."
})
# --- PROFILE 15 ---
error_profiles.append({
    "error": "npm ERR! cb() never called! This is an error with npm itself",
    "query": "npm ERR cb never called npm cache clean force troubleshooting",
    "results": "NPM package resolution pipeline hung or corrupted file handles in local node cache directory. Fix: npm cache clean --force or delete node_modules.",
    "summary": "The NPM package pipeline installer aborted abruptly with a generic runtime fallback validation trace (`cb() never called`).",
    "root_cause": "This issue is commonly caused by locally corrupted network cache folders, interrupted package generation routines, or background file system locking actions preventing updates to lockfile states.",
    "resolution": "1. **Wipe Deployment Caches:** Forcefully clear out local download registry cache configurations:\n   ```bash\n   npm cache clean --force\n   ```\n2. **Purge Corrupted Assets:** Trash old local workspace artifact records:\n   ```bash\n   rm -rf node_modules package-lock.json\n   ```\n3. **Execute Clean Installs:** Trigger a fresh workspace dependency assembly sequence: `npm install`."
})

# --- PROFILE 16 ---
error_profiles.append({
    "error": "Error: Host '10.244.3.12' is not allowed to connect to this MySQL server",
    "query": "Error Host is not allowed to connect to this MySQL server grant privileges",
    "results": "MySQL user account restriction. The user is allowed to connect from localhost but not from the Kubernetes pod IP range. Fix: GRANT ALL PRIVILEGES ON *.* TO user@'%'",
    "summary": "The MySQL database engine rejected an incoming application server request due to network client privilege host mismatches.",
    "root_cause": "The SQL identity target account is strictly locked down to accept queries originating exclusively from defined targets (e.g., `db-user@localhost`). The requesting client IP (such as a Kubernetes pod network subnet) lacks authorization rules.",
    "resolution": "1. **Access Core Terminal:** Log directly into the database engine with an administrative profile: `mysql -u root -p`.\n2. **Grant Broad Network Access:** Expand account verification restrictions to authorize connection routing patterns:\n   ```sql\n   GRANT ALL PRIVILEGES ON my_database.* TO 'db_user'@'10.244.%' IDENTIFIED BY 'password';\n   FLUSH PRIVILEGES;\n   ```\n3. **Validate Server Bindings:** Ensure that your `/etc/mysql/my.cnf` configuration accepts remote network connections: `bind-address = 0.0.0.0`."
})

# --- PROFILE 17 ---
error_profiles.append({
    "error": "Helm upgrade failed: rpc error: code = ResourceExhausted desc = grpc: received message larger than max",
    "query": "helm rpc error code ResourceExhausted desc grpc received message larger than max",
    "results": "Helm chart release history configmap object is too large for Kubernetes etcd backend store limits. Fix: Clean up old helm releases or change backend to secrets.",
    "summary": "Helm configuration processes failed because the structural deployment footprint exceeded maximum gRPC system communication thresholds.",
    "root_cause": "By default, Helm archives previous deployment revisions inside local cluster ConfigMaps or Secrets. If application metadata accumulation loops grow excessively large over hundreds of build cycles, backend storage queries will trigger standard gRPC payload constraints.",
    "resolution": "1. **Prune Release Tracking Logs:** Purge historic data logs to shrink environment footprints:\n   ```bash\n   helm history <release-name>\n   ```\n2. **Enforce Storage Reductions:** Apply a hard cap on historic deployment logs in future deployment cycles:\n   ```bash\n   helm upgrade --install <release-name> <chart> --history-max 10\n   ```\n3. **Manually Clear Config Data:** Locate old ConfigMaps using standard dashboard filters and safely drop stale deployment metadata objects."
})

# --- PROFILE 18 ---
error_profiles.append({
    "error": "Jenkins Error: Severe: Hostname verification failed for cloud instance deployment target",
    "query": "Jenkins Severe Hostname verification failed ssl target endpoint",
    "results": "Jenkins deployment agent TLS check failed because remote server certificate CN/SAN does not match IP/DNS used in configuration.",
    "summary": "The Jenkins automation orchestrator aborted connection attempts to a cloud runner node due to TLS hostname validation errors.",
    "root_cause": "The public or internal host path used in the job configuration does not match the names listed in the Common Name (CN) or Subject Alternative Name (SAN) fields of the remote server's SSL certificate.",
    "resolution": "1. **Verify Certificate Names:** Inspect remote endpoint certificates using standard inspection tools:\n   ```bash\n   openssl x509 -in remote_server.crt -text -noout | grep SAN\n   ```\n2. **Update Jenkins Pipeline Addresses:** Correct connection endpoints inside your deployment configs to match the authorized certificate string exactly.\n3. **Inject Local Domain Mappings:** If working behind development subnets, map test pathways cleanly via local `/etc/hosts` resolution configs."
})

# --- PROFILE 19 ---
error_profiles.append({
    "error": "ElasticsearchException[OpenSearch exception [type=circuit_breaking_exception, reason=[parent] Data too large, data for [<http_request>] ESRecoverableException]",
    "query": "opensearch circuit_breaking_exception Data too large heap memory",
    "results": "Elasticsearch/OpenSearch circuit breaker tripped. JVM Heap utilization is above 95 percent threshold. Fix: Increase indices memory or scale JVM heap.",
    "summary": "The search and indexing node tripped its internal safety circuit breaker, immediately blocking inbound indexing operations.",
    "root_cause": "The engine's total dynamic data memory requirements have breached allocated JVM Heap thresholds (typically 95%). To prevent out-of-memory kernel panics, OpenSearch proactively rejects heavy incoming traffic queries.",
    "resolution": "1. **Scale Memory Parameters:** Double the runtime heap allocation inside `/etc/opensearch/jvm.options` (never exceed 50% of raw physical host RAM):\n   ```ini\n   -Xms4g\n   -Xmx4g\n   ```\n2. **Flush Memory Indices:** Force clear out processing caches via structural API endpoints:\n   ```bash\n   curl -XPOST 'localhost:9200/_cache/clear'\n   ```\n3. **Optimize Index Lifecycles:** Delete old indices or implement strict aging policies to reduce total memory footprints."
})

# --- PROFILE 20 ---
error_profiles.append({
    "error": "Error: Prometheus target scraping failed: context deadline exceeded",
    "query": "prometheus target scraping failed context deadline exceeded timeout",
    "results": "Prometheus scraping timeout. The metrics endpoint takes longer to respond than the configured scrape_timeout value. Fix: Profile application metrics endpoint or increase timeout.",
    "summary": "Prometheus timed out while attempting to scrape metrics data from a monitored application target endpoint.",
    "root_cause": "The application target metrics page (`/metrics`) takes longer to calculate and respond than the duration specified by the Prometheus `scrape_timeout` configuration (defaulting to 10s). This is caused by metric accumulation bloat or application performance bottlenecks.",
    "resolution": "1. **Profile Endpoint Behavior:** Manually time metrics page execution responses directly from the application container infrastructure:\n   ```bash\n   curl -o /dev/null -s -w 'Total time: %{time_total}s\n' http://localhost:8080/metrics\n   ```\n2. **Adjust Monitoring Timeout Settings:** Extend scraping allowances inside your global `/etc/prometheus/prometheus.yml` profile:\n   ```yaml\n   scrape_configs:\n     - job_name: 'my-app'\n       scrape_interval: 15s\n       scrape_timeout: 12s\n   ```\n3. **Optimize Custom Metrics:** Reduce the cardinality of application counters to minimize text payload compilation times."
})


# ==========================================
# CORE COMPILATION RUNTIME LOOP
# ==========================================
dataset_rows = []

for item in error_profiles:
    row = {
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"Received error log: '{item['error']}'"
            },
            {
                "role": "assistant",
                "content": f"Action: Search tool required. Query: '{item['query']}'"
            },
            {
                "role": "user",
                "content": f"Search tool execution results: {item['results']}"
            },
            {
                "role": "assistant",
                "content": (
                    f"## Error Summary\n{item['summary']}\n\n"
                    f"## Root Cause Analysis\n{item['root_cause']}\n\n"
                    f"## Step-by-Step Resolution\n{item['resolution']}"
                )
            }
        ]
    }
    dataset_rows.append(row)

# Save the unified dataset lines to your target jsonl file
output_filename = "devops_agent_finetune.jsonl"
with open(output_filename, "w", encoding="utf-8") as f:
    for row in dataset_rows:
        f.write(json.dumps(row) + "\n")

print(f"SUCCESS: Compiled {len(dataset_rows)} compliant SFT schema rows inside '{output_filename}'.")

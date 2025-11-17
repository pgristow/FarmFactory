# FarmFactory Database Performance Tuning

**Sprint 3 - DO-203: TimescaleDB Performance Tuning**

This directory contains PostgreSQL and TimescaleDB configuration optimized for time-series data workloads.

## Table of Contents

- [Overview](#overview)
- [Configuration Files](#configuration-files)
- [Performance Settings](#performance-settings)
- [Performance Tuning Rationale](#performance-tuning-rationale)
- [Compression Strategy](#compression-strategy)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting Guide](#troubleshooting-guide)
- [Performance Targets](#performance-targets)

---

## Overview

FarmFactory uses PostgreSQL with TimescaleDB extension for managing time-series agricultural data. This configuration is optimized for:

- **Workload**: High-volume time-series inserts and range queries
- **Hardware**: 4GB RAM server with SSD storage
- **Data Pattern**: Mixed read/write operations with batch imports
- **Use Cases**: Real-time dashboards, historical analysis, data import processing

---

## Configuration Files

### postgresql.conf

Main PostgreSQL configuration file with optimized settings for time-series workloads.

**Location**: `/home/user/FarmFactory/infrastructure/database/postgresql.conf`

**Applied via**: Docker Compose automatically mounts and applies this configuration on container startup.

### tune-timescaledb.sql

Script to configure TimescaleDB-specific features: chunk intervals, compression policies, and statistics collection.

**Location**: `/home/user/FarmFactory/scripts/tune-timescaledb.sql`

**Usage**:
```bash
make db-tune
```

### performance-monitoring.sql

Comprehensive monitoring queries for performance validation and troubleshooting.

**Location**: `/home/user/FarmFactory/scripts/performance-monitoring.sql`

**Usage**:
```bash
make db-performance
```

---

## Performance Settings

### Memory Configuration

| Parameter | Value | Description | Rationale |
|-----------|-------|-------------|-----------|
| `shared_buffers` | 1GB | PostgreSQL shared memory cache | 25% of 4GB RAM - balances cache size with OS memory needs |
| `effective_cache_size` | 3GB | Total memory available for caching | 75% of 4GB RAM - tells planner how much memory is available |
| `work_mem` | 32MB | Memory per sort/hash operation | Conservative to support concurrent queries without OOM |
| `maintenance_work_mem` | 256MB | Memory for maintenance operations | Sized for VACUUM, CREATE INDEX on time-series data |

**Why these values?**
- 4GB RAM system requires conservative memory allocation
- Time-series workloads benefit from larger buffer cache for recent data
- Multiple concurrent connections need headroom for work_mem operations
- Maintenance operations on chunked data need sufficient memory

### TimescaleDB Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `timescaledb.max_background_workers` | 8 | Background workers for chunk operations |
| `max_worker_processes` | 16 | Total worker processes (must be ≥ parallel + background) |
| `max_parallel_workers_per_gather` | 4 | Parallel workers per query |
| `max_parallel_workers` | 8 | Total parallel workers |

**Why these values?**
- 8 background workers handle compression, retention policies, and chunk management
- Parallel query execution speeds up large time-range scans
- 16 total workers accommodate both parallel queries and background jobs

### WAL (Write-Ahead Log) Settings

| Parameter | Value | Description |
|-----------|-------|-------------|
| `wal_buffers` | 16MB | WAL buffer size |
| `checkpoint_completion_target` | 0.9 | Spread checkpoints over 90% of interval |
| `checkpoint_timeout` | 15min | Time between automatic checkpoints |
| `max_wal_size` | 2GB | Maximum WAL size before checkpoint |
| `min_wal_size` | 1GB | Minimum WAL size to keep |

**Why these values?**
- Larger WAL buffers reduce I/O overhead for high-volume inserts
- Spread checkpoints prevent I/O spikes that impact query performance
- Larger max_wal_size accommodates batch CSV imports without forcing checkpoints

### Query Optimizer Settings

| Parameter | Value | Description |
|-----------|-------|-------------|
| `random_page_cost` | 1.1 | Cost estimate for random page access |
| `seq_page_cost` | 1.0 | Cost estimate for sequential page access |
| `effective_io_concurrency` | 200 | Concurrent I/O operations (SSD) |
| `default_statistics_target` | 100 | Statistics detail level |

**Why these values?**
- Low `random_page_cost` (1.1) reflects SSD random access performance
- High `effective_io_concurrency` (200) optimizes for SSD parallel I/O
- Default statistics target balances ANALYZE time with query plan quality

### Autovacuum Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `autovacuum` | on | Enable automatic vacuum |
| `autovacuum_max_workers` | 3 | Maximum concurrent vacuum workers |
| `autovacuum_naptime` | 60s | Time between autovacuum runs |
| `autovacuum_vacuum_scale_factor` | 0.05 | Vacuum after 5% of rows change |
| `autovacuum_analyze_scale_factor` | 0.02 | Analyze after 2% of rows change |

**Why these values?**
- Aggressive autovacuum (5% threshold) prevents bloat in high-update tables
- Frequent ANALYZE (2% threshold) keeps statistics fresh for query planner
- 60s naptime ensures regular maintenance without excessive overhead
- 3 workers balance maintenance workload with query performance

### Logging Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `log_min_duration_statement` | 1000ms | Log queries slower than 1 second |
| `log_checkpoints` | on | Log checkpoint activity |
| `log_connections` | on | Log connection attempts |
| `log_disconnections` | on | Log disconnections |
| `log_lock_waits` | on | Log lock wait events |

**Why these values?**
- 1-second threshold captures slow queries without flooding logs
- Connection logging helps identify connection pool issues
- Lock wait logging reveals contention problems
- Checkpoint logging tracks I/O patterns

### Connection Settings

| Parameter | Value | Description |
|-----------|-------|-------------|
| `max_connections` | 100 | Maximum client connections |
| `superuser_reserved_connections` | 3 | Connections reserved for superuser |

**Why these values?**
- 100 connections support application pool (50), Celery workers (20), monitoring (10), headroom (20)
- Each connection consumes `work_mem`, so balance with memory limits

---

## Performance Tuning Rationale

### Why TimescaleDB?

TimescaleDB extends PostgreSQL with time-series optimizations:

1. **Automatic Partitioning**: Data split into time-based chunks
2. **Chunk-wise Operations**: Queries only scan relevant time ranges
3. **Compression**: Old data compressed transparently
4. **Continuous Aggregates**: Pre-computed rollups for fast dashboards
5. **Retention Policies**: Automatic old data removal

### Chunk Interval Strategy

Chunk intervals optimized per table based on query patterns:

| Table | Chunk Interval | Rationale |
|-------|---------------|-----------|
| `irrigation_events` | 7 days | Daily/weekly queries common |
| `environmental_readings` | 7 days | Hourly data, daily aggregation queries |
| `nutrient_applications` | 14 days | Weekly queries, less frequent updates |
| `water_quality` | 30 days | Monthly queries, infrequent measurements |

**Guidelines**:
- Chunk size ≈ common query time range
- Smaller chunks = faster recent data queries, more overhead
- Larger chunks = faster historical scans, slower recent queries
- Target: 100MB - 1GB per chunk for optimal performance

### Compression Strategy

**Goals**:
- Reduce storage costs for historical data
- Maintain query performance on old data
- Keep recent data uncompressed for fast writes

**Implementation**:
- **Compression Method**: Segmentby `plot_id`, Orderby `time DESC`
- **Compression Threshold**: 30 days for most tables, 60 days for water_quality
- **Expected Ratio**: 50-90% storage reduction

**How it works**:
1. Recent data (<30 days): Uncompressed, fast inserts/updates
2. Old data (>30 days): Automatically compressed by background job
3. Queries: Transparent decompression, faster scans due to reduced I/O
4. Compressed chunks: Read-only, prevent updates to old data

---

## Compression Strategy

### Compression Configuration

#### Irrigation Events
```sql
ALTER TABLE irrigation_events SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'plot_id',
  timescaledb.compress_orderby = 'time DESC'
);
SELECT add_compression_policy('irrigation_events', INTERVAL '30 days');
```

**Rationale**:
- Segment by `plot_id`: Groups data for same plot together (better compression)
- Order by `time DESC`: Optimizes for recent-first queries
- 30-day threshold: Balances write performance with storage savings

#### Environmental Readings
```sql
ALTER TABLE environmental_readings SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'plot_id',
  timescaledb.compress_orderby = 'time DESC'
);
SELECT add_compression_policy('environmental_readings', INTERVAL '30 days');
```

**Rationale**: Same as irrigation_events - high-frequency data benefits from aggressive compression

#### Nutrient Applications
```sql
ALTER TABLE nutrient_applications SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'plot_id',
  timescaledb.compress_orderby = 'time DESC'
);
SELECT add_compression_policy('nutrient_applications', INTERVAL '30 days');
```

**Rationale**: Weekly data pattern, 30-day threshold ensures 4+ weeks of uncompressed data

#### Water Quality
```sql
ALTER TABLE water_quality SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'plot_id',
  timescaledb.compress_orderby = 'time DESC'
);
SELECT add_compression_policy('water_quality', INTERVAL '60 days');
```

**Rationale**:
- Infrequent measurements (monthly/quarterly)
- 60-day threshold keeps ~2 months uncompressed
- Lower update frequency tolerates longer compression delay

### Compression Benefits

| Benefit | Impact |
|---------|--------|
| **Storage Reduction** | 50-90% savings on historical data |
| **Faster Queries** | Less I/O for large time-range scans |
| **Lower Costs** | Reduced storage and I/O costs in cloud deployments |
| **Automatic Management** | Background jobs handle compression transparently |

### Compression Trade-offs

| Trade-off | Mitigation |
|-----------|------------|
| **Compressed chunks are read-only** | Keep recent data (30 days) uncompressed |
| **Compression CPU overhead** | Background jobs run during low-activity periods |
| **Query decompression cost** | Offset by reduced I/O (typically net performance gain) |

---

## Monitoring and Maintenance

### Quick Health Check

```bash
make db-summary
```

Shows at-a-glance metrics:
- Database size
- Active connections
- Cache hit ratio (target: >95%)
- Total hypertables and chunks
- Compression status

### Comprehensive Performance Report

```bash
make db-performance
```

Generates full report including:
1. Hypertable chunk statistics
2. Compression effectiveness
3. Slow query analysis
4. Index usage
5. Table statistics
6. Cache hit ratios
7. Connection status
8. Autovacuum activity
9. TimescaleDB background jobs
10. Performance summary

### Monitoring Commands

| Command | Purpose |
|---------|---------|
| `make db-stats` | Table sizes and access patterns |
| `make db-cache` | Cache hit ratio (should be >95%) |
| `make db-chunks` | Chunk distribution and sizing |
| `make db-compression` | Compression savings and ratios |
| `make db-connections` | Active connections and pool status |
| `make db-bloat` | Table bloat indicators |
| `make db-index-usage` | Index effectiveness and unused indexes |

### Maintenance Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `make db-tune` | Apply TimescaleDB tuning | After schema changes, initial setup |
| `make db-vacuum` | Manual VACUUM ANALYZE | After large deletes, before major queries |
| `make db-reindex` | Rebuild all indexes | After bloat detected, index corruption |

### Monitoring Best Practices

**Daily**:
- Check `make db-summary` for health overview
- Monitor slow query log for queries >1s

**Weekly**:
- Run `make db-performance` for detailed analysis
- Review compression statistics
- Check autovacuum activity

**Monthly**:
- Analyze storage trends
- Review and optimize slow queries
- Validate compression policies effectiveness

**After Deployments**:
- Run `make db-tune` if schema changed
- Monitor query performance for regressions
- Check for new slow queries

---

## Troubleshooting Guide

### Problem: Slow Queries

**Symptoms**:
- Queries taking >200ms for 30-day ranges
- Dashboard loading slowly
- High CPU usage

**Diagnosis**:
```bash
make db-performance  # Check Section 3: Slow Query Analysis
```

**Solutions**:
1. **Missing Indexes**: Check index usage, add indexes for frequent WHERE/JOIN columns
2. **Poor Statistics**: Run `make db-vacuum` to update statistics
3. **Inefficient Chunk Intervals**: Adjust chunk intervals in `tune-timescaledb.sql`
4. **Large Result Sets**: Implement pagination or continuous aggregates

### Problem: Low Cache Hit Ratio

**Symptoms**:
- Cache hit ratio <95%
- High disk I/O
- Slow query performance

**Diagnosis**:
```bash
make db-cache  # Check cache hit ratio
```

**Solutions**:
1. **Insufficient Memory**:
   - Increase `shared_buffers` in `postgresql.conf`
   - Add more RAM to server
   - Reduce `max_connections` to free memory

2. **Large Working Set**:
   - Data size exceeds available memory
   - Implement data retention policies
   - Archive old data to cheaper storage

3. **Cold Cache**:
   - Restart recently occurred
   - Run common queries to warm cache
   - Monitor over time, not just snapshot

### Problem: Table Bloat

**Symptoms**:
- Tables much larger than expected
- High dead tuple percentage
- Slow sequential scans

**Diagnosis**:
```bash
make db-bloat  # Check bloat statistics
```

**Solutions**:
1. **Autovacuum Not Keeping Up**:
   ```bash
   make db-vacuum  # Manual vacuum
   ```
   - Increase `autovacuum_max_workers` in postgresql.conf
   - Decrease `autovacuum_naptime` for more frequent runs

2. **Long-Running Transactions**:
   - Check `make db-connections` for stuck transactions
   - Kill long-running queries blocking vacuum

3. **Heavy Update Workload**:
   - More aggressive autovacuum settings
   - Consider VACUUM FULL during maintenance window (requires table lock)

### Problem: Compression Not Working

**Symptoms**:
- Storage not decreasing
- Compression ratio 0% or low
- Old data still uncompressed

**Diagnosis**:
```bash
make db-compression  # Check compression status
```

**Solutions**:
1. **Policies Not Applied**:
   ```bash
   make db-tune  # Re-apply compression policies
   ```

2. **Background Jobs Not Running**:
   - Check TimescaleDB job status in performance report
   - Verify `timescaledb.max_background_workers` > 0
   - Check PostgreSQL logs for errors

3. **Data Too Recent**:
   - Compression only applies to data older than threshold (30/60 days)
   - Wait for data to age
   - Adjust threshold in `tune-timescaledb.sql` if needed

### Problem: Connection Pool Exhaustion

**Symptoms**:
- "too many connections" errors
- Application timeouts
- Idle connections accumulating

**Diagnosis**:
```bash
make db-connections  # Check connection status
```

**Solutions**:
1. **Connection Leaks**:
   - Review application code for unclosed connections
   - Check connection pool settings in application

2. **Pool Size Too Large**:
   - Reduce application connection pool size
   - Use connection pooler (PgBouncer)

3. **Stuck Transactions**:
   - Identify long-running idle transactions
   - Kill stuck connections:
     ```sql
     SELECT pg_terminate_backend(pid) FROM pg_stat_activity
     WHERE state = 'idle in transaction' AND state_change < NOW() - INTERVAL '10 minutes';
     ```

### Problem: High Disk Usage

**Symptoms**:
- Disk space running low
- Rapid growth
- WAL files accumulating

**Diagnosis**:
```bash
make db-stats  # Check table sizes
make db-compression  # Check compression effectiveness
```

**Solutions**:
1. **Compression Not Applied**:
   - Apply compression policies (see above)
   - Manually compress old chunks

2. **WAL Accumulation**:
   - Check replication lag (if applicable)
   - Verify archive_command working
   - Adjust `max_wal_size` if too small

3. **Index Bloat**:
   ```bash
   make db-reindex  # Rebuild indexes
   ```

4. **Implement Retention**:
   - Add data retention policies to drop old data
   - Archive historical data to cold storage

---

## Performance Targets

### Query Performance

| Query Type | Target Response Time | Measurement |
|------------|---------------------|-------------|
| 30-day range query | <200ms | 95th percentile |
| Single day query | <50ms | 95th percentile |
| Dashboard refresh | <500ms | All widgets loaded |
| Batch import | >1000 rows/sec | Sustained throughput |

**How to measure**:
```bash
make db-performance  # Section 3: Slow Query Analysis
```

### Storage Efficiency

| Metric | Target | Measurement |
|--------|--------|-------------|
| Compression ratio | >50% | For data >30 days old |
| Table bloat | <20% | Dead tuples / live tuples |
| Index bloat | <30% | Fragmentation ratio |

**How to measure**:
```bash
make db-compression  # Compression stats
make db-bloat        # Bloat analysis
```

### System Health

| Metric | Target | Acceptable Range |
|--------|--------|------------------|
| Cache hit ratio | >95% | 90-100% |
| Index hit ratio | >99% | 95-100% |
| Active connections | <50 | 0-80 (max 100) |
| Autovacuum lag | <1 day | 0-3 days |

**How to measure**:
```bash
make db-summary  # Quick overview
make db-cache    # Cache metrics
```

### Resource Utilization

| Resource | Target Usage | Alert Threshold |
|----------|-------------|-----------------|
| RAM | 60-80% | >90% |
| CPU | <50% avg | >80% sustained |
| Disk I/O | <70% | >90% |
| Disk space | <70% | >85% |

**How to measure**:
```bash
make stats  # Docker container stats
docker-compose exec postgres top  # Inside container
```

---

## Performance Validation Checklist

After applying tuning, validate effectiveness:

- [ ] Cache hit ratio >95% (`make db-cache`)
- [ ] Index hit ratio >99% (`make db-cache`)
- [ ] No queries >200ms for 30-day ranges (`make db-performance`)
- [ ] Compression ratio >50% for old data (`make db-compression`)
- [ ] Autovacuum running regularly (`make db-performance` Section 8)
- [ ] No unused indexes consuming space (`make db-index-usage`)
- [ ] Table bloat <20% (`make db-bloat`)
- [ ] Active connections reasonable (<50) (`make db-connections`)
- [ ] Chunk sizes consistent (100MB-1GB) (`make db-chunks`)
- [ ] Background jobs running successfully (`make db-performance` Section 9)

---

## Additional Resources

### Documentation

- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/14/performance-tips.html)
- [TimescaleDB Best Practices](https://docs.timescale.com/timescaledb/latest/how-to-guides/compression/)
- [PostgreSQL Autovacuum](https://www.postgresql.org/docs/14/routine-vacuuming.html)

### Tools

- **pgAdmin**: GUI for PostgreSQL administration
- **pg_top**: Real-time PostgreSQL activity monitor
- **pg_stat_statements**: Query performance statistics
- **TimescaleDB Toolkit**: Advanced analytics functions

### Related Files

- `docker-compose.yml`: Database service configuration
- `backend/alembic/versions/`: Database migrations
- `scripts/init-db.sql`: Database initialization
- `infrastructure/database/init-performance.sql`: Performance monitoring views

---

## Support and Contact

For issues or questions:

1. Check this README troubleshooting section
2. Review PostgreSQL logs: `make logs-db`
3. Run performance diagnostics: `make db-performance`
4. Consult Sprint 3 documentation in `/docs`

**Maintained by**: DevOps Team
**Sprint**: Sprint 3 - Core Data Management
**Task**: DO-203 - TimescaleDB Performance Tuning
**Last Updated**: 2025-11-17

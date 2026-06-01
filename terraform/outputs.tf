output "web_url" {
  description = "Live URL of the Roommate Finder API"
  value       = render_web_service.web.url
}

output "db_connection_string" {
  description = "PostgreSQL internal connection string"
  value       = render_postgres.db.connection_info.internal_connection_string
  sensitive   = true
}

output "redis_connection_string" {
  description = "Redis internal connection string"
  value       = render_redis.cache.connection_info.internal_connection_string
  sensitive   = true
}

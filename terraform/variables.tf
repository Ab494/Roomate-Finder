variable "render_api_key" {
  description = "Render API key — from dashboard.render.com/u/settings"
  type        = string
  sensitive   = true
}

variable "render_owner_id" {
  description = "Render owner/team ID"
  type        = string
}

variable "secret_key" {
  description = "Django SECRET_KEY"
  type        = string
  sensitive   = true
}

variable "cloudinary_cloud_name" {
  type    = string
  default = ""
}

variable "cloudinary_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "cloudinary_api_secret" {
  type      = string
  sensitive = true
  default   = ""
}

variable "at_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "email_host_user" {
  type    = string
  default = ""
}

variable "email_host_password" {
  type      = string
  sensitive = true
  default   = ""
}

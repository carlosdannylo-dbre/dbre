resource "mongodbatlas_api_key" "this" {
  org_id      = var.org_id
  description = var.description
  role_names  = var.org_roles
}
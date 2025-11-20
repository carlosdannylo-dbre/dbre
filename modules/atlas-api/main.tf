resource "mongodbatlas_org_api_key" "this" {
  org_id      = var.org_id
  description = var.description
  roles       = var.org_roles
}

resource "mongodbatlas_project_api_key" "project_bindings" {
  for_each   = toset(var.project_ids)
  project_id = each.value
  api_key_id = mongodbatlas_org_api_key.this.id
  role_names = var.project_roles
}

resource "mongodbatlas_access_list_api_key" "access_list" {
  for_each = var.access_list

  api_key_id = mongodbatlas_org_api_key.this.id
  cidr_block = each.value.cidr_block
  ip_address = each.value.ip_address
  comment    = each.value.comment
  org_id     = var.org_id
}

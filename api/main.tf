resource "mongodbatlas_api_key" "this" {
  org_id      = var.org_id
  description = var.description
  role_names  = var.org_roles

}

resource "mongodbatlas_access_list_api_key" "this" {
  org_id     = var.org_id
  cidr_block = var.cidr_block
  api_key_id = mongodbatlas_api_key.this.api_key_id
}
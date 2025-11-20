variable "org_id" {
    description = "ID da organização do MongoDB Atlas onde a API Key será criada"
    type        = string    
}
variable "description" {
    description = "Descrição da API Key que será criada"
    type        = string
}
variable "org_roles" {
    description = "Lista de roles de organização atribuídas à API Key" 
    type = list(string)   
}   
variable "cidr_block" {
    description = "Bloco CIDR para a lista de acesso da API Key"
    type        = string
}
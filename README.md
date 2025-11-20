# MongoDB Atlas Terraform building blocks

Este repositório traz três módulos do Terraform para provisionamento completo do MongoDB Atlas seguindo boas práticas de organização, segurança e automação:

- **modules/atlas-api**: cria chaves de API em nível de organização e concede acesso a projetos específicos com listas de controle de origem.
- **modules/atlas-cluster**: entrega um cluster avançado (replica set) em AWS ou Azure com endpoints privados aprovados.
- **modules/atlas-project**: cria projetos e mapeia grupos de federation (SSO) para funções específicas dentro de cada projeto.

Um exemplo de uso combinando os módulos está disponível em [`examples/complete`](examples/complete), incluindo variáveis para apontar regiões, endpoints privados e grupos federados.

## Requisitos
- Terraform >= 1.5
- Provider `mongodb/mongodbatlas` >= 1.17
- Chaves de API do Atlas exportadas como variáveis de ambiente ou via `terraform.tfvars` (`atlas_public_key`, `atlas_private_key`).

## Como começar
1. Copie `examples/complete` e preencha suas variáveis (organização, regiões, endpoints privados de AWS/Azure, ID do federation settings e grupos SSO).
2. Execute `terraform init` para baixar o provider.
3. Use `terraform plan`/`apply` para validar e criar os recursos.

Cada módulo foi desenhado para ser composable e protegido contra deleções acidentais (termination protection habilitada por padrão nos clusters).

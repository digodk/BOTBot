# BOTBot
O **Broadcast On Topics Bot**

BOTBot é um bot do Telegram projetado para facilitar a inscrição em tópicos e a publicação anônima de mensagens. Os usuários podem se inscrever ou cancelar a inscrição em tópicos, e postar mensagens de texto nesses tópicos.

Para falar com o bot é só ir no [@dotstopsbot](https://t.me/dotstopsbot)

## Estrutura do Projeto

Este projeto consiste em vários scripts Python que são usados em funções AWS Lambda e arquivos Terraform que são usados para gerenciar os recursos AWS necessários para o bot, além dos arquivos de configuração do GitHub Actions.

Breve visão geral dos principais arquivos:

- `helpers.py`: Contém funções auxiliares para lidar com inscrição, cancelamento de inscrição, transmissão de mensagens e envio de mensagens via Telegram.
- `telegram-handler/lambda_function.py`: A função AWS Lambda que processa eventos recebidos do Telegram. Ela analisa o comando do usuário e realiza a ação apropriada (por exemplo, inscrever-se em um tópico, transmitir uma mensagem).
- `send-message/lambda_function.py`: A função AWS Lambda que lida com o envio de mensagens para a API do Telegram.
- Arquivos Terraform: Usados para gerenciar os recursos de infraestrutura da AWS necessários para o bot.

Nota: O script `helpers.py` interage com AWS DynamoDB e AWS SQS, e esses recursos são configurados usando Terraform.

## Roadmap
1. [x] MVP
    - Inscrição e cancelamento de inscrição em tópicos
    - Publicação de mensagens de texto em tópicos
    - Recebimento de mensagens de texto publicadas
2. [x] IaC
    - [x] Provisão de recursos e deploy de lambdas com Terraform
3. [x] CI/CD (WIP)
    - [x] Deploy automático terraform
4. [ ] Testes Integrados
    - [ ] Desenvolver testes integrados simulando ambiente de nuvem
    - [ ] Automação de testes integrados
5. [ ] Observabilidade
    - [ ] Prometheus
    - [ ] Grafana
6. [ ] Tuning
    - [ ] Melhoria do tempo de resposta
7. [ ] Futuro
    - [ ] Enviar outras mídias (foto, vídeo, áudio, stickers, gifs)
    - [ ] Suporte a markdown do Telegram
    - [ ] Separar em dois bots, um para config e outro para broadcast
    - [ ] Throtling da taxa de respostas para ser compatível com os limites do telegram
    - [ ] i18n

## Utilização

Para um usuário interagir com o bot, ele deve usar os seguintes comandos:

- `/sub <nome_do_topico>`: Inscrever-se em um tópico. Os tópicos podem ter caracteres alfanuméricos e o símbolo "_".
- `/unsub <nome_do_topico>`: Cancelar inscrição em um tópico.
- `.<nome_do_topico> sua mensagem de texto`: Enviar uma mensagem para um tópico. Todos os inscritos receberão uma cópia da mensagem.
- `/about`: Para saber mais sobre o BOTBot

## Como implantar o projeto

Se você quiser implementar seu próprio BOTBot, siga os passos abaixo.

### Pré requisitos

Você obrigatoriamente vai precisar do seguinte:

1. Criar um bot no telegram. Você pode criar o bot falando com o [@botfather](https://t.me/BotFather)
Guarde o token secreto do bot, ele é importante!

2. Uma conta na [AWS](https://aws.amazon.com/)

3. O par de chaves de acesso para um usuário IAM de sua conta AWS. [Tutorial](https://docs.aws.amazon.com/pt_br/powershell/latest/userguide/pstools-appendix-sign-up.html)

3. Uma conta Terraform Cloud, uma organização e workspace nessa conta. [Tutorial](https://developer.hashicorp.com/terraform/tutorials/cloud-get-started/cloud-sign-up)

4. Um token para o workspace que você criou. [Tutorial](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/api-tokens)

5. Incluir seu token de bot e as chaves de acesso AWS como uma variáveis secretas de ambiente no seu workspace Terraform Cloud. [Tutorial](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/variables)

6. Um clone desse projeto. Use o comando `git clone https://github.com/digodk/BOTBot.git` no terminal da sua máquina ou faça um fork via GitHub.

A partir daqui existem dois caminhos:

### Deploy a partir do GitHub Actions

Esse é o método padrão utilizado por esse projeto.

1. **Configure as variáveis de ambiente no GitHub Secrets**: Para que o GitHub Actions funcione corretamente, você precisará definir algumas variáveis de ambiente no GitHub Secrets. Estas variáveis são:

- TF_API_TOKEN: Seu token de acesso ao Terraform Cloud

- TF_CLOUD_ORG: O nome da sua organização no Terraform Cloud

- TF_WORKSPACE: O nome do seu workspace no Terrform Cloud

[Documentação do GitHub Secrets](https://docs.github.com/pt/actions/reference/encrypted-secrets)

2. **Acione o workflow de implantação**: Com as variáveis de ambiente corretamente configuradas, acione o workflow de implantação do GitHub Actions. Isso pode ser feito fazendo um push para o branch principal ou manualmente na interface do GitHub. Se precisar de ajuda, consulte a [documentação do GitHub Actions](https://docs.github.com/pt/actions/managing-workflow-runs/manually-running-a-workflow).

3. **Configure o webhook do telegram**: É necessário indicar ao telegram que os updates do bot devem ser enviados ao endpoint de sua API. Para isso, siga a [documentação do telegram](https://core.telegram.org/bots/api#setwebhook). 

O endpoint pode ser encontrado no dashboard do [API Gateway](https://us-east-1.console.aws.amazon.com/apigateway). Você quer algo assim:

https://aaaaaaaaa.execute-api.us-east-1.amazonaws.com/dev

no entanto, você deve incluir um /update ao final do endpoint, esse é o ponto de integração configurado para a lambda. Então o endpoint a ser enviado para o Telegram no `setWebhook` é:

https://aaaaaaaaa.execute-api.us-east-1.amazonaws.com/dev/update


### Deploy a partir da máquina local usando Terraform Cloud

1. **Instale o Terraform**: Para fazer o deploy a partir da sua máquina local, você precisará ter o Terraform instalado. [Documentação de instalação do Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)

2. **Configure suas variáveis de ambiente**: Assim como no deploy com o GitHub Actions, você precisará configurar suas variáveis de ambiente. 

Nesse caso, você precisa [fazer login no Terraform Cloud a partir do CLI](https://developer.hashicorp.com/terraform/tutorials/0-13/cloud-login).

Além disso, você deve preencher sua org e workspace no arquivo `backend.tf`:

```
terraform {
  backend "remote" {
    organization = "sua-org-aqui"

    workspaces {
      name = "seu-workspace"
    }
  }
}
```

3. **Inicie o Terraform e execute o comando de implantação**: Garanta que o Terraform está corretamente configurado com o backend cloud com o comando `terraform init` a partir da raiz do projeto. 

Em seguida, execute `terraform plan` e verifique se as modificações a serem feitas estão de acordo com a expectativa. 

Depois disso, execute `terraform apply` para fazer o deploy do projeto. Você vai precisar confirmar a operação.

Uma vez concluído, não esqueça de configurar o webhook do telegram com o endpoint da sua API, conforme explicado na seção anterior.

### Como testar

Vá no bot e mande um /start, bot deve responder com uma mensagem se apresentando e descrevendo seus comandos. A primeira execução do bot demorar um pouco a responder devido ao cold start das lambdas. Have fun!

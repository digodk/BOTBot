# BOTBot
O **Broadcast On Topics Bot**

BOTBot é um bot do Telegram projetado para facilitar a inscrição em tópicos e a publicação anônima de mensagens. Os usuários podem se inscrever ou cancelar a inscrição em tópicos, e postar mensagens de texto nesses tópicos.

## Estrutura do Projeto

Este projeto consiste em vários scripts Python e arquivos Terraform que são usados para gerenciar os recursos AWS necessários para o bot.

Aqui está uma breve visão geral dos principais arquivos:

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
3. [ ] CI/CD (WIP)
    - [ ] Deploy automático
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

## Utilização

Para um usuário interagir com o bot, ele deve usar os seguintes comandos:

- `/sub <nome_do_topico>`: Inscrever-se em um tópico. Os tópicos podem ter caracteres alfanuméricos e o símbolo "_".
- `/unsub <nome_do_topico>`: Cancelar inscrição em um tópico.
- `.<nome_do_topico> sua mensagem de texto`: Enviar uma mensagem para um tópico. Todos os inscritos receberão uma cópia da mensagem.

## Começando

Para usar o bot, siga as instruções abaixo:

1. Clone o repositório para sua máquina local.
2. Configure um bot no telegram usando o @botfather
3. Configure os recursos AWS necessários usando Terraform, seguindo as instruções nos arquivos Terraform.
4. Comece a interagir com o bot no Telegram enviando o comando `/start`.
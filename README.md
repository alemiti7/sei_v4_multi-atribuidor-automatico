# SEI versão 4 Multi-atribuidor automático de processos

Este projeto automatiza a atribuição de processos no Sistema Eletrônico de Informações (SEI) versão 4.

Elaborado no Ambiente de teste público SEI versão 4.0.11, https://sei.orgao1.tramita.processoeletronico.gov.br/

Dados de acesso fornecidos pelo site <a href="https://www.gov.br/gestao/pt-br/assuntos/processo-eletronico-nacional/noticias/2023/tramita-gov-br-lanca-quatro-novos-ambientes-de-teste-para-orgaos-e-entidades-em-processo-de-implantacao-da-plataforma">Tramita GOV.BR - Ministério da Gestão e da Inovação de Serviços Públicos</a>

[![image](https://github.com/user-attachments/assets/32956465-4fa2-4d8a-adfe-9ac78f92e60c)]([https://www.youtube.com/watch?v=vc488Y)

<iframe width="560" height="315" src="https://www.youtube.com/embed/SWjCjvc488Y?si=iVPDj96pSTDqdhpD" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## 🚀 Funcionalidades

- Login automatizado no sistema SEI
- Atribuição automática de processos para múltiplos usuários e múltiplos TIPOS de processo
- Contagem e relatório de atribuições realizadas
- Pode ser executado pelo cron (Linux, Macos) ou Agendador de Tarefas (Windows) em pré-determinados horários.

## 📋 Pré-requisitos

- Python 3.6 ou superior
- Google Chrome
- ChromeDriver compatível com sua versão do Chrome

### Bibliotecas Python necessárias
```bash
selenium
```

## 🔧 Instalação

1. Clone o repositório
```bash
git clone https://github.com/alemiti7/sei_v4_multi-atribuidor-automatico.git
```

2. Instale as dependências
```bash
pip install -r requirements.txt
```

3. Exemplo de teste, configure o arquivo de credenciais, criando o arquivo .env

```
SEI_URL=https://sei.orgao1.tramita.processoeletronico.gov.br/
USERNAME=usuariobasicoseiorgao101
PASSWORD=usuariobasicoseiorgao101
```

## ⚙️ Configuração

O script pode ser configurado através do dicionário `termos_acoes.json` no arquivo principal. Exemplo:

```python
{
    "Contabilidade: Manuais": {
        "atributo": "usuariobasicoseiorgao101 - Usuário Básico SEI Ambiente 1 Número 01"
    },
    "Gestão da Informação: Recebimento de Processo Externo": {
        "atributo": "usuariobasicoseiorgao101 - Usuário Básico SEI Ambiente 1 Número 01"
    },
    "Acompanhamento Legislativo: Câmara dos Deputados": {
        "atributo": "usuariobasicoseiorgao101 - Usuário Básico SEI Ambiente 1 Número 01"
    },
    "Finanças: Normatização Interna": {
        "atributo": "usuariobasicoseiorgao101 - Usuário Básico SEI Ambiente 1 Número 01"
    }
}
```

## 🖥️ Uso

Execute o script principal:
```bash
python main.py
```

## 🔍 Funcionamento

O script realiza as seguintes operações:

1. Faz login no sistema SEI
2. Navega até a página de controle de processos
3. Para cada página:
   - Procura por processos que correspondam aos termos configurados
   - Verifica se os processos já possuem atribuição
   - Seleciona processos sem atribuição
   - Realiza a atribuição conforme configurado
4. Navega para a próxima página até atingir a última
5. Gera um relatório das atribuições realizadas
6. Realiza logout do sistema

## ⚠️ Elementos JavaScript

O script interage com elementos JavaScript em alguns pontos específicos:

1. Navegação entre páginas:
```html
<a id="lnkInfraProximaPaginaInferior" href="javascript:void(0);" onclick="infraAcaoPaginar('+',0,'Infra', null);">
```

2. Interações via Selenium:
```python
driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
driver.execute_script("arguments[0].click();", checkbox)
```

## 🛠️ Tecnologias Utilizadas

- Python
- Selenium WebDriver
- JavaScript (para interações com a página)
- Chrome WebDriver

## 📊 Logs e Monitoramento

O script fornece logs detalhados de suas operações gerando o arquivo script_log.log, contendo:
- Progresso da navegação entre páginas
- Contagem de atribuições por termo
- Erros e exceções encontrados
- Resumo final das operações realizadas e data atual

  ![image](https://github.com/user-attachments/assets/eeb53645-219a-4df0-8d85-6f8c2cc9b47e)


## 🤝 Contribuindo

Formas de contribuir:
- Sugerir melhorias e reportar bugs
- Compartilhar scripts de automação do SEI!

## ✒️ Autores

* ** Alexandre Mitsuru ** - *Desenvolvimento Inicial* - https://github.com/alemiti7
* ** Luis Carlos ** -*Colaborador técnico* - https://github.com/luismelloleite

📞 Contato
Alexandre
📧 alemiti@gmail.com
⌨️ com ❤️ por [@alemiti7]([https://github.com/alemiti7]) 😊

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE.md](LICENSE.md) para detalhes.

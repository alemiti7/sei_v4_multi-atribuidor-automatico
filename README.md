# SEI Multi-atribuidor Automático (Playwright)

Este projeto automatiza a atribuição de processos no Sistema Eletrônico de Informações (SEI). 

A versão **v2.0** marca uma evolução tecnológica significativa, substituindo o antigo motor Selenium pelo **Playwright**, garantindo execuções assíncronas, mais rápidas e com maior estabilidade.

## 🚀 Modernizações

Em comparação com a versão original baseada em Selenium, as principais melhorias são:

* **Motor Playwright (Async):** Migração para engine assíncrona, com maior velocidade e menor consumo de memória.
* **Resiliência:** Lógica de retentativas automática para superar lentidões e timeouts do SEI.
* **Código Limpo:** Refatoração completa (PEP8/Lint) para maior estabilidade e manutenção.


## 📋 Pré-requisitos

Antes de executar o script, certifique-se de ter instalado:

- Python 3.10 ou superior
- Uma conexão estável com o ambiente do SEI

## 🛠️ Instalação e Dependências

1.  Instale as bibliotecas externas necessárias:
    ```bash
    pip install playwright python-dotenv
    ```

2.  Instale o navegador (Chromium) utilizado pelo Playwright:
    ```bash
    playwright install chromium
    ```

3.  Configure o arquivo `.env` na raiz do projeto com suas credenciais:
    ```env
    SEI_URL=[https://seu-link-do-sei.gov.br](https://seu-link-do-sei.gov.br)
    USERNAME=seu_usuario
    PASSWORD=sua_senha
    ```

## 📊 Estrutura de Operação

O script funciona lendo o arquivo `termos_acoes.json`, onde você define qual termo de busca deve ser atribuído a qual ID de usuário:

```json
{
    "Pessoal: Férias - Solicitação": {
        "atributo": "usuariobasicoseiorgao101"
    },
    "Pessoal: Avaliação de Desempenho Individual": {
        "atributo": "usuariobasicoseiorgao101"
    },
    "Gestão da Informação: Recebimento de Processo Externo": {
        "atributo": "usuario1"
    },
    "Pessoal: Contabilidade: DIRF": {
        "atributo": "ORGAO1"
    },
    "Pessoal: Auxílio Doença": {
        "atributo": "ORGAO1"
    }
}
```

## 🖥️ Uso

Execute o script principal `main.py`:
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

O script fornece logs detalhados de suas operações gerando o arquivo `script_log.log` contendo:
- Progresso da navegação entre páginas
- Contagem de atribuições por termo
- Erros e exceções encontrados

<img width="1418" height="388" alt="image" src="https://github.com/user-attachments/assets/23161d44-ffb8-4358-a8b6-03bc85b66903" />




- Data atual e resumo final das operações realizadas serão exibidas no terminal:

<img width="1043" height="129" alt="image" src="https://github.com/user-attachments/assets/2831246c-4e2e-41c5-83b8-4115bfbf7a0c" />


## 🤝 Contribuindo

Formas de contribuir:
- Sugerir melhorias e reportar bugs
- Compartilhar scripts de automação do SEI!

## ✒️ Autores

* ** Alexandre Mitsuru Nikaitow ** - *Desenvolvimento Inicial* - https://github.com/alemiti7
* ** Luis Carlos ** -*Colaborador técnico* - https://github.com/luismelloleite

📞 Contato
Alexandre
alemiti@gmail.com


## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE.md](LICENSE.md) para detalhes.

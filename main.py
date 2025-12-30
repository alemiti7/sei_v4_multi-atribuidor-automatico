import asyncio
import os
import json
import logging
import re
import datetime
import locale
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Configuração de locale e logs
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except Exception: # Correção E722: Especificado Exception
    pass

class SEILogFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return datetime.datetime.now().strftime('%d/%m/%Y %H:%M')

formatter = SEILogFormatter("%(asctime)s – %(levelname)s – %(message)s")
file_handler = logging.FileHandler("script_log.log", encoding="utf-8")
file_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

class SEIAutomation:
    def __init__(self):
        load_dotenv()
        self.url = os.getenv("SEI_URL")
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")
        self.termos_acoes = self._carregar_termos()
        self.resumo_final = {}

    def _carregar_termos(self):
        try:
            with open("termos_acoes.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Erro ao carregar JSON: {e}")
            return {}

    async def fazer_login(self, page):
        logging.info("Iniciando acesso ao sistema SEI...")
        await page.goto(self.url, wait_until="networkidle")
        await page.fill("#txtUsuario", self.username)
        await page.fill("#pwdSenha", self.password)
        await page.click("#Acessar")
        
        await page.wait_for_selector("#lnkControleProcessos", timeout=20000)
        await page.click("#lnkControleProcessos")
        
        try:
            logging.info("Configurando filtros...")
            detalhado = page.locator("#divFiltro > div:nth-child(1) > a")
            if await detalhado.is_visible():
                await detalhado.click()
            
            ordenacao_seta = page.locator("#tblProcessosDetalhado th:nth-child(6) img").first
            await ordenacao_seta.wait_for(state="visible", timeout=10000)
            await ordenacao_seta.click()
        except Exception: # Correção E722: Especificado Exception
            logging.warning("Não foi possível ordenar a tabela, prosseguindo...")
        
        await page.wait_for_selector("table.infraTable", timeout=15000)

    async def realizar_atribuicao(self, page, id_usuario_json, quantidade):
        max_tentativas = 2
        for tentativa in range(1, max_tentativas + 1):
            try:
                await page.click("img[title='Atribuir Processo'], img[src*='atribuir']", timeout=10000)
                await page.wait_for_selector("#selAtribuicao", state="visible")

                opcoes = await page.locator("#selAtribuicao option").all_inner_texts()
                opcao_correta = next((opt for opt in opcoes if opt.lower().startswith(id_usuario_json.lower())), None)
                
                if opcao_correta:
                    await page.select_option("#selAtribuicao", label=opcao_correta)
                    await page.click("#sbmSalvar")
                    logging.info(f"Sucesso: {quantidade} itens atribuídos para {opcao_correta}")
                    await page.wait_for_selector("table.infraTable")
                    return True
                
                logging.error(f"Usuário '{id_usuario_json}' não encontrado.")
                return False

            except Exception: # Correção F841: Variável 'e' removida pois não era usada
                logging.warning(f"Falha na tentativa {tentativa}. Recarregando...")
                await page.reload()
                await page.wait_for_selector("#lnkControleProcessos")
                await page.click("#lnkControleProcessos")
        return False

    async def processar_pagina_atual(self, page, num_pagina):
        logging.info(f"Analisando Página {num_pagina}")
        await page.wait_for_selector("table.infraTable tbody tr", timeout=10000)
        linhas = page.locator("table.infraTable tbody tr")
        total_linhas = await linhas.count()

        for termo, info in self.termos_acoes.items():
            id_usuario = info["atributo"]
            selecionados_count = 0
            termo_regex = re.compile(re.escape(termo).replace(r'\ ', r'\s*'), re.IGNORECASE)

            for i in range(total_linhas):
                linha = linhas.nth(i)
                if termo_regex.search(await linha.inner_text()):
                    if await linha.locator(".ancoraSigla").count() == 0:
                        checkbox = linha.locator("input[type='checkbox']").first
                        await checkbox.evaluate("node => { node.checked = true; node.dispatchEvent(new Event('click', { bubbles: true })); }")
                        selecionados_count += 1

            if selecionados_count > 0:
                if await self.realizar_atribuicao(page, id_usuario, selecionados_count):
                    self.resumo_final[(termo, id_usuario)] = self.resumo_final.get((termo, id_usuario), 0) + selecionados_count
                    linhas = page.locator("table.infraTable tbody tr")
                    total_linhas = await linhas.count()

    async def executar(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await self.fazer_login(page)
                num_pag = 1
                while True:
                    await self.processar_pagina_atual(page, num_pag)
                    proxima = page.locator("#lnkInfraProximaPaginaInferior").first
                    if await proxima.is_visible():
                        await proxima.click()
                        num_pag += 1
                        await page.wait_for_timeout(2000)
                    else:
                        break
                self.imprimir_resumo()
            except Exception as e:
                logging.error(f"Erro crítico: {e}")
            finally:
                await browser.close()

    def imprimir_resumo(self):
        print("\n" + "="*70)
        print(f"==== {datetime.datetime.now().strftime('%A, %d de %B de %Y, às %H:%M:%S')} ====")
        print("\nRESUMO DAS ATRIBUIÇÕES:")
        for (termo, id_user), qtd in self.resumo_final.items():
            msg = f"- {qtd} processos de '{termo}' atribuído a {id_user}"
            print(msg)
            logging.info(msg)
        print("="*70)

if __name__ == "__main__":
    asyncio.run(SEIAutomation().executar())

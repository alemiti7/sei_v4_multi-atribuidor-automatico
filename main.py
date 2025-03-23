import locale
import json
import datetime
import time
import logging
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from functools import wraps

# Configuração do logging
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')


class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return datetime.datetime.now().strftime('%d/%m/%Y %H:%M')


formatter = CustomFormatter("%(asctime)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("script_log.log")
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])


def retry_operation(max_attempts=3, delay=1):
    """Decorator para retentar operações"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logging.warning(f"Tentativa {attempt + 1} falhou: {str(e)}. Retentando em {delay} segundos...")
                        time.sleep(delay)
                    else:
                        logging.error(f"Todas as {max_attempts} tentativas falharam para {func.__name__}")
                        raise last_exception
        return wrapper
    return decorator


def log_and_print(message):
    """Registra a mensagem no log e opcionalmente imprime no console."""
    logging.info(message)


def configurar_driver():
    """Configura e retorna o driver do Chrome com opções otimizadas."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_script_timeout(20)  # Aumentado para 20 segundos
    driver.set_page_load_timeout(30)  # Timeout de carregamento de página
    return driver


def tratar_alerta(driver):
    """
    Trata alertas pendentes no navegador.
    Retorna True se um alerta foi tratado, False caso contrário.
    """
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        logging.info(f"Alerta tratado: {alert_text}")
        return True
    except:
        return False


@retry_operation(max_attempts=3, delay=2)
def fazer_login(driver, url, username, password):
    """Realiza o login na página com tratamento de erros melhorado."""
    try:
        driver.get(url)
        # Esperar carregamento completo da página
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        # Login com verificações explícitas
        usuario_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "txtUsuario"))
        )
        usuario_input.clear()
        usuario_input.send_keys(username)
        senha_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pwdSenha"))
        )
        senha_input.clear()
        senha_input.send_keys(password)
        botao_login = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "Acessar"))
        )
        botao_login.click()

        # Verificar alerta de erro
        if tratar_alerta(driver):
            raise Exception("Falha no login: Alerta de erro detectado.")

        # Navegar após login bem-sucedido
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#lnkControleProcessos > img"))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#divFiltro > div:nth-child(1) > a"))
        ).click()
        
        # Substituição mais segura do time.sleep
        time.sleep(1.5)  # Mantido time.sleep aqui para garantir estabilidade
        
        logging.info("")
        logging.info(f"===== Logs de {obter_data_atual_formatada()} =====")
        logging.info("Iniciando script SEI...")
        logging.info("Login realizado com sucesso")
    except Exception as e:
        logging.error(f"Erro durante o login: {str(e)}")
        raise


def verificar_linha_sem_atribuicao(linha):
    """Verifica se a linha não tem usuário atribuído com tratamento de erros."""
    try:
        celulas = linha.find_elements(By.TAG_NAME, "td")
        for celula in celulas:
            elementos_ancora = celula.find_elements(By.CLASS_NAME, "ancoraSigla")
            if elementos_ancora:
                return False
        return True
    except Exception as e:
        log_and_print(f"Erro ao verificar atribuição: {str(e)}")
        return False


def verificar_ultima_pagina(driver):
    """Verifica se está na última página com verificação robusta."""
    try:
        elemento = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "lnkInfraProximaPaginaInferior"))
        )
        return False
    except (TimeoutException, NoSuchElementException):
        return True


@retry_operation(max_attempts=2, delay=1)
def processar_pagina_atual(driver, termos_acoes, contadores, contadores_pagina):
    """Processa a página atual com retentativas."""
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.infraTable")))
    
    # Resetar contadores da página
    for atributo in contadores_pagina:
        for termo in contadores_pagina[atributo]:
            contadores_pagina[atributo][termo] = 0
    
    for termo_busca, acao in termos_acoes.items():
        atributo = acao["atributo"]
        logging.info(f"Procurando por: {termo_busca}")
        xpath_termo = f"//td[contains(text(), '{termo_busca}')]"
        celulas_termo = driver.find_elements(By.XPATH, xpath_termo)
        for celula in celulas_termo:
            try:
                linha = celula.find_element(By.XPATH, "./..")
                if not verificar_linha_sem_atribuicao(linha):
                    continue
                try:
                    checkbox_div = linha.find_element(By.CSS_SELECTOR, "td:first-child div.infraCheckboxDiv")
                    checkbox = checkbox_div.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                    
                    # Uso mais conservador do WebDriverWait com fallback para time.sleep
                    try:
                        WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, ".//input[@type='checkbox']"))
                        )
                    except:
                        time.sleep(0.5)  # Fallback para time.sleep
                    
                    driver.execute_script("arguments[0].click();", checkbox)
                    
                    # Espera mais simples com fallback
                    try:
                        WebDriverWait(driver, 2).until(
                            lambda d: checkbox.is_selected()
                        )
                    except:
                        time.sleep(0.5)  # Fallback para time.sleep
                    
                    if checkbox.is_selected():
                        contadores_pagina[atributo][termo_busca] += 1
                    else:
                        log_and_print(f"Checkbox não foi selecionado para: {termo_busca}")
                except Exception as e:
                    log_and_print(f"Erro ao interagir com checkbox: {str(e)}")
                    continue
            except Exception as e:
                log_and_print(f"Erro ao processar linha: {str(e)}")
                continue
        
        if contadores_pagina[atributo][termo_busca] > 0:
            realizar_atribuicao(driver, acao)
            contadores[atributo][termo_busca] += contadores_pagina[atributo][termo_busca]


@retry_operation(max_attempts=2, delay=1)
def realizar_atribuicao(driver, acao):
    """Realiza a atribuição com verificações e retentativas."""
    try:
        logging.info("Iniciando processo de atribuição")
        botao_atributo = WebDriverWait(driver, 10).until(
            # Clicando no icone "Atribuiçao de processos"
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#divComandos > a:nth-child(3) > img"))
        )
        botao_atributo.click()
        
        # Combinação de WebDriverWait com time.sleep para maior robustez
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#selAtribuicao"))
            )
        except:
            time.sleep(0.8)  # Fallback para garantir estabilidade
        
        logging.info("Botão de atribuição clicado")
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#selAtribuicao"))
        )
        dropdown.click()
        
        # Combinação segura com fallback
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#selAtribuicao option"))
            )
        except:
            time.sleep(0.8)  # Fallback para time.sleep
        
        opcao = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'//option[contains(text(), "{acao["atributo"]}")]'))
        )
        opcao.click()
        
        # Abordagem híbrida para garantir transição
        time.sleep(0.8)  # Mantido para garantir estabilidade
        
        logging.info(f"Opção {acao['atributo']} selecionada")
        botao_salvar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#sbmSalvar'))
        )
        botao_salvar.click()
        
        # Combinação de WebDriverWait com time.sleep
        try:
            WebDriverWait(driver, 5).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "table.infraTable"))
            )
        except:
            time.sleep(1.5)  # Fallback para time.sleep
        
    except Exception as e:
        log_and_print(f"Erro ao realizar atribuição: {str(e)}")
        raise


def realizar_atribuicoes(driver, termos_acoes):
    """Realiza as atribuições em todas as páginas com gestão de erros."""
    contadores = {}
    contadores_pagina = {}
    
    # Inicializar contadores por atributo
    for termo, acao in termos_acoes.items():
        atributo = acao["atributo"]
        if atributo not in contadores:
            contadores[atributo] = {}
            contadores_pagina[atributo] = {}
        contadores[atributo][termo] = 0
        contadores_pagina[atributo][termo] = 0
    
    pagina_atual = 1
    while True:
        try:
            logging.info(f"\nProcessando página {pagina_atual}")
            processar_pagina_atual(driver, termos_acoes, contadores, contadores_pagina)
            if verificar_ultima_pagina(driver):
                logging.info("Última página alcançada")
                break
            proximo_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "lnkInfraProximaPaginaInferior"))
            )
            proximo_link.click()
            
            # Abordagem híbrida para maior estabilidade
            try:
                WebDriverWait(driver, 8).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                WebDriverWait(driver, 8).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "table.infraTable"))
                )
            except:
                time.sleep(2.0)  # Fallback para time.sleep
            
            pagina_atual += 1
        except Exception as e:
            log_and_print(f"Erro ao processar página {pagina_atual}: {str(e)}")
            if pagina_atual > 1:
                # Tenta continuar com a próxima página se não estiver na primeira
                continue
            else:
                break
    return contadores


def obter_data_atual_formatada():
    """Retorna a data e hora atual formatada."""
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    agora = datetime.datetime.now()
    return agora.strftime('%A, %d de %B de %Y, às %H:%M:%S')


def fazer_logout(driver):
    """Realiza o logout com tratamento de erros aprimorado."""
    try:
        # Verifica se ainda está logado
        try:
            botao_logout = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#lnkInfraSairSistema > img"))
            )
            botao_logout.click()
            logging.info("Logout realizado com sucesso")
            
            # Combinação mais segura para esperar pelo logout
            try:
                WebDriverWait(driver, 5).until(
                    lambda d: "login" in d.current_url.lower() or "acesso" in d.current_url.lower()
                )
            except:
                time.sleep(1.0)  # Fallback para time.sleep
            
        except TimeoutException:
            logging.warning("Botão de logout não encontrado - usuário possivelmente já deslogado")
    except Exception as e:
        logging.error(f"Erro durante o logout: {str(e)}")
    finally:
        try:
            # Trata qualquer alerta pendente
            try:
                alert = driver.switch_to.alert
                alert.accept()
                logging.info("Alerta fechado durante logout")
            except:
                pass
            driver.quit()
            logging.info("Driver fechado com sucesso")
        except Exception as e:
            logging.error(f"Erro ao fechar o driver: {str(e)}")


def verificar_credenciais(url, username, password):
    """Verifica se as credenciais estão presentes e válidas."""
    if not url or not isinstance(url, str):
        raise ValueError("URL inválida ou não encontrada no arquivo .env")
    if not username or not isinstance(username, str):
        raise ValueError("USERNAME inválido ou não encontrado no arquivo .env")
    if not password or not isinstance(password, str):
        raise ValueError("PASSWORD inválida ou não encontrada no arquivo .env")


def validar_termos_acoes(termos_acoes):
    """Valida o conteúdo do arquivo termos_acoes.json."""
    if not isinstance(termos_acoes, dict) or len(termos_acoes) == 0:
        raise ValueError("Arquivo termos_acoes.json vazio ou mal formatado.")
    for termo, acao in termos_acoes.items():
        if not isinstance(termo, str) or not isinstance(acao, dict):
            raise ValueError(f"Entrada inválida no arquivo termos_acoes.json: {termo}")
        if "atributo" not in acao or not isinstance(acao["atributo"], str):
            raise ValueError(f"Atributo ausente ou inválido para o termo: {termo}")


def main():
    driver = None
    try:
        # Carregar e verificar credenciais
        load_dotenv()
        url = os.getenv("SEI_URL")
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")
        verificar_credenciais(url, username, password)

        # Carregar termos de busca
        try:
            with open("termos_acoes.json", "r", encoding="utf-8") as arquivo:
                termos_acoes = json.load(arquivo)
                validar_termos_acoes(termos_acoes)
        except FileNotFoundError:
            raise FileNotFoundError("Arquivo termos_acoes.json não encontrado.")
        except json.JSONDecodeError:
            raise ValueError("Erro ao decodificar o arquivo termos_acoes.json. Verifique o formato JSON.")

        # Log dos termos carregados
        for termo, valores in termos_acoes.items():
            logging.info(f"Termo: {termo}, Atributo: {valores['atributo']}")

        # Configurar driver e realizar login
        driver = configurar_driver()
        fazer_login(driver, url, username, password)

        # Realizar atribuições
        contadores = realizar_atribuicoes(driver, termos_acoes)

        # Resultados
        print("\n" + "="*50)
        print(obter_data_atual_formatada())
        log_and_print("Script SEI executado com sucesso!")
        print("\nResumo das atribuições realizadas:")
        for atributo, termos in contadores.items():
            print(f"\nAtribuições para o atributo '{atributo}':")
            for termo, contador in termos.items():
                print(f"- {contador} atribuições para '{termo}'")
        print("="*50)
    except Exception as e:
        log_and_print(f"Erro durante a execução: {str(e)}")
        logging.error("Stacktrace completo:", exc_info=True)
    finally:
        if driver:
            fazer_logout(driver)


if __name__ == "__main__":
    main()
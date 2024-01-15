import csv
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("form.html")


@app.route("/consulta_processos", methods=["POST"])
def consulta_processos():
    cpf = request.form.get("cpf")
    start_time = time.time()

    resultados_pesquisa_atual = []

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get(
        "https://pje2g.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam"
    )

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "fPP:dpDec:documentoParte"))
        )
        numerocpf = driver.find_element(By.ID, "fPP:dpDec:documentoParte")
        numerocpf.send_keys(cpf)
        botao_pesquisar = driver.find_element(By.ID, "fPP:searchProcessos")
        botao_pesquisar.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//b[@class="btn-block"]'))
        )
        links_processos = driver.find_elements(By.XPATH, '//b[@class="btn-block"]')

        with open("processos.csv", "a", newline="") as file:
            writer = csv.writer(file)
            for link in links_processos:
                main_window = driver.current_window_handle
                link.click()
                driver.switch_to.window(driver.window_handles[1])

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="j_id135:processoTrfViewView:j_id143"]/div/div[2]',
                        )
                    )
                )
                numero_processo = driver.find_element(
                    By.XPATH,
                    '//*[@id="j_id135:processoTrfViewView:j_id143"]/div/div[2]',
                )
                data_distribuicao = driver.find_element(
                    By.XPATH,
                    '//*[@id="j_id135:processoTrfViewView:j_id155"]/div/div[2]',
                )
                data_pesquisa = time.strftime("%d/%m/%Y - %H:%M:%S")

                writer.writerow(
                    [cpf, numero_processo.text, data_distribuicao.text, data_pesquisa]
                )
                resultados_pesquisa_atual.append(
                    [numero_processo.text, data_distribuicao.text, data_pesquisa]
                )

                driver.close()
                driver.switch_to.window(main_window)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        driver.quit()

    end_time = time.time()
    total_time = end_time - start_time
    formatted_time = "{:.2f} segundos".format(total_time)

    return render_template(
        "resultados.html",
        cpf=cpf,
        quantidade_processos=len(resultados_pesquisa_atual),
        total_time=formatted_time,
        dados=resultados_pesquisa_atual,
    )


if __name__ == "__main__":
    app.run(debug=True)

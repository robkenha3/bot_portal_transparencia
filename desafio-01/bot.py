from playwright.sync_api import sync_playwright
import base64, re

AUXILIO_BRASIL = "Auxílio Brasil"
AUXILIO_EMERGENCIAL = "Auxílio Emergencial"
BENEFICIARIO_BOLSA_FAMILIA = "Beneficiário de Bolsa Família"
NOVO_BOLSA_FAMILIA = "Novo Bolsa Família"
FAVORECIDO_RECURSO = "Favorecido de Recursos do Governo Federal"

def rodar_bot(consultar):
    
    def captcha_freeze():
        try:
            pagina.wait_for_selector("text=Vamos confirmar que você é humano", timeout=3000)
            print("Captcha detectado! Resolva-o agora.")
            input("Aperte ENTER depois de resolver o captcha...")
        except:
            print("Captcha nao apareceu, seguindo fluxo normal.")

        pagina.wait_for_selector("tbody tr td", timeout=3000)

        pagina.wait_for_timeout(1000)

    def converter_base64(titulo):
        
        if titulo == FAVORECIDO_RECURSO:
            elemento = pagina.locator("#lista").filter(visible=True).first
        else:
            elemento = pagina.locator(".dados-detalhados").filter(visible=True).first

        elemento.locator("tbody tr td").first.wait_for(state="visible", timeout=10000)
        pagina.wait_for_timeout(500)
        img_bytes = elemento.screenshot()

        return base64.b64encode(img_bytes).decode()
    
    def erro_padrao(consultar):
        numeros = re.sub(r"\D", "", consultar)

        if numeros.isdigit():
            return {"erro": "Não foi possível retornar os dados no tempo de resposta solicitado"}

        return {"erro": f"Foram encontrados 0 resultados para o termo {consultar}"}


    def gravar_dados(): 
        nome = pagina.locator("strong:has-text('Nome') + span").text_content().strip()
        cpf = pagina.locator("strong:has-text('CPF') + span").text_content().strip()
        localidade = pagina.locator("strong:has-text('Localidade') + span").text_content().strip()

        pagina.locator('.item .header').click()
        pagina.wait_for_timeout(1000)

        dados_finais = []

        cards_tipo1 = pagina.locator(".form-group .br-table").all()
        cards_tipo2 = pagina.locator(".form-group .row").all()

        if len(cards_tipo1) > 0:
            for card_tipo1 in cards_tipo1:
                titulo = card_tipo1.locator(".responsive strong").text_content().strip()
                linhas_card_tipo1 = card_tipo1.locator("tbody tr").all()

                for linha in linhas_card_tipo1:
                    nis = linha.locator("td").nth(1).text_content().strip()
                    valor_total_recebido = linha.locator("td").nth(3).text_content().strip()
                    buttons = linha.locator("td a")

                    buttons.click()
                    pagina.wait_for_load_state("networkidle")
                    
                    captcha_freeze()

                    primeira_tabela = pagina.locator(".dados-detalhados").first
                    tabela = primeira_tabela.locator("tbody tr").all()
                    response = []

                    for linha in tabela:
                        linha_valor = linha.locator("td").all_text_contents()

                        if not linha_valor:
                            continue

                        try:
                            if titulo == AUXILIO_EMERGENCIAL:
                                dados = {
                                    "mes_disponibilizacao": linha_valor[0],
                                    "parcela": linha_valor[1],
                                    "uf": linha_valor[2],
                                    "municipio": linha_valor[3],
                                    "enquadramento": linha_valor[4],
                                    "valor": linha_valor[5],
                                    "observacao": linha_valor[6]
                                }

                            elif titulo == BENEFICIARIO_BOLSA_FAMILIA:
                                dados = {
                                    "mes_folha": linha_valor[0],
                                    "mes_referencia": linha_valor[1],
                                    "uf": linha_valor[2],
                                    "municipio": linha_valor[3],
                                    "quantidade_dependentes": linha_valor[4],
                                    "valor": linha_valor[5]
                                }

                            else:
                                try:
                                    dados = {
                                        "mes_folha": linha_valor[0],
                                        "mes_referencia": linha_valor[1],
                                        "uf": linha_valor[2],
                                        "municipio": linha_valor[3],
                                        "valor_parcela": linha_valor[4]
                                    }
                                except Exception as e:                 
                                    print(f"Dados nao correspondente para {AUXILIO_EMERGENCIAL}, {BENEFICIARIO_BOLSA_FAMILIA}, {NOVO_BOLSA_FAMILIA}, {AUXILIO_BRASIL}")
                            
                            response.append(dados)
                        except Exception as e:
                            print("Erro ao processar linha:", linha_valor)
                            print("Erro:", e)

                    img_64 = converter_base64(titulo)

                    dados_finais.append({
                        "nome": nome,
                        "cpf": cpf,
                        "nis": nis,
                        "location": localidade,
                        "recurso_tipo": titulo,
                        "valor_total_recebido": valor_total_recebido,
                        "detalhes": response,
                        "img_base64": img_64
                    })

                    pagina.go_back()
                    pagina.wait_for_load_state("networkidle")
                    pagina.locator('.item .header').click()
                    pagina.wait_for_timeout(2000)

        if len(cards_tipo2) > 0:
            for card_tipo2 in cards_tipo2:
                titulo = FAVORECIDO_RECURSO
                texto_valor_recebido = card_tipo2.locator("#gastosDiretos").text_content()
                valor_total_recebido = texto_valor_recebido.split(":")[-1].strip()

                button = card_tipo2.locator("a")
                button.click()
                pagina.wait_for_load_state("networkidle")
                
                captcha_freeze()

                tabela = pagina.locator("#lista tbody tr").all()
                response = []

                for linha in tabela:
                    linha_valor = linha.locator("td").all_text_contents()

                    if not linha_valor:
                        continue

                    try:
                        dados = {
                            "data": linha_valor[0],
                            "documento": linha_valor[1].strip(),
                            "localidade_aplicacao_recurso": linha_valor[2],
                            "fase_despesa": linha_valor[3],
                            "especie": linha_valor[4],
                            "favorecido": linha_valor[5],
                            "uf_favorecido": linha_valor[6],
                            "valor": linha_valor[7],
                            "ug": linha_valor[8],
                            "unidade_orcamentaria": linha_valor[9],
                            "orgao": linha_valor[10],
                            "orgao_superior": linha_valor[11],
                            "grupo_despesa": linha_valor[12],
                            "elemento_despesa": linha_valor[13],
                            "modalidade_despesa": linha_valor[14],
                            "plano_orcamentario": linha_valor[15],
                            "nome_autor_emenda": linha_valor[16]
                        }

                        response.append(dados)

                    except Exception as e:
                        print("Erro ao processar linha:", linha_valor)
                        print("Erro:", e)

                img_64 = converter_base64(titulo)

                dados_finais.append({
                    "nome": nome,
                    "cpf": cpf,
                    "nis": "",
                    "location": localidade,
                    "recurso_tipo": titulo,
                    "valor_total_recebido": valor_total_recebido,
                    "detalhes": response,
                    "img_base64": img_64
                })

                pagina.go_back()
                pagina.wait_for_load_state("networkidle")                
                pagina.locator('.item .header').click()
                pagina.wait_for_timeout(2000)

        return dados_finais

    with sync_playwright() as pw:
        consultar_limpo = consultar.replace(".", "").replace("*", "").replace("-", "").upper()
        navegador = pw.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        pagina = navegador.new_page()

        pagina.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)

        pagina.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        try:
            pagina.goto("https://portaldatransparencia.gov.br/pessoa-fisica/busca/lista?pagina=1&tamanhoPagina=10")
            pagina.get_by_role("searchbox", name="Busque por Nome, Nis ou CPF (").fill(consultar_limpo)
            pagina.get_by_role("button", name="Enviar dados do formulário de busca").click()

            pagina.wait_for_timeout(3000) 
            count_resultados = pagina.locator("#resultados a.link-busca-nome").count()

            if count_resultados == 0:
                return erro_padrao(consultar)
                
            links_nome = pagina.locator("#resultados a.link-busca-nome").first

            nome_encontrado = links_nome.text_content().strip().upper()
            cpf_encontrado = int(pagina.locator("#countResultados").text_content())
            nis_encontrado = int(pagina.locator("#countResultados").text_content())

            if not (
                nome_encontrado == consultar_limpo or
                (cpf_encontrado != 0) or
                (nis_encontrado != 0)
            ):
                return erro_padrao(consultar)
            
            links_nome.click()
            pagina.wait_for_load_state("networkidle")

            dados = gravar_dados()
            return dados
    
        finally:
            navegador.close()
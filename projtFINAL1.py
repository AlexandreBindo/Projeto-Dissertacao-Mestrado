# =============================================================
# ALUNO: ALEXANDRE DOS SANTOS BINDO CABRAL
# PROGRAMA 1 – Aplicativo de Extração de Dados Geográficos da Rede Condor
# ==============================================================
# Objetivo:
# Este programa realiza a busca automática das unidades da rede
# Condor localizadas em Curitiba-PR utilizando dados públicos do
# OpenStreetMap por meio da biblioteca OSMnx.
#
# As informações coletadas (nome, endereço, latitude e longitude)
# são organizadas e exportadas para o arquivo "condor_curitiba.csv",
# que será utilizado como entrada pelo próximo programa do projeto,
# responsável pela otimização das rotas.
# ==============================================================
import flet as ft
import osmnx as ox
import pandas as pd


def buscar_condor():

    place = "Curitiba, Paraná, Brasil"

    tags = {
        "shop": "supermarket"
    }

    ox.settings.use_cache = True

    gdf = ox.features_from_place(place, tags)

    condor = gdf[
        gdf["name"].fillna("").str.contains("Condor", case=False)
    ]

    dados = []

    for _, row in condor.iterrows():

        nome = str(row.get("name", "")).strip()

        if row.geometry.geom_type == "Point":
            lat = row.geometry.y
            lon = row.geometry.x
        else:
            centro = row.geometry.centroid
            lat = centro.y
            lon = centro.x

        rua = str(row.get("addr:street", "")).strip()
        numero = str(row.get("addr:housenumber", "")).strip()

        endereco = f"{rua} {numero}".strip()

        dados.append({
            "nome": nome,
            "endereco": endereco,
            "latitude": lat,
            "longitude": lon
        })

    # --------------------------------------------------------
    # Renomeia os mercados cujo nome é apenas "Condor"
    # --------------------------------------------------------

    centro_lat = -25.4284
    centro_lon = -49.2733

    condor_genericos = []

    for loja in dados:

        if loja["nome"].lower() == "condor":

            distancia = (
                (loja["latitude"] - centro_lat) ** 2 +
                (loja["longitude"] - centro_lon) ** 2
            )

            condor_genericos.append((distancia, loja))

    condor_genericos.sort(key=lambda x: x[0])

    for i, (_, loja) in enumerate(condor_genericos, start=1):

        loja["nome"] = f"Condor C{i}"

    # --------------------------------------------------------

    df = pd.DataFrame(dados)

    df.to_csv(
        "condor_curitiba.csv",
        index=False,
        encoding="utf-8-sig"
    )

    return dados


def main(page: ft.Page):
    page.title = "Extrator Supermercados Condor - Curitiba"
    page.window_width = 1200
    page.window_height = 750
    page.scroll = "auto"

    titulo = ft.Text(
        "🛒 Extrator de Supermercados Condor",
        size=30,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_700
    )

    subtitulo = ft.Text(
        "Busca coordenadas no OpenStreetMap e salva em CSV",
        size=16,
        color=ft.Colors.GREY_700
    )

    status = ft.Text(
        "Pronto para buscar!",
        size=16,
        color=ft.Colors.GREY_700
    )

    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("Endereço")),
            ft.DataColumn(ft.Text("Latitude")),
            ft.DataColumn(ft.Text("Longitude")),
        ],
        rows=[]
    )

    def ao_clicar(e):
        status.value = "Buscando dados no OpenStreetMap..."
        page.update()

        try:
            lojas = buscar_condor()

            tabela.rows.clear()

            for loja in lojas:
                tabela.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(loja["nome"]))),
                            ft.DataCell(ft.Text(str(loja["endereco"]))),
                            ft.DataCell(
                                ft.Text(str(round(loja["latitude"], 6)))),
                            ft.DataCell(
                                ft.Text(str(round(loja["longitude"], 6)))),
                        ]
                    )
                )

            status.value = f"CSV criado com sucesso! Total encontrado: {len(lojas)} lojas."

        except Exception as erro:
            status.value = f"Erro: {erro}"

        page.update()

    botao = ft.ElevatedButton(
        "Buscar Supermercados",
        icon=ft.Icons.SEARCH,
        on_click=ao_clicar
    )

    page.add(
        ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [titulo, subtitulo],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    alignment=ft.alignment.center,
                    padding=20
                ),
                ft.Divider(),
                ft.Container(
                    content=ft.Column(
                        [botao, status],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=20,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=10
                ),
                ft.Divider(),
                tabela
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )


ft.app(target=main)

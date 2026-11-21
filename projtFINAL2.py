# =============================================================
# ALUNO: ALEXANDRE DOS SANTOS BINDO CABRAL
#
# PROGRAMA 2 – Otimização Interativa de Rotas com Algoritmo Genético
# =============================================================
#
# Objetivo:
# Este programa utiliza as coordenadas geográficas armazenadas no
# arquivo "condor_curitiba.csv" para buscar uma rota otimizada entre
# as unidades da rede Condor em Curitiba-PR.
#
# A solução é obtida por meio de um Algoritmo Genético aplicado ao
# Problema do Caixeiro Viajante (TSP), utilizando seleção, cruzamento
# ordenado e mutação. As distâncias entre os pontos são calculadas
# pela fórmula de Haversine.
#
# Durante a execução, o programa apresenta de forma gráfica e
# interativa a evolução da melhor rota encontrada ao longo das
# gerações e, ao final, informa a sequência das lojas e a distância
# total da melhor solução obtida.
#
# =============================================================
import math
import random
import matplotlib.pyplot as plt
import csv


# ---------- Read CSV file ----------

def read_csv(filename):

    coords = {}
    nomes = {}

    with open(filename, newline="", encoding="utf-8-sig") as arquivo:

        leitor = csv.DictReader(arquivo)

        indice = 1

        for linha in leitor:

            try:
                latitude = float(linha["latitude"])
                longitude = float(linha["longitude"])

                coords[indice] = (latitude, longitude)
                nomes[indice] = linha["nome"]

                indice += 1

            except:
                pass

    return coords, nomes


# ---------- Haversine distance (km) ----------

def haversine_distance(coord1, coord2):

    R = 6371.0

    lat1 = math.radians(coord1[0])
    lon1 = math.radians(coord1[1])

    lat2 = math.radians(coord2[0])
    lon2 = math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(lat1) *
        math.cos(lat2) *
        math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# ---------- Objective function ----------

def tour_distance(tour, coords):

    total = 0

    for i in range(len(tour)):

        city_a = tour[i]
        city_b = tour[(i + 1) % len(tour)]

        total += haversine_distance(
            coords[city_a],
            coords[city_b]
        )

    return total
# ---------- Generate initial population ----------


def create_individual(cities):

    individual = cities[:]
    random.shuffle(individual)

    return individual


def create_population(cities, population_size):

    return [
        create_individual(cities)
        for _ in range(population_size)
    ]


# ---------- Mutation ----------

def mutate(individual, mutation_rate):

    new_individual = individual[:]

    if random.random() < mutation_rate:

        i, j = random.sample(
            range(len(new_individual)),
            2
        )

        new_individual[i], new_individual[j] = \
            new_individual[j], new_individual[i]

    return new_individual


# ---------- Ordered crossover ----------

def reproduce(parent1, parent2):

    size = len(parent1)

    start, end = sorted(
        random.sample(range(size), 2)
    )

    child = [None] * size

    child[start:end + 1] = parent1[start:end + 1]

    parent2_cities = [
        city
        for city in parent2
        if city not in child
    ]

    index = 0

    for i in range(size):

        if child[i] is None:

            child[i] = parent2_cities[index]
            index += 1

    return child


# ---------- Selection ----------

def selection(population, coords, M):

    population_sorted = sorted(
        population,
        key=lambda ind: tour_distance(ind, coords)
    )

    return population_sorted[:M]


# ---------- Plot solution ----------

def plot_tour(
    tour,
    coords,
    nomes,
    title="Melhor rota entre supermercados Condor",
    generation=None,
    distance=None
):

    plt.clf()

    x = []
    y = []

    for city in tour:
        x.append(coords[city][1])  # longitude
        y.append(coords[city][0])  # latitude

    x.append(coords[tour[0]][1])
    y.append(coords[tour[0]][0])

    plt.plot(
        x,
        y,
        "-o",
        color="blue",
        linewidth=2,
        markersize=6,
        label="Sequência da rota"
    )

    start_city = tour[0]

    plt.scatter(
        coords[start_city][1],
        coords[start_city][0],
        color="red",
        s=170,
        edgecolors="black",
        linewidths=1.5,
        zorder=10,
        label="Início"
    )

    for city in tour:

        plt.text(
            coords[city][1],
            coords[city][0],
            nomes[city],
            fontsize=7
        )

    titulo = title

    if generation is not None:

        titulo += (
            f"\nGeração {generation}"
            f"   Distância = {distance:.2f} km"
        )

    plt.title(titulo)

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    plt.grid(True)
    plt.legend()

    plt.pause(0.001)

# ---------- Evolutionary Algorithm ----------


def evolutionary_tsp(
    coords,
    nomes,
    population_size=200,
    selected_size=20,
    generations=500,
    mutation_rate=0.2
):

    cities = list(coords.keys())

    population = create_population(
        cities,
        population_size
    )

    best_solution = None
    best_distance = float("inf")

    plt.figure(figsize=(12, 8))
    plt.ion()

    for generation in range(generations):

        selected = selection(
            population,
            coords,
            selected_size
        )

        current_best = selected[0]

        current_distance = tour_distance(
            current_best,
            coords
        )

        if current_distance < best_distance:

            best_solution = current_best[:]
            best_distance = current_distance

            plot_tour(
                best_solution,
                coords,
                nomes,
                title="TSP - Rede Condor Curitiba",
                generation=generation,
                distance=best_distance
            )

        new_population = selected[:]

        while len(new_population) < population_size:

            parent1, parent2 = random.sample(
                selected,
                2
            )

            child = reproduce(
                parent1,
                parent2
            )

            child = mutate(
                child,
                mutation_rate
            )

            new_population.append(child)

        population = new_population

        print(
            f"Geração {generation} | "
            f"Melhor distância = {best_distance:.4f} km"
        )

    return best_solution, best_distance


# ---------- Main execution ----------

if __name__ == "__main__":

    coords, nomes = read_csv("condor_curitiba.csv")

    print("-----------------------------------")
    print("Supermercados carregados:", len(coords))
    print("-----------------------------------")

    best_tour, best_cost = evolutionary_tsp(
        coords,
        nomes,
        population_size=200,
        selected_size=20,
        generations=500,
        mutation_rate=0.2
    )

    print("\n===================================")
    print(" MELHOR ROTA ENCONTRADA")
    print("===================================\n")

    print("Sequência das lojas:\n")

    for cidade in best_tour:
        print(f"{cidade:02d} - {nomes[cidade]}")

    print("\n-----------------------------------")
    print(f"Distância total = {best_cost:.4f} km")
    print("-----------------------------------")

    plt.ioff()

    plot_tour(
        best_tour,
        coords,
        nomes,
        title="TSP - Rede Condor Curitiba"
    )

    plt.show()

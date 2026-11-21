# =============================================================
# ALUNO: ALEXANDRE DOS SANTOS BINDO CABRAL
#
# PROGRAMA 3 – Comparação entre a Abordagem Clássica e Quântica
# para Otimização de Rotas utilizando QUBO, Hamiltoniano e QAOA
# =============================================================
#
# Objetivo:
# Este programa implementa uma abordagem de computação quântica
# para o Problema do Caixeiro Viajante (TSP), convertendo o problema
# em uma matriz QUBO e, posteriormente, em um Hamiltoniano de Ising,
# utilizado pelo algoritmo QAOA (Quantum Approximate Optimization Algorithm).
#
# Os parâmetros do circuito quântico são otimizados pelo método
# clássico COBYLA, permitindo encontrar uma solução aproximada para
# o problema. Ao final, os resultados obtidos pelo QAOA são comparados
# com a solução clássica, analisando a rota encontrada, a distância
# percorrida e o desempenho computacional de ambas as abordagens.
#
# =============================================================
import csv
import math
import itertools
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, SparsePauliOp
from scipy.optimize import minimize
import time

# ============================================================
# DATA STRUCTURE FOR A HAMILTONIAN TERM
# ============================================================


@dataclass
class HamiltonianTerm:
    coefficient: float
    pauli: str
    qubits: tuple


# ============================================================
# READ CSV
# ============================================================

def read_csv(filename):

    coords = []
    nomes = []

    with open(filename, newline="", encoding="latin1") as arquivo:

        leitor = csv.DictReader(arquivo)

        for linha in leitor:

            try:
                nome = linha["nome"]
                lat = float(linha["latitude"])
                lon = float(linha["longitude"])

                nomes.append(nome)
                coords.append((lat, lon))

            except:
                pass

    return coords, nomes


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

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


# ============================================================
# DISTANCE MATRIX
# ============================================================

def build_distance_matrix(coords):

    n = len(coords)
    D = np.zeros((n, n))

    for i in range(n):
        for j in range(n):

            if i != j:
                D[i, j] = haversine_distance(
                    coords[i],
                    coords[j]
                )

    return D


# ============================================================
# TSP COST FUNCTION
# ============================================================

def route_distance(route, D):

    total = 0.0
    n = len(route)

    for t in range(n):

        city_a = route[t]
        city_b = route[(t + 1) % n]

        total += D[city_a, city_b]

    return total


# ============================================================
# VARIABLE INDEX
# x_{city, position}
# ============================================================

def var_index(city, position, n):

    return city * n + position
# ============================================================
# ADD QUBO TERM
# Ensures the matrix uses only the upper triangular part
# ============================================================


def add_qubo_term(Q, i, j, value):

    if i == j:
        Q[i, i] += value
    else:
        a = min(i, j)
        b = max(i, j)
        Q[a, b] += value


# ============================================================
# BUILD QUBO MATRIX FOR TSP
# ============================================================

def build_tsp_qubo(D, penalty=100.0):

    n = D.shape[0]
    num_variables = n * n

    Q = np.zeros((num_variables, num_variables))

    # Distance cost:
    # sum_{i,j} D[i,j] * sum_t x_{i,t} x_{j,t+1}

    for i in range(n):

        for j in range(n):

            if i == j:
                continue

            for t in range(n):

                a = var_index(i, t, n)
                b = var_index(j, (t + 1) % n, n)

                add_qubo_term(Q, a, b, D[i, j])

    # Constraint 1:
    # each city appears exactly once
    # penalty * (sum_t x_{i,t} - 1)^2

    for i in range(n):

        for t in range(n):

            a = var_index(i, t, n)

            add_qubo_term(Q, a, a, -penalty)

            for s in range(t + 1, n):

                b = var_index(i, s, n)

                add_qubo_term(Q, a, b, 2 * penalty)

    # Constraint 2:
    # each position has exactly one city
    # penalty * (sum_i x_{i,t} - 1)^2

    for t in range(n):

        for i in range(n):

            a = var_index(i, t, n)

            add_qubo_term(Q, a, a, -penalty)

            for j in range(i + 1, n):

                b = var_index(j, t, n)

                add_qubo_term(Q, a, b, 2 * penalty)

    return Q


# ============================================================
# QUBO VALUE
# f(x) = sum_i Q_ii x_i + sum_{i<j} Q_ij x_i x_j
# ============================================================

def qubo_value(x, Q):

    total = 0.0
    n = len(x)

    for i in range(n):
        total += Q[i, i] * x[i]

    for i in range(n):
        for j in range(i + 1, n):
            total += Q[i, j] * x[i] * x[j]

    return total


# ============================================================
# CONVERT QUBO TO ISING / PAULI HAMILTONIAN
# x_i = (1 - Z_i) / 2
# x_i x_j = (1 - Z_i - Z_j + Z_i Z_j) / 4
# ============================================================

def qubo_to_hamiltonian_terms(Q):

    terms = []
    offset = 0.0

    n = Q.shape[0]

    # Linear Q_ii x_i
    for i in range(n):

        qii = Q[i, i]

        if abs(qii) > 1e-9:

            offset += qii / 2

            terms.append(
                HamiltonianTerm(
                    coefficient=-qii / 2,
                    pauli="Z",
                    qubits=(i,)
                )
            )

    # Quadratic Q_ij x_i x_j
    for i in range(n):

        for j in range(i + 1, n):

            qij = Q[i, j]

            if abs(qij) > 1e-9:

                offset += qij / 4

                terms.append(
                    HamiltonianTerm(
                        coefficient=-qij / 4,
                        pauli="Z",
                        qubits=(i,)
                    )
                )

                terms.append(
                    HamiltonianTerm(
                        coefficient=-qij / 4,
                        pauli="Z",
                        qubits=(j,)
                    )
                )

                terms.append(
                    HamiltonianTerm(
                        coefficient=qij / 4,
                        pauli="ZZ",
                        qubits=(i, j)
                    )
                )

    return terms, offset
# ============================================================
# BUILD PAULI STRING FOR QISKIT
# ============================================================


def build_full_pauli_string(num_qubits, pauli, qubits):

    full = ["I"] * num_qubits

    for p, q in zip(pauli, qubits):
        full[num_qubits - 1 - q] = p

    return "".join(full)


def build_sparse_pauli_hamiltonian(terms, num_qubits):

    pauli_list = []

    for term in terms:

        full_pauli = build_full_pauli_string(
            num_qubits,
            term.pauli,
            term.qubits
        )

        pauli_list.append(
            (full_pauli, float(term.coefficient))
        )

    return SparsePauliOp.from_list(pauli_list)


# ============================================================
# ROUTE TO BITSTRING
# ============================================================

def route_to_bitstring(route, n):

    x = np.zeros(n * n)

    for position, city in enumerate(route):
        index = var_index(city, position, n)
        x[index] = 1

    return x


# ============================================================
# BRUTE FORCE VALIDATION
# ============================================================

def brute_force_tsp(D):

    n = D.shape[0]

    best_route = None
    best_distance = float("inf")

    for route in itertools.permutations(range(n)):

        distance = route_distance(route, D)

        if distance < best_distance:
            best_distance = distance
            best_route = route

    return best_route, best_distance


# ============================================================
# QISKIT ENERGY FROM BITSTRING
# ============================================================

def qiskit_energy_from_bitstring(x, hamiltonian, offset):

    bitstring = "".join(
        str(int(x[i]))
        for i in reversed(range(len(x)))
    )

    state = Statevector.from_label(bitstring)

    energy = state.expectation_value(hamiltonian).real + offset

    return energy


# ============================================================
# QAOA CIRCUIT - p = 1
# ============================================================

def apply_cost_unitary(qc, terms, gamma):

    for term in terms:

        coeff = float(term.coefficient)

        if term.pauli == "Z":

            q = term.qubits[0]
            qc.rz(2 * gamma * coeff, q)

        elif term.pauli == "ZZ":

            q1, q2 = term.qubits

            qc.cx(q1, q2)
            qc.rz(2 * gamma * coeff, q2)
            qc.cx(q1, q2)


def apply_mixer_unitary(qc, beta):

    for q in range(qc.num_qubits):
        qc.rx(2 * beta, q)


def build_qaoa_circuit(num_qubits, terms, beta, gamma):

    qc = QuantumCircuit(num_qubits)

    for q in range(num_qubits):
        qc.h(q)

    apply_cost_unitary(qc, terms, gamma)

    apply_mixer_unitary(qc, beta)

    return qc


def qaoa_energy(num_qubits, terms, hamiltonian, offset, beta, gamma):

    qc = build_qaoa_circuit(
        num_qubits,
        terms,
        beta,
        gamma
    )

    state = Statevector.from_instruction(qc)

    energy = state.expectation_value(hamiltonian).real + offset

    return energy

# ============================================================
# OPTIMIZE QAOA PARAMETERS WITH COBYLA
# ============================================================


def optimize_qaoa_parameters(
    num_qubits,
    terms,
    hamiltonian,
    offset
):

    def objective(params):

        beta = params[0]
        gamma = params[1]

        energy = qaoa_energy(
            num_qubits,
            terms,
            hamiltonian,
            offset,
            beta,
            gamma
        )

        return energy

    initial_params = np.array([0.5, 0.5])

    result = minimize(
        objective,
        initial_params,
        method="COBYLA",
        options={
            "maxiter": 50,
            "rhobeg": 0.5
        }
    )

    best_beta = result.x[0]
    best_gamma = result.x[1]
    best_energy = result.fun

    return best_beta, best_gamma, best_energy

# ============================================================
# DECODE BITSTRING TO TSP ROUTE
# ============================================================


def bitstring_to_route(bitstring, n):

    x = [
        int(bitstring[::-1][i])
        for i in range(len(bitstring))
    ]

    route = []

    for position in range(n):

        cities_in_position = []

        for city in range(n):

            index = var_index(city, position, n)

            if x[index] == 1:
                cities_in_position.append(city)

        if len(cities_in_position) != 1:
            return None

        route.append(cities_in_position[0])

    if len(set(route)) != n:
        return None

    return tuple(route)


# ============================================================
# RUN QAOA CIRCUIT WITH MEASUREMENTS
# ============================================================

def run_qaoa_sampling(num_qubits, terms, beta, gamma, shots=4096):

    qc = build_qaoa_circuit(
        num_qubits,
        terms,
        beta,
        gamma
    )

    qc.measure_all()

    simulator = AerSimulator()

    compiled = transpile(qc, simulator)

    result = simulator.run(
        compiled,
        shots=shots
    ).result()

    counts = result.get_counts()

    return counts
# ============================================================
# FIND BEST VALID ROUTE FROM QAOA COUNTS
# ============================================================


def find_best_qaoa_route(counts, D):

    n = D.shape[0]

    best_route = None
    best_distance = float("inf")
    best_bitstring = None
    best_count = 0

    valid_solutions = 0

    for bitstring, count in counts.items():

        route = bitstring_to_route(bitstring, n)

        if route is None:
            continue

        valid_solutions += count

        distance = route_distance(route, D)

        if distance < best_distance:

            best_distance = distance
            best_route = route
            best_bitstring = bitstring
            best_count = count

    return best_route, best_distance, best_bitstring, best_count, valid_solutions

# ============================================================
# PLOT ENERGY LANDSCAPE
# ============================================================


def plot_energy_landscape(D):

    routes = list(itertools.permutations(range(D.shape[0])))

    energies = [
        route_distance(route, D)
        for route in routes
    ]

    plt.figure(figsize=(10, 6))
    plt.plot(range(len(energies)), energies, "-o")

    plt.title("Paisagem de energia - Rotas possíveis do TSP")
    plt.xlabel("Configuração da rota")
    plt.ylabel("Energia / Distância (km)")
    plt.grid(True)
    plt.show()


# ============================================================
# REAL QAOA PARAMETER LANDSCAPE
# ============================================================

def plot_qaoa_parameter_landscape(num_qubits, terms, hamiltonian, offset):

    beta_values = np.linspace(-1, 1, 20)
    gamma_values = np.linspace(-1, 1, 20)

    B, G = np.meshgrid(beta_values, gamma_values)

    E = np.zeros_like(B)

    for i in range(B.shape[0]):
        for j in range(B.shape[1]):

            E[i, j] = qaoa_energy(
                num_qubits,
                terms,
                hamiltonian,
                offset,
                B[i, j],
                G[i, j]
            )

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot_surface(B, G, E, cmap="viridis")

    ax.set_title("Landscape real dos parâmetros QAOA")
    ax.set_xlabel("Beta")
    ax.set_ylabel("Gamma")
    ax.set_zlabel("Energia")

    plt.show()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    coords, nomes = read_csv("condor_curitiba_teste.csv")

    # Limite para rodar QAOA no simulador
    coords = coords[:4]
    nomes = nomes[:4]

    print("-----------------------------------")
    print("PROGRAMA 3 - QUBO / HAMILTONIANO / QAOA")
    print("-----------------------------------")
    print("Lojas carregadas:", len(nomes))

    for i, nome in enumerate(nomes):
        print(f"{i} - {nome}")

    D = build_distance_matrix(coords)

    print("\nMatriz de distâncias D (km):")
    print(np.round(D, 2))

    Q = build_tsp_qubo(D, penalty=100.0)

    print("\nMatriz QUBO criada.")
    print("Dimensão da matriz Q:", Q.shape)

    terms, offset = qubo_to_hamiltonian_terms(Q)

    num_qubits = Q.shape[0]

    hamiltonian = build_sparse_pauli_hamiltonian(
        terms,
        num_qubits
    )

    print("\nTermos Hamiltonianos gerados:")
    print("Total de termos:", len(terms))
    print("Número de qubits:", num_qubits)
    print("Offset:", offset)

    print("\nPrimeiros 20 termos:")
    for term in terms[:20]:
        print(term)

    # =====================================================
    # VALIDAÇÃO CLÁSSICA
    # =====================================================

    inicio_classico = time.perf_counter()

    best_route, best_distance = brute_force_tsp(D)

    fim_classico = time.perf_counter()
    tempo_classico = fim_classico - inicio_classico

    print("\n===================================")
    print(" MELHOR ROTA CLÁSSICA - VALIDAÇÃO")
    print("===================================")

    for city in best_route:
        print(f"{city} - {nomes[city]}")

    print(f"\nDistância mínima = {best_distance:.4f} km")
    print(f"Tempo da busca clássica = {tempo_classico:.6f} segundos")

    x_best = route_to_bitstring(best_route, len(nomes))

    qubo_energy = qubo_value(x_best, Q)

    qiskit_energy = qiskit_energy_from_bitstring(
        x_best,
        hamiltonian,
        offset
    )

    print("\n===================================")
    print(" FUNÇÃO DE CUSTO / QUBO")
    print("===================================")
    print("Valor QUBO da melhor rota:")
    print(qubo_energy)

    print("\nEnergia pelo Hamiltoniano no Qiskit:")
    print(qiskit_energy)

    print("\nForma conceitual usada:")
    print("f(x) = soma_i Q_ii x_i + soma_{i<j} Q_ij x_i x_j")

    # =====================================================
    # EXECUÇÃO DO QAOA
    # =====================================================

    print("\n===================================")
    print(" EXECUÇÃO DO QAOA COM MEDIÇÕES")
    print("===================================")

    print("\n===================================")
    print(" OTIMIZAÇÃO DOS PARÂMETROS QAOA")
    print("===================================")

    inicio_cobyla = time.perf_counter()

    best_beta, best_gamma, best_qaoa_energy = optimize_qaoa_parameters(
        num_qubits,
        terms,
        hamiltonian,
        offset
    )
    fim_cobyla = time.perf_counter()
    tempo_cobyla = fim_cobyla - inicio_cobyla

    print(f"Melhor beta encontrado: {best_beta:.6f}")
    print(f"Melhor gamma encontrado: {best_gamma:.6f}")
    print(f"Menor energia QAOA encontrada: {best_qaoa_energy:.6f}")
    print(f"Tempo da otimização COBYLA = {tempo_cobyla:.6f} segundos")
    beta = best_beta
    gamma = best_gamma

    inicio_qaoa = time.perf_counter()
    counts = run_qaoa_sampling(
        num_qubits,
        terms,
        beta,
        gamma,
        shots=4096
    )
    fim_qaoa = time.perf_counter()
    tempo_qaoa = fim_qaoa - inicio_qaoa

    (
        qaoa_route,
        qaoa_distance,
        qaoa_bitstring,
        qaoa_count,
        valid_solutions
    ) = find_best_qaoa_route(
        counts,
        D
    )

    print(f"Beta usado: {beta:.6f}")
    print(f"Gamma usado: {gamma:.6f}")
    print("Total de medições:", sum(counts.values()))
    print("Soluções válidas encontradas:", valid_solutions)
    print(f"Tempo da execução do QAOA = {tempo_qaoa:.6f} segundos")

    if qaoa_route is not None:

        print("\nMelhor rota encontrada pelo QAOA:")

        for city in qaoa_route:
            print(f"{city} - {nomes[city]}")

        print(f"\nDistância QAOA = {qaoa_distance:.4f} km")
        print("Bitstring:", qaoa_bitstring)
        print("Frequência:", qaoa_count)

    else:

        print("\nO QAOA não encontrou rota válida nessa execução.")

    # =====================================================
    # RESUMO FINAL
    # =====================================================

    print("\n===================================")
    print(" RESUMO FINAL - CLÁSSICO x QAOA")
    print("===================================")

    print(f"Distância clássica = {best_distance:.4f} km")

    if qaoa_route is not None:

        diferenca = abs(qaoa_distance - best_distance)

        erro_relativo = (diferenca / best_distance) * 100

        print(f"Distância QAOA     = {qaoa_distance:.4f} km")
        print(f"Diferença          = {diferenca:.4f} km")
        print(f"Erro relativo      = {erro_relativo:.4f} %")

        print("\nTempos de execução:")
        print(f"Busca clássica     = {tempo_classico:.6f} segundos")
        print(f"Otimização COBYLA  = {tempo_cobyla:.6f} segundos")
        print(f"Execução QAOA      = {tempo_qaoa:.6f} segundos")

        if diferenca < 0.01:
            print("\nResultado:")
            print("O QAOA encontrou uma solução equivalente à solução clássica.")
        else:
            print("\nResultado:")
            print("O QAOA encontrou uma solução aproximada, mas diferente da clássica.")

    else:

        print("\nO QAOA não encontrou rota válida nesta execução.")
        print("\nTempos de execução:")
        print(f"Busca clássica     = {tempo_classico:.6f} segundos")
        print(f"Otimização COBYLA  = {tempo_cobyla:.6f} segundos")
        print(f"Execução QAOA      = {tempo_qaoa:.6f} segundos")

    # =====================================================
    # ENCERRAMENTO
    # =====================================================

    print("\n===================================")
    print(" HAMILTONIANO FINAL")
    print("===================================")
    print(f"Total de termos de Pauli = {len(terms)}")
    print(f"Número de qubits         = {num_qubits}")
    print(f"Offset do Hamiltoniano   = {offset:.6f}")

    print("\n===================================")
    print(" PROGRAMA FINALIZADO COM SUCESSO")
    print("===================================")

    # =====================================================
    # GRÁFICOS
    # =====================================================

    plot_energy_landscape(D)

    plot_qaoa_parameter_landscape(
        num_qubits,
        terms,
        hamiltonian,
        offset
    )

from go_knapsack import GeneticAlgorithm
import matplotlib.pyplot as plt

def plot_results(results_dict, title, optimum=None):
    plt.figure(figsize=(12, 8))
    
    for series_name, fitness_history in results_dict.items():
        plt.plot(fitness_history, label=series_name)
    
    if optimum is not None:
        plt.axhline(y=optimum, color='r', linestyle='--', label=f'Optimum ({optimum})')

    plt.title(title)
    plt.xlabel("Generation")
    plt.ylabel("Best Fitness")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    
    # --- USTAWIENIA ---
    # Zmień 'data_file_path' na ścieżkę do Twojego pliku z danymi
    DATA_FILE_PATH = "low-dimensional/f1_l-d_kp_10_269"  # <--- ZMIEŃ TO
    OPTIMUM_VALUE = 295                        # <--- ZMIEŃ TO (na optimum dla tego pliku)
    
    POPULATION_SIZE = 100
    ITERATIONS = 200
    CROSSOVER_PROB = 0.8
    MUTATION_PROB = 0.02 # 2% na gen

    # Inicjalizacja głównego obiektu
    ga = GeneticAlgorithm(
        data_file=DATA_FILE_PATH,
        population_size=POPULATION_SIZE,
        crossover_prob=CROSSOVER_PROB,
        mutation_prob=MUTATION_PROB,
        iterations=ITERATIONS
    )

    # --- Eksperyment 1: Porównanie selekcji (Wymaganie 4.5) ---
    print("\n--- Running Experiment 1: Selection Methods ---")
    
    # Używamy tego samego krzyżowania (1-punktowego) do obu testów
    results_selection = {}
    
    history_roulette = ga.run_evolution(
        selection_method=ga.selection_roulette_wheel,
        crossover_method=ga.crossover_one_point
    )
    results_selection["Roulette Wheel Selection"] = history_roulette
    
    history_rank = ga.run_evolution(
        selection_method=ga.selection_rank,
        crossover_method=ga.crossover_one_point
    )
    results_selection["Rank Selection"] = history_rank

    plot_results(
        results_selection,
        f"Selection Comparison (File: {DATA_FILE_PATH})",
        OPTIMUM_VALUE
    )

    # --- Eksperyment 2: Porównanie krzyżowania (Wymaganie 4.5) ---
    print("\n--- Running Experiment 2: Crossover Methods ---")
    
    # Używamy tej samej selekcji (np. rank) do obu testów
    results_crossover = {}
    
    history_one_point = ga.run_evolution(
        selection_method=ga.selection_rank,
        crossover_method=ga.crossover_one_point
    )
    results_crossover["One-Point Crossover"] = history_one_point
    
    history_two_point = ga.run_evolution(
        selection_method=ga.selection_rank,
        crossover_method=ga.crossover_two_point
    )
    results_crossover["Two-Point Crossover"] = history_two_point
    
    plot_results(
        results_crossover,
        f"Crossover Comparison (File: {DATA_FILE_PATH})",
        OPTIMUM_VALUE
    )
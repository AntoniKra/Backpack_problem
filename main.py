from go_knapsack import GeneticAlgorithm
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

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


def get_file_path():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="Wybierz plik danych")


if __name__ == "__main__":
    
    DATA_FILE_PATH = get_file_path() 
    DATA_FILE_PATH_SPLITTED = DATA_FILE_PATH.split("/")

    DATA_FILE_PATH_SPLITTED[len(DATA_FILE_PATH_SPLITTED)-2] = DATA_FILE_PATH_SPLITTED[len(DATA_FILE_PATH_SPLITTED)-2] + "-optimum"
    DATA_FILE_PATH_OPTIMUM=""

    for i in range(0,len(DATA_FILE_PATH_SPLITTED)):
        current = DATA_FILE_PATH_SPLITTED[i]
        if i == len(DATA_FILE_PATH_SPLITTED)-1:
            DATA_FILE_PATH_OPTIMUM += current
            continue
        DATA_FILE_PATH_OPTIMUM += current+'/'

    OPTIMUM_VALUE = 0

    with open(DATA_FILE_PATH_OPTIMUM, 'r') as f:
            first_line = f.readline().split()
            OPTIMUM_VALUE = int(first_line[0])  
            
    print(OPTIMUM_VALUE)         
    print("Population size:")
    POPULATION_SIZE =  int(input()) 
    print("Iterations:")
    ITERATIONS = int(input())
    print("Crossover probability")
    CROSSOVER_PROB =  float(input())  
    if(CROSSOVER_PROB < 0.5 or CROSSOVER_PROB > 1):
        print("CROSSOVER_PROB value must be between 0.5 and 1")
        quit()
    
    print("Mutation probability")
    MUTATION_PROB = float(input()) 
    if(MUTATION_PROB > 0.1 and MUTATION_PROB < 0):
        print("MUTATION_PROB value must be positive and smaller or equal to 0.1")
        quit()

    

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
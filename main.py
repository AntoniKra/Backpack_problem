# Importowanie niezbędnych bibliotek
from go_knapsack import GeneticAlgorithm  # Importuje główną klasę algorytmu genetycznego
import matplotlib.pyplot as plt          # Biblioteka do tworzenia wykresów
import tkinter as tk                     # Biblioteka do tworzenia prostych okien GUI
from tkinter import filedialog           # Specyficznie do okna dialogowego wyboru pliku

def plot_results(results_dict, title, optimum=None):
    """
    Funkcja do rysowania wykresów wyników ewolucji.
    
    :param results_dict: Słownik, gdzie klucze to nazwy serii, a wartości to historie fitnessu.
    :param title: Tytuł wykresu.
    :param optimum: (Opcjonalnie) Wartość optymalna, która zostanie narysowana jako linia pozioma.
    """
    plt.figure(figsize=(12, 8))  # Ustawienie rozmiaru okna wykresu
    
    # Pętla przez wszystkie serie wyników (np. "Selekcja Rankingowa")
    for series_name, fitness_history in results_dict.items():
        plt.plot(fitness_history, label=series_name)  # Rysowanie linii dla danej serii
    
    # Jeśli podano optimum, narysuj czerwoną, przerywaną linię
    if optimum is not None:
        plt.axhline(y=optimum, color='r', linestyle='--', label=f'Optimum ({optimum})')

    # Ustawienie etykiet i tytułu
    plt.title(title)
    plt.xlabel("Generacja")
    plt.ylabel("Najlepszy Fitness")
    plt.legend()  # Pokaż legendę (opisy linii)
    plt.grid(True)  # Pokaż siatkę
    plt.show()  # Wyświetl wykres


def get_file_path():
    """
    Otwiera okno dialogowe (używając Tkinter), aby użytkownik mógł wybrać plik.
    """
    root = tk.Tk()  # Inicjalizacja głównego okna Tkinter
    root.withdraw()  # Ukrycie tego głównego okna (potrzebujemy tylko okna dialogowego)
    
    # Otwórz okno "Wybierz plik"
    file_path = filedialog.askopenfilename(title="Wybierz plik danych")
    
    if not file_path:  # Jeśli użytkownik zamknie okno bez wyboru
        print("Nie wybrano pliku. Zamykanie aplikacji.")
        quit()  # Zakończ program
    return file_path

def get_recommendations(file_type):
    """
    Zwraca słownik z zalecanymi zakresami parametrów na podstawie typu problemu.
    """
    if file_type == "low-dimensional":
        # Małe problemy (np. 10-20 przedmiotów)
        return {
            "pop_size": (20, 50),
            "iterations": (50, 100),
            "mutation_prob": (0.02, 0.05), # Np. 1/20 = 0.05
            "crossover_prob": (0.8, 0.9)
        }
    elif file_type == "large_scale":
        # Duże problemy (np. 100 przedmiotów)
        return {
            "pop_size": (100, 200),
            "iterations": (200, 500),
            "mutation_prob": (0.01, 0.02), # Np. 1/100 = 0.01
            "crossover_prob": (0.8, 0.9)
        }
    else:
        # Nieznany typ, brak zaleceń
        return {}

def get_validated_input(prompt, input_type=int, rec_range=None, hard_min=None, hard_max=None):
    """
    Pobiera dane od użytkownika z walidacją twardą (błąd) i miękką (ostrzeżenie).
    
    :param prompt: Tekst wyświetlany użytkownikowi (np. "Podaj liczbę:")
    :param input_type: Typ danych, jaki chcemy otrzymać (np. int lub float)
    :param rec_range: (Opcjonalnie) Krotka (min, max) z zalecanym zakresem (wyświetli ostrzeżenie)
    :param hard_min: (Opcjonalnie) Twarda dolna granica (wyświetli błąd i poprosi ponownie)
    :param hard_max: (Opcjonalnie) Twarda górna granica (wyświetli błąd i poprosi ponownie)
    """
    while True:  # Pętla działa, dopóki użytkownik nie poda poprawnej wartości
        try:
            user_input_str = input(prompt)  # Pobranie tekstu od użytkownika
            value = input_type(user_input_str)  # Próba konwersji na docelowy typ
            
            # 1. Twarde ograniczenia (przerywają i proszą ponownie)
            if hard_min is not None and value < hard_min:
                print(f"BŁĄD: Wartość musi być większa lub równa {hard_min}. Spróbuj ponownie.")
                continue  # Wróć na początek pętli
            if hard_max is not None and value > hard_max:
                print(f"BŁĄD: Wartość musi być mniejsza lub równa {hard_max}. Spróbuj ponownie.")
                continue  # Wróć na początek pętli
                
            # 2. Miękkie ograniczenia (tylko ostrzeżenie)
            if rec_range is not None:
                if not (rec_range[0] <= value <= rec_range[1]):
                    print(f"--- OSTRZEŻENIE: Wartość jest poza zalecanym zakresem ({rec_range[0]} - {rec_range[1]}). ---")
            
            # Jeśli kod doszedł tutaj, walidacja się powiodła
            return value
            
        except ValueError:
            # Jeśli konwersja (np. float("abc")) się nie powiodła
            print(f"BŁĄD: Niepoprawny typ danych. Oczekiwano {input_type.__name__}. Spróbuj ponownie.")
        except Exception as e:
            # Inne nieoczekiwane błędy
            print(f"Wystąpił nieoczekiwany błąd: {e}")


# --- Główny blok programu ---
# Kod w tym bloku uruchomi się tylko wtedy, gdy plik main.py jest uruchamiany bezpośrednio
if __name__ == "__main__":
    
    # 1. Pobranie ścieżki do pliku z danymi od użytkownika
    DATA_FILE_PATH = get_file_path() 
    
    # 2. Automatyczne ustalanie ścieżki do pliku z wartością optymalną
    DATA_FILE_PATH_SPLITTED = DATA_FILE_PATH.split("/")
    DATA_FILE_PATH_SPLITTED[len(DATA_FILE_PATH_SPLITTED)-2] = DATA_FILE_PATH_SPLITTED[len(DATA_FILE_PATH_SPLITTED)-2] + "-optimum"
    DATA_FILE_PATH_OPTIMUM = ""

    for i in range(0, len(DATA_FILE_PATH_SPLITTED)):
        current = DATA_FILE_PATH_SPLITTED[i]
        if i == len(DATA_FILE_PATH_SPLITTED)-1:
            DATA_FILE_PATH_OPTIMUM += current
            continue
        DATA_FILE_PATH_OPTIMUM += current + '/'

    # 3. Wczytanie wartości optymalnej z pliku
    OPTIMUM_VALUE = 0
    try:
        with open(DATA_FILE_PATH_OPTIMUM, 'r') as f:
            first_line = f.readline().split()
            OPTIMUM_VALUE = int(first_line[0])
    except FileNotFoundError:
        # Obsługa błędu, jeśli plik optimum nie istnieje
        print(f"OSTRZEŻENIE: Nie znaleziono pliku optimum: {DATA_FILE_PATH_OPTIMUM}")
        print("Wykresy będą rysowane bez linii optimum.")
    except Exception as e:
        # Inne błędy przy wczytywaniu
        print(f"Błąd podczas ładowania pliku optimum: {e}")
        OPTIMUM_VALUE = 0
            
    print(f"Załadowano optimum: {OPTIMUM_VALUE}")
    
    # 4. Wykrywanie typu pliku i wyświetlanie zaleceń
    file_type = "unknown"
    if "low-dimensional" in DATA_FILE_PATH:
        file_type = "low-dimensional"
    elif "large_scale" in DATA_FILE_PATH:
        file_type = "large_scale"

    print(f"\n--- Wykryto typ pliku: {file_type} ---")
    recs = get_recommendations(file_type)  # Pobranie słownika zaleceń
    
    if recs:
        # Wyświetlenie zaleceń, jeśli udało się je ustalić
        print("Zalecane parametry dla tego typu pliku:")
        print(f"  > Rozmiar populacji: {recs['pop_size'][0]} - {recs['pop_size'][1]}")
        print(f"  > Iteracje:           {recs['iterations'][0]} - {recs['iterations'][1]}")
        print(f"  > P. mutacji:         {recs['mutation_prob'][0]} - {recs['mutation_prob'][1]}")
        print(f"  > P. krzyżowania:     {recs['crossover_prob'][0]} - {recs['crossover_prob'][1]}")
    else:
        print("Nie można było automatycznie określić zaleceń dla tego pliku.")

    
    print("\n--- Wprowadź parametry algorytmu ---")
    
    # 5. Pobieranie parametrów od użytkownika z użyciem walidacji
    #    (Te parametry będą bazowe dla wszystkich eksperymentów)
    POPULATION_SIZE = get_validated_input(
        "Rozmiar populacji: ", 
        input_type=int, 
        rec_range=recs.get('pop_size'), # Miękka walidacja (ostrzeżenie)
        hard_min=4  # Twardy limit (błąd)
    )
    
    ITERATIONS = get_validated_input(
        "Liczba iteracji: ", 
        input_type=int, 
        rec_range=recs.get('iterations'),
        hard_min=1
    )
    
    # Zapisujemy je jako "bazowe" do późniejszego użytku
    BASE_MUTATION_PROB = get_validated_input(
        "Prawdopodobieństwo mutacji (bazowe): ", 
        input_type=float, 
        rec_range=recs.get('mutation_prob'),
        hard_min=0.0,
        hard_max=0.1  # Twardy limit (zgodnie z pierwotnymi założeniami)
    )

    BASE_CROSSOVER_PROB = get_validated_input(
        "Prawdopodobieństwo krzyżowania (bazowe): ", 
        input_type=float, 
        rec_range=recs.get('crossover_prob'),
        hard_min=0.5, # Twardy limit (zgodnie z pierwotnymi założeniami)
        hard_max=1.0
    )

    # 6. Inicjalizacja głównego obiektu algorytmu genetycznego
    ga = GeneticAlgorithm(
        data_file=DATA_FILE_PATH,
        population_size=POPULATION_SIZE,
        crossover_prob=BASE_CROSSOVER_PROB,
        mutation_prob=BASE_MUTATION_PROB,
        iterations=ITERATIONS
    )

    # --- Eksperyment 1: Porównanie selekcji (Wymaganie 4.5) ---
    print("\n--- Uruchamianie Eksperymentu 1: Metody Selekcji ---")
    
    # Upewniamy się, że algorytm używa bazowych parametrów
    ga.set_mutation_prob(BASE_MUTATION_PROB)
    ga.set_crossover_prob(BASE_CROSSOVER_PROB)
    
    results_selection = {}  # Słownik do przechowywania wyników
    
    history_roulette = ga.run_evolution(
        selection_method=ga.selection_roulette_wheel,
        crossover_method=ga.crossover_one_point
    )
    results_selection["Selekcja Kołem Ruletki"] = history_roulette
    
    history_rank = ga.run_evolution(
        selection_method=ga.selection_rank,
        crossover_method=ga.crossover_one_point
    )
    results_selection["Selekcja Rankingowa"] = history_rank

    plot_results(
        results_selection,
        f"Porównanie Selekcji (Plik: {DATA_FILE_PATH})",
        OPTIMUM_VALUE
    )

    # --- Eksperyment 2: Porównanie krzyżowania (Wymaganie 4.5) ---
    print("\n--- Uruchamianie Eksperymentu 2: Metody Krzyżowania ---")
    
    # Upewniamy się, że algorytm używa bazowych parametrów
    ga.set_mutation_prob(BASE_MUTATION_PROB)
    ga.set_crossover_prob(BASE_CROSSOVER_PROB)
    
    results_crossover = {}
    
    history_one_point = ga.run_evolution(
        selection_method=ga.selection_rank,
        crossover_method=ga.crossover_one_point
    )
    results_crossover["Krzyżowanie Jednopunktowe"] = history_one_point
    
    history_two_point = ga.run_evolution(
        selection_method=ga.selection_rank,
        crossover_method=ga.crossover_two_point
    )
    results_crossover["Krzyżowanie Dwupunktowe"] = history_two_point
    
    plot_results(
        results_crossover,
        f"Porównanie Krzyżowania (Plik: {DATA_FILE_PATH})",
        OPTIMUM_VALUE
    )

    # --- NOWY EKSPERYMENT 3a: Porównanie współczynników mutacji (Wymaganie 3.5) ---
    print("\n--- Uruchamianie Eksperymentu 3a: Współczynniki Mutacji ---")
    
    # Używamy Selekcji Rankingowej i Krzyżowania Jednopunktowego jako stabilnej bazy
    # Używamy BAZOWEGO prawdopodobieństwa krzyżowania
    ga.set_crossover_prob(BASE_CROSSOVER_PROB)

    # Definiujemy listę współczynników do przetestowania
    MUTATION_RATES_TO_TEST = [0.0, 0.01, 0.02, 0.05, 0.1]
    results_mutation = {}

    for rate in MUTATION_RATES_TO_TEST:
        print(f"\n--- Testowanie P. Mutacji: {rate} ---")
        ga.set_mutation_prob(rate)  # Ustawiamy nową wartość mutacji
        
        history = ga.run_evolution(
            selection_method=ga.selection_rank,
            crossover_method=ga.crossover_one_point
        )
        results_mutation[f"Mutacja {rate}"] = history

    # Rysowanie wykresu porównawczego dla mutacji
    plot_results(
        results_mutation,
        f"Porównanie współczynników mutacji (Plik: {DATA_FILE_PATH})",
        OPTIMUM_VALUE
    )

    # --- NOWY EKSPERYMENT 3b: Porównanie współczynników krzyżowania (Wymaganie 3.5) ---
    print("\n--- Uruchamianie Eksperymentu 3b: Współczynniki Krzyżowania ---")
    
    # Używamy BAZOWEGO prawdopodobieństwa mutacji
    ga.set_mutation_prob(BASE_MUTATION_PROB)
    
    # Definiujemy listę współczynników do przetestowania
    CROSSOVER_RATES_TO_TEST = [0.5, 0.7, 0.8, 0.9, 1.0]
    results_crossover_rates = {}

    for rate in CROSSOVER_RATES_TO_TEST:
        print(f"\n--- Testowanie P. Krzyżowania: {rate} ---")
        ga.set_crossover_prob(rate)  # Ustawiamy nową wartość krzyżowania
        
        history = ga.run_evolution(
            selection_method=ga.selection_rank,
            crossover_method=ga.crossover_one_point
        )
        results_crossover_rates[f"Krzyżowanie {rate}"] = history

    # Rysowanie wykresu porównawczego dla krzyżowania
    plot_results(
        results_crossover_rates,
        f"Porównanie współczynników krzyżowania (Plik: {DATA_FILE_PATH})",
        OPTIMUM_VALUE
    )
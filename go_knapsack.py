import random

class Item:
    """
    Prosta klasa reprezentująca pojedynczy przedmiot w plecaku.
    Posiada dwa atrybuty: wartość (value) i wagę (weight).
    """
    def __init__(self, value, weight):
        self.value = value
        self.weight = weight

    def __repr__(self):
        """Reprezentacja tekstowa obiektu, przydatna przy debugowaniu."""
        return f"(V: {self.value}, W: {self.weight})"

class Individual:
    """
    Reprezentuje pojedynczego osobnika (kandydata na rozwiązanie) w populacji.
    Osobnik ma "genotyp" (listę 0 i 1) oraz obliczoną "wartość fitness".
    """
    def __init__(self, items, capacity, genotype=None):
        self.items = items  # Lista wszystkich dostępnych przedmiotów (referencja)
        self.capacity = capacity  # Maksymalna pojemność plecaka (referencja)
        self.chromosome_length = len(items)  # Długość chromosomu (liczba przedmiotów)
        
        if genotype is None:
            # Jeśli nie podano genotypu (np. przy tworzeniu pierwszej populacji),
            # stwórz losowy genotyp (losową listę 0 i 1).
            self.genotype = [random.randint(0, 1) for _ in range(self.chromosome_length)]
        else:
            # Jeśli podano genotyp (np. po krzyżowaniu), użyj go.
            self.genotype = genotype
        
        # Oblicz fitness dla tego genotypu.
        self.fitness = self.calculate_fitness()

    def calculate_fitness(self):
        """
        Oblicza wartość fitness dla osobnika na podstawie jego genotypu.
        Jest to kluczowa funkcja całego algorytmu.
        """
        total_weight = 0
        total_value = 0
        
        # Przejdź przez genotyp bit po bicie
        for i in range(self.chromosome_length):
            if self.genotype[i] == 1:
                # Jeśli genotyp ma '1' na pozycji 'i', dodaj przedmiot 'i' do plecaka
                current_item = self.items[i]
                total_weight += current_item.weight
                total_value += current_item.value
        
        if total_weight > self.capacity:
            # Jeśli plecak jest za ciężki, osobnik jest "niepoprawny".
            # Zamiast dawać mu fitness 0, dajemy mu małą wartość ułamkową.
            # Im mniejsze przeładowanie, tym bliżej 1 jest ten ułamek.
            # Daje to algorytmowi "wskazówkę", by dążył do zmniejszania wagi.
            fitness = self.capacity / total_weight
            return fitness
        
        # Jeśli waga jest w porządku, fitness to po prostu suma wartości.
        # Pusty plecak (total_value = 0) to najgorsze poprawne rozwiązanie.
        # Każde niepoprawne rozwiązanie ma fitness (0, 1).
        return total_value

    def __repr__(self):
        """Reprezentacja tekstowa osobnika."""
        return f"Fitness: {self.fitness}"

class GeneticAlgorithm:
    """
    Główna klasa zarządzająca całym procesem ewolucji.
    """
    
    def __init__(self, data_file, population_size, crossover_prob, mutation_prob, iterations):
        # Inicjalizacja parametrów algorytmu
        self.population_size = population_size
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.iterations = iterations
        
        # Wczytanie danych z pliku
        self.capacity, self.items = self.load_data(data_file)
        self.chromosome_length = len(self.items)
        
        # Stworzenie pierwszej, losowej populacji
        self.population = self.create_initial_population()

    def load_data(self, data_file):
        """Wczytuje dane problemu (pojemność i listę przedmiotów) z pliku tekstowego."""
        items = []
        with open(data_file, 'r') as f:
            first_line = f.readline().split()
            # Pierwsza linia pliku: [liczba_przedmiotow] [pojemnosc_plecaka]
            capacity = int(first_line[1])
            
            # Kolejne linie: [wartosc] [waga]
            for line in f:
                if line.strip():  # Ignoruj puste linie
                    value, weight = line.split()
                    items.append(Item(int(value), int(weight)))
        
        return capacity, items

    def create_initial_population(self):
        """Tworzy listę losowych osobników o rozmiarze `population_size`."""
        return [Individual(self.items, self.capacity) for _ in range(self.population_size)]

    def find_best_individual(self, population):
        """Znajduje i zwraca najlepszego osobnika z danej populacji."""
        return max(population, key=lambda ind: ind.fitness)

    # --- METODY SELEKCJI ---

    def selection_roulette_wheel(self):
        """Metoda selekcji kołem ruletki."""
        total_fitness = sum(ind.fitness for ind in self.population)
        
        if total_fitness == 0:
            # Sytuacja awaryjna (np. cała populacja ma fitness 0)
            return [random.choice(self.population) for _ in range(self.population_size)]

        # Prawdopodobieństwo wyboru jest proporcjonalne do fitnessu
        selection_probs = [ind.fitness / total_fitness for ind in self.population]
        
        # Losowanie `population_size` osobników do nowej puli rodziców
        selected_population = random.choices(
            self.population,
            weights=selection_probs,
            k=self.population_size
        )
        return selected_population

    def selection_rank(self):
        """Metoda selekcji rankingowej."""
        # Sortowanie populacji od najgorszego do najlepszego
        sorted_population = sorted(self.population, key=lambda ind: ind.fitness)
        
        N = self.population_size
        total_rank_sum = N * (N + 1) / 2  # Suma rang (1 + 2 + ... + N)
        
        if total_rank_sum == 0:
             # Sytuacja awaryjna
             return [random.choice(self.population) for _ in range(self.population_size)]

        # Prawdopodobieństwo wyboru jest proporcjonalne do miejsca w rankingu
        selection_probs = [(i + 1) / total_rank_sum for i in range(N)]
        
        # Losowanie `population_size` osobników do nowej puli rodziców
        selected_population = random.choices(
            sorted_population,
            weights=selection_probs,
            k=N
        )
        return selected_population

    # --- METODY KRZYŻOWANIA ---

    def crossover_one_point(self, parent1, parent2):
        """Krzyżowanie jednopunktowe."""
        if random.random() > self.crossover_prob:
            # Jeśli losowanie się nie powiodło, zwróć rodziców bez zmian
            return parent1, parent2
        
        # Losowanie punktu cięcia (od 1 do przedostatniego bitu)
        cut_point = random.randint(1, self.chromosome_length - 1)
        
        # Tworzenie genotypów dzieci
        child1_genotype = parent1.genotype[:cut_point] + parent2.genotype[cut_point:]
        child2_genotype = parent2.genotype[:cut_point] + parent1.genotype[cut_point:]
        
        # Tworzenie nowych obiektów Individual z nowymi genotypami
        child1 = Individual(self.items, self.capacity, child1_genotype)
        child2 = Individual(self.items, self.capacity, child2_genotype)
        
        return child1, child2

    def crossover_two_point(self, parent1, parent2):
        """Krzyżowanie dwupunktowe."""
        if random.random() > self.crossover_prob:
            # Jeśli losowanie się nie powiodło, zwróć rodziców bez zmian
            return parent1, parent2
        
        # Losowanie dwóch różnych punktów cięcia
        p1, p2 = sorted(random.sample(range(1, self.chromosome_length), 2))
        
        gen1 = parent1.genotype
        gen2 = parent2.genotype
        
        # Wymiana "środkowej" części genotypu
        child1_genotype = gen1[:p1] + gen2[p1:p2] + gen1[p2:]
        child2_genotype = gen2[:p1] + gen1[p1:p2] + gen2[p2:]
        
        child1 = Individual(self.items, self.capacity, child1_genotype)
        child2 = Individual(self.items, self.capacity, child2_genotype)
        
        return child1, child2

    # --- METODA MUTACJI ---

    def mutate(self, individual):
        """Mutacja osobnika poprzez odwrócenie bitów (bit-flip)."""
        genotype = individual.genotype[:]  # Stwórz kopię genotypu
        
        for i in range(self.chromosome_length):
            if random.random() < self.mutation_prob:
                # Jeśli losowanie się powiodło, odwróć bit (0 -> 1, 1 -> 0)
                genotype[i] = 1 - genotype[i]
        
        # Zwróć nowego osobnika (lub starego, jeśli mutacja nie zaszła)
        return Individual(self.items, self.capacity, genotype)

    # --- GŁÓWNA PĘTLA EWOLUCJI ---

    def run_evolution(self, selection_method, crossover_method):
        """
        Uruchamia główną pętlę algorytmu genetycznego na `iterations` pokoleń.
        """
        
        print(f"Start ewolucji: Selekcja={selection_method.__name__}, Krzyżowanie={crossover_method.__name__}")
        
        # Resetowanie populacji na początku każdego eksperymentu
        self.population = self.create_initial_population()
        best_fitness_history = []  # Lista do przechowywania najlepszego fitnessu z każdej generacji

        # Pętla główna - wykonuje się 'iterations' razy
        for i in range(self.iterations):
            # 1. Znajdź najlepszego osobnika w bieżącej populacji
            best_in_gen = self.find_best_individual(self.population)
            # Zapisz jego fitness do historii (na potrzeby wykresu)
            best_fitness_history.append(best_in_gen.fitness)

            # Logowanie postępów co 20 generacji
            if (i + 1) % 20 == 0:
                current_fitness = best_in_gen.fitness
                if current_fitness < 1:
                    print(f"Iteracja {i+1}/{self.iterations}: Najlepszy Fitness = {current_fitness:.4f} (ciągle niepoprawny)")
                else:
                    print(f"Iteracja {i+1}/{self.iterations}: Najlepszy Fitness = {current_fitness}")

            # 2. Selekcja -> Stworzenie puli rodziców
            parents_pool = selection_method()
            
            # 3. Tworzenie nowej populacji
            new_population = []
            
            # Wypełnij nową populację dziećmi
            while len(new_population) < self.population_size:
                # a. Wybierz 2 rodziców z puli
                parent1, parent2 = random.sample(parents_pool, 2)
                
                # b. Krzyżowanie
                child1, child2 = crossover_method(parent1, parent2)
                
                # c. Mutacja
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                # d. Dodaj dzieci do nowej populacji
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    # Dodaj drugie dziecko tylko, jeśli jest jeszcze miejsce
                    new_population.append(child2)
            
            # 4. Zastąp starą populację nową
            self.population = new_population
        
        print("Ewolucja zakończona.")
        return best_fitness_history

    # --- NOWE FUNKCJE (SETTERY) ---
    
    def set_mutation_prob(self, prob):
        """Pozwala na zmianę prawdopodobieństwa mutacji po inicjalizacji."""
        if 0.0 <= prob <= 0.1:
            self.mutation_prob = prob
        else:
            print(f"OSTRZEŻENIE: Próba ustawienia nieprawidłowej stopy mutacji: {prob}. Używam domyślnej.")

    def set_crossover_prob(self, prob):
        """Pozwala na zmianę prawdopodobieństwa krzyżowania po inicjalizacji."""
        if 0.5 <= prob <= 1.0:
            self.crossover_prob = prob
        else:
            print(f"OSTRZEŻENIE: Próba ustawienia nieprawidłowej stopy krzyżowania: {prob}. Używam domyślnej.")
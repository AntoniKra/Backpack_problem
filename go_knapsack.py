import random

class Item:
    def __init__(self, value, weight):
        self.value = value
        self.weight = weight

    def __repr__(self):
        return f"(V: {self.value}, W: {self.weight})"

class Individual:
    def __init__(self, items, capacity, genotype=None):
        self.items = items
        self.capacity = capacity
        self.chromosome_length = len(items)
        
        if genotype is None:
            self.genotype = [random.randint(0, 1) for _ in range(self.chromosome_length)]
        else:
            self.genotype = genotype
        
        self.fitness = self.calculate_fitness()

    def calculate_fitness(self):
        total_weight = 0
        total_value = 0
        
        for i in range(self.chromosome_length):
            if self.genotype[i] == 1:
                current_item = self.items[i]
                total_weight += current_item.weight
                total_value += current_item.value
        
        if total_weight > self.capacity:
            return 0
        
        return total_value

    def __repr__(self):
        return f"Fitness: {self.fitness}"

class GeneticAlgorithm:
    
    def __init__(self, data_file, population_size, crossover_prob, mutation_prob, iterations):
        self.population_size = population_size
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.iterations = iterations
        
        self.capacity, self.items = self.load_data(data_file)
        self.chromosome_length = len(self.items)
        self.population = self.create_initial_population()

    def load_data(self, data_file):
        items = []
        with open(data_file, 'r') as f:
            first_line = f.readline().split()
            capacity = int(first_line[1])
            
            for line in f:
                if line.strip():
                    value, weight = line.split()
                    items.append(Item(int(value), int(weight)))
        
        return capacity, items

    def create_initial_population(self):
        return [Individual(self.items, self.capacity) for _ in range(self.population_size)]

    def find_best_individual(self, population):
        return max(population, key=lambda ind: ind.fitness)

    def selection_roulette_wheel(self):
        total_fitness = sum(ind.fitness for ind in self.population)
        
        if total_fitness == 0:
            return [random.choice(self.population) for _ in range(self.population_size)]

        selection_probs = [ind.fitness / total_fitness for ind in self.population]
        
        selected_population = random.choices(
            self.population,
            weights=selection_probs,
            k=self.population_size
        )
        return selected_population

    def selection_rank(self):
        sorted_population = sorted(self.population, key=lambda ind: ind.fitness)
        
        N = self.population_size
        total_rank_sum = N * (N + 1) / 2
        
        if total_rank_sum == 0:
            return [random.choice(self.population) for _ in range(self.population_size)]

        selection_probs = [(i + 1) / total_rank_sum for i in range(N)]
        
        selected_population = random.choices(
            sorted_population,
            weights=selection_probs,
            k=N
        )
        return selected_population

    def crossover_one_point(self, parent1, parent2):
        if random.random() > self.crossover_prob:
            return parent1, parent2
        
        cut_point = random.randint(1, self.chromosome_length - 1)
        
        child1_genotype = parent1.genotype[:cut_point] + parent2.genotype[cut_point:]
        child2_genotype = parent2.genotype[:cut_point] + parent1.genotype[cut_point:]
        
        child1 = Individual(self.items, self.capacity, child1_genotype)
        child2 = Individual(self.items, self.capacity, child2_genotype)
        
        return child1, child2

    def crossover_two_point(self, parent1, parent2):
        if random.random() > self.crossover_prob:
            return parent1, parent2
        
        p1, p2 = sorted(random.sample(range(1, self.chromosome_length), 2))
        
        gen1 = parent1.genotype
        gen2 = parent2.genotype
        
        child1_genotype = gen1[:p1] + gen2[p1:p2] + gen1[p2:]
        child2_genotype = gen2[:p1] + gen1[p1:p2] + gen2[p2:]
        
        child1 = Individual(self.items, self.capacity, child1_genotype)
        child2 = Individual(self.items, self.capacity, child2_genotype)
        
        return child1, child2

    def mutate(self, individual):
        genotype = individual.genotype[:]
        for i in range(self.chromosome_length):
            if random.random() < self.mutation_prob:
                genotype[i] = 1 - genotype[i]
        
        return Individual(self.items, self.capacity, genotype)

    def run_evolution(self, selection_method, crossover_method):
        
        print(f"Starting evolution: Selection={selection_method.__name__}, Crossover={crossover_method.__name__}")
        
        self.population = self.create_initial_population()
        best_fitness_history = []

        for i in range(self.iterations):
            best_in_gen = self.find_best_individual(self.population)
            best_fitness_history.append(best_in_gen.fitness)

            if (i + 1) % 20 == 0:
                print(f"Iteration {i+1}/{self.iterations}: Best Fitness = {best_in_gen.fitness}")

            parents_pool = selection_method()
            
            new_population = []
            
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(parents_pool, 2)
                
                child1, child2 = crossover_method(parent1, parent2)
                
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
            
            self.population = new_population
        
        print("Evolution finished.")
        return best_fitness_history
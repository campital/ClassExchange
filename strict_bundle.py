import random
import math
import numpy as np

class Student:
    def __init__(self, ranked_schedules, budget):
        self.ranked_schedules = ranked_schedules
        self.budget = budget
    def get_schedule_ranking(self):
        return self.ranked_schedules
    def get_budget(self):
        return self.budget
    def best_bundle(self, prices):
        for sched in self.ranked_schedules:
            indices = np.zeros(len(prices))
            indices[sched] = 1
            if np.dot(indices, prices) <= self.budget:
                return sched

def choose_schedule(n, k):
    return random.sample(range(k), n)

def generate_students(n, k):
    students = []
    for i in range(n):
        students.append(Student([choose_schedule(3, k) for j in range(3)], 1 + random.random() * (1 / n)))
    return students

def generate_capacities(n):
    return [random.randint(10, 30) for i in range(n)]

def generate_prices(n):
    return [random.random() * 1000 + 500 for i in range(n)]

num_classes = 30
num_students = 100
students = generate_students(num_students, num_classes)
capacities = tuple(generate_capacities(num_classes))

def clearing_error(prices, students, capacities):
    requested_enrollment = [0] * len(capacities)
    for s in students:
        # print(prices)
        curr_sched = s.best_bundle(prices)
        for i in curr_sched:
            requested_enrollment[i] += 1
    
    total_error_squared = 0
    for i in range(len(prices)):
        tentative = requested_enrollment[i] - capacities[i]
        if prices[i] == 0:
            tentative = max(tentative, 0)
        total_error_squared += tentative ** 2
    
    return (math.sqrt(total_error_squared), requested_enrollment)

def get_neighbors(students, capacities, prices):
    _, requested = clearing_error(prices, students, capacities)
    neighbors = []
    gradient = []
    for i in range(len(capacities)):
        tentative = requested[i] - capacities[i]
        if prices[i] == 0:
            tentative = max(tentative, 0)
        gradient.append(tentative)
    gradient = tuple(gradient)

    max_gradient = max(gradient)

    gradient_steps = [.1, .05, .01, .005, .001]
    for step in gradient_steps:
        curr_neighbor = tuple(np.add(prices, np.array(gradient) * (step / max_gradient)).clip(min = 0))
        err, enrollment = clearing_error(curr_neighbor, students, capacities)
        neighbors.append((err, enrollment, curr_neighbor))
    
    # IMPLEMENT INDIVIDUAL PRICE ADJUSTMENTS

    neighbors.sort(key=lambda x: x[0])

    return neighbors

def market_clear_search(students, capacities, max_budget):
    best_error = -1
    best_prices = None
    for iter in range(10000):
        p_curr = tuple([random.random() * max_budget for i in range(len(capacities))])
        search_error = clearing_error(p_curr, students, capacities)[0]
        tabu = set()
        c = 0
        while c < 5:
            neighbors = get_neighbors(students, capacities, p_curr)
            next_neighbor = None
            for neighbor in neighbors:
                if not neighbor[1] in tabu:
                    next_neighbor = neighbor
                    break

            if next_neighbor == None:
                c = 5
            else:
                p_curr = neighbor[2]
                tabu.add(neighbor[1])
                if neighbor[0] < search_error:
                    search_error = neighbor[0]
                    c = 0
                else:
                    c += 1
                
                if search_error < best_error or best_error == -1:
                    best_error = search_error
                    best_prices = neighbor

    return best_prices

print(market_clear_search(students, capacities, 1 + (1 / num_students)))

# Implement individual neighbor finding, MIP for bundles

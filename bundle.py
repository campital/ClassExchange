import random
import math
import numpy as np
import gurobipy as gp
from gurobipy import GRB

class Student:
    def __init__(self, start_bundles, bundle_bonus, budget, class_utility):
        self.class_utility = class_utility
        self.start_bundles = start_bundles
        self.bundle_bonus = bundle_bonus
        self.budget = budget
    def get_schedule_ranking(self):
        return self.ranked_schedules
    def get_budget(self):
        return self.budget
    def best_bundle(self, prices):
        model = gp.Model("BundleOptimization")

        model.Params.OutputFlag = 0

        items = list(self.class_utility.keys())
        x = model.addVars(items, vtype=GRB.BINARY, name="x")
        # bonus
        y = model.addVars(len(self.start_bundles), vtype=GRB.BINARY, name="y")
        # bundle enforcer
        z = model.addVars(len(self.start_bundles), vtype=GRB.BINARY, name="z")
    
        model.addConstr(
            gp.quicksum(prices[i] * x[i] for i in items) <= self.budget,
            name="budget"
        )

        model.addConstr(
            gp.quicksum(z) == 1,
            name="enforce_single"
        )

        for j, bundle in enumerate(self.start_bundles):
            for i in bundle:
                model.addConstr(y[j] <= x[i], name=f"b{j}_bonus_requires_item_{i}")
                model.addConstr(x[i] <= z[j], name=f"b{j}_requires_item_{i}")

        obj = (
            gp.quicksum(self.class_utility[i] * x[i] for i in items)
            + gp.quicksum(self.bundle_bonus[j] * y[j] for j in range(len(self.start_bundles)))
        )
        model.setObjective(obj, GRB.MAXIMIZE)
        model.optimize()

        selected_items = [i for i in items if x[i].X > 0.5]
        total_utility = model.ObjVal

        return selected_items, total_utility


def choose_schedule(n, k):
    return random.sample(range(k), n)

def generate_students(n, k):
    students = []
    for i in range(n):
        student_schedules = [choose_schedule(3, k) for j in range(3)]
        bonuses = np.random.uniform(0, 100, size=len(student_schedules))

        all_courses = set(course for sched in student_schedules for course in sched)
        utility = {course: np.random.uniform(1, 100) for course in all_courses}

        students.append(Student(student_schedules, bonuses, 1 + random.random() * (1 / n), utility))
    return students

def generate_capacities(n):
    return [random.randint(10, 30) for i in range(n)]

def generate_prices(n):
    return [random.random() * 1000 + 500 for i in range(n)]

num_classes = 30
num_students = 500
students = generate_students(num_students, num_classes)
capacities = tuple(generate_capacities(num_classes))

def clearing_error(prices, students, capacities):
    requested_enrollment = [0] * len(capacities)
    for s in students:
        curr_sched, best_util = s.best_bundle(prices)
        for i in curr_sched:
            requested_enrollment[i] += 1
    
    total_error_squared = 0
    for i in range(len(prices)):
        tentative = requested_enrollment[i] - capacities[i]
        if prices[i] == 0:
            tentative = max(tentative, 0)
        total_error_squared += tentative ** 2
    
    return (math.sqrt(total_error_squared), tuple(requested_enrollment))

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

    max_gradient = max([abs(x) for x in gradient])

    gradient_steps = [.1, .05, .01, .005, .001]
    for step in gradient_steps:
        curr_neighbor = tuple(np.add(prices, np.array(gradient) * (step / max_gradient)).clip(min = 0))
        err, enrollment = clearing_error(curr_neighbor, students, capacities)
        neighbors.append((err, enrollment, curr_neighbor))
    
    for i, diff in enumerate(gradient):
        if diff < 0:
            tmp_prices = list(prices)
            tmp_prices[i] = 0
            err, enrollment = clearing_error(tuple(tmp_prices), students, capacities)
            neighbors.append((err, enrollment, tuple(tmp_prices)))

    neighbors.sort(key=lambda x: x[0])

    return neighbors

def market_clear_search(students, capacities, max_budget, max_k=10000):
    best_error = -1
    best_prices = None
    for iter in range(max_k):
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
            print(best_error)

    return best_error, best_prices


err, prices = market_clear_search(students, capacities, 1 + (1 / num_students), 20)
print(err, prices)
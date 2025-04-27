import random
import math
import gurobipy as gp
from gurobipy import GRB

class Student:
    def __init__(self, ranked_schedules, budget):
        self.ranked_schedules = ranked_schedules
        self.budget = budget
    def get_schedule_ranking(self):
        return self.ranked_schedules
    def get_budget(self):
        return self.budget

def choose_weighted(prices):
    ind = random.random() * sum(prices)
    running = 0
    for i in range(len(prices)):
        if running + prices[i] > ind:
            return i
        running += prices[i]
    return len(prices) - 1

def choose_schedule(n, prices):
    sched = set()
    while len(sched) < n:
        sched.add(choose_weighted(prices))
    return sched

def generate_students(n, prices):
    students = []
    for i in range(n):
        students.append(Student([choose_schedule(5, prices) for j in range(3)], 1 + random.random() * (1 / n)))
    return students

def generate_capacities(n):
    return [random.randint(10, 30) for i in range(n)]

def generate_prices(n):
    return [random.random() * 1000 + 500 for i in range(n)]

num_classes = 30
num_students = 100
prices = generate_prices(num_classes)
students = generate_students(num_students, prices)
capacities = generate_capacities(num_classes)

print(prices)
print(capacities)

def optimize_schedules(students, prices, capacities):
    model = gp.Model("ScheduleOptimization")
    
    num_students = len(students)
    num_classes = len(prices)
    
    x = {}
    for i in range(num_students):
        for j, schedule in enumerate(students[i].get_schedule_ranking()):
            x[i, j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")
    
    y = {}
    for c in range(num_classes):
        y[c] = model.addVar(vtype=GRB.INTEGER, name=f"class_{c}")
    
    model.update()
    
    for i in range(num_students):
        model.addConstr(sum(x[i, j] for j in range(len(students[i].get_schedule_ranking()))) == 1)
    
    for c in range(num_classes):
        model.addConstr(
            y[c] == sum(
                x[i, j] for i in range(num_students) 
                for j, schedule in enumerate(students[i].get_schedule_ranking()) 
                if c in schedule
            )
        )
    
    for c in range(num_classes):
        model.addConstr(y[c] <= capacities[c])
    
    for i in range(num_students):
        for j, schedule in enumerate(students[i].get_schedule_ranking()):
            schedule_cost = sum(prices[c] for c in schedule)
            if schedule_cost > students[i].get_budget():
                model.addConstr(x[i, j] == 0)  # Disable if it exceeds budget
    
    obj_expr = gp.quicksum(
        x[i, j] * sum(prices[c] for c in schedule)
        for j, schedule in enumerate(students[i].get_schedule_ranking())
        for i in range(num_students)
    )
    model.setObjective(obj_expr, GRB.MAXIMIZE)
    
    model.optimize()
    
    assigned_schedules = []
    if model.status == GRB.OPTIMAL:
        total_expenditure = model.objVal
        for i in range(num_students):
            for j in range(len(students[i].get_schedule_ranking())):
                if x[i, j].X > 0.5:  # Binary variable is 1
                    assigned_schedules.append((i, students[i].get_schedule_ranking()[j]))
                    break
        
        class_enrollments = {c: int(y[c].X) for c in range(num_classes)}
        
        return {
            "success": True,
            "total_expenditure": total_expenditure,
            "assigned_schedules": assigned_schedules,
            "class_enrollments": class_enrollments
        }
    else:
        return {
            "success": False,
            "message": "No feasible solution found"
        }

result = optimize_schedules(students, prices, capacities)

if result["success"]:
    print(f"Optimization successful!")
    print(f"Total expenditure: ${result['total_expenditure']:.2f}")
    print(f"Number of students assigned: {len(result['assigned_schedules'])}/{num_students}")
    
    print("\nClass enrollment statistics:")
    for c, enrollment in result['class_enrollments'].items():
        print(f"Class {c}: {enrollment}/{capacities[c]} students (${prices[c]:.2f})")
else:
    print(f"Optimization failed: {result['message']}")

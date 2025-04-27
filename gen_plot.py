import matplotlib.pyplot as plt

with open('output_raw.txt', 'r') as f:
    data = [float(line.strip()) for line in f if line.strip()]

iterations = list(range(len(data)))

min_error = min(data)
min_index = data.index(min_error)

plt.style.use('seaborn-v0_8-darkgrid')
plt.figure(figsize=(10, 6))
plt.plot(iterations, data, marker='o', linestyle='-', color='tab:blue', markersize=6, linewidth=2)

plt.plot(min_index, min_error, marker='o', color='red', markersize=10, label='Best Error')
plt.annotate(f'Best Error: {min_error:.4f}',
             xy=(min_index, min_error),
             xytext=(min_index + len(data)*0.05, min_error),
             arrowprops=dict(arrowstyle='->', color='red'),
             fontsize=12,
             color='red')

plt.xlabel('Number of Iterations')
plt.ylabel('Market Clearing Error')
plt.title('Market Clearing Error vs. Algorithm Iterations')

plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.minorticks_on()

plt.tight_layout()

plt.savefig('error_plot.png', dpi=300)
plt.show()

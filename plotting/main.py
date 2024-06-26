import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Latency graph minimum and maximum values, in ms (for y-axis)
LATENCY_MIN = 20
LATENCY_MAX = 100
LATENCY_INCREMENT = 10

# Throughput graph minimum and maximum values, in ms (for y-axis)
THROUGHPUT_MIN = 0
THROUGHPUT_MAX = 30
THROUGHPUT_INCREMENT = 5

# The time, in ms, to check throughput for plotting
THROUGHPUT_INTERVAL = 1000

# Whether or not we trim, and if so, how much to trim
LATENCY_TRIM = True
L_TRIM_AMOUNT = 50
THROUGHPUT_TRIM = False
T_TRIM_AMOUNT = 50

# The columns in the data that are floats
FLOAT_COLS = [0]

# The file naming format
def BENCHMARK_FILE_FORMAT(file):
    return file.startswith('client') and file.endswith('.txt')

# Directories and file paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
RESULTS_DIR = os.path.join(PARENT_DIR, 'experiments_results')
PLOTS_DIR = os.path.join(PARENT_DIR, 'experiments_plots')

def main():
    first = True

    # Aggregate latencies
    latencies_trials = {}
    throughputs_trials = {}
    latencies_slow_trials = {}
    throughputs_slow_trials = {}

    # Go into each benchmarked system
    for root, dirs, files in os.walk(RESULTS_DIR):

        # HACK to ignore files not in sub-directories
        if first:
            first = False
            continue

        # Get the system name
        sys_name = root[root.rfind('/') + 1:]

        # Go through each individual benchmark
        benchmark_files = fetch_files(root, files)
        latencies = []
        throughputs = []
        for file_path, raw_data in benchmark_files:

            # Pre-process all the benchmark txt files for graphing
            timestamps = clean_data(tablify(raw_data))

            # Compute latency and throughput
            latencies.append(latency_arr(timestamps))
            throughputs.append(throughput_arr(timestamps))

        # Add to aggregate data sets
        if ('slow' in sys_name):
            throughputs_slow_trials.update({sys_name: throughputs})
            latencies_slow_trials.update({sys_name: latencies})
        else:
            throughputs_trials.update({sys_name: throughputs})
            latencies_trials.update({sys_name: latencies})

        # Plot latency and throughput
        plot_latency(latencies, sys_name)
        plot_throughput(throughputs, sys_name)

    # BW Plots
    box_whiskers_plot_latency(latencies_trials, "default")
    box_whiskers_plot_latency(latencies_slow_trials, "slow")
    box_whiskers_plot_throughput(throughputs_trials, "default")
    box_whiskers_plot_throughput1(throughputs_slow_trials, "slow")

    # 99th Latency Plots
    latency_dist_plot(latencies_slow_trials)


def fetch_files(root, files):
    txt_files = []

    for file in files:
        if BENCHMARK_FILE_FORMAT(file):
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                file_content = f.read()
            txt_files.append((file_path, file_content))

    return txt_files


def tablify(text):
    return [row.split() for row in text.strip().split('\n')]


def clean_data(data):
    def purge_non_data(data):
        return data[2:-1]

    def cols_to_float(arr, cols):
        return [[float(row[i]) if i in cols else row[i] for i in range(len(row))] for row in arr]

    def drop_second_col(arr):
        return [row[0] for row in arr]

    def col1_s_to_ms(arr):
        return [x * 1000 for x in arr]

    return col1_s_to_ms(drop_second_col(cols_to_float(purge_non_data(data), FLOAT_COLS)))


def latency_arr(arr):
    latency = []
    for i in range(1, len(arr)):
        latency.append([i, arr[i] - arr[i-1]])
    return latency_trim(latency)


def throughput_arr(arr):
    # Normalize for first timestamp being t=0
    start_time = arr[0]
    adjusted_timestamps = [timestamp - start_time for timestamp in arr]

    throughput = {}
    for timestamp in adjusted_timestamps:
        second = timestamp // THROUGHPUT_INTERVAL
        if second in throughput:
            throughput[second] += 1
        else:
            throughput[second] = 1

    return throughput_trim([[key, value] for key, value in throughput.items()])


def latency_trim(arr):
    if not LATENCY_TRIM: return arr
    else: return arr[L_TRIM_AMOUNT:-L_TRIM_AMOUNT] if len(arr) > (2 * L_TRIM_AMOUNT) else []


def throughput_trim(arr):
    if not THROUGHPUT_TRIM: return arr
    else: return arr[T_TRIM_AMOUNT:-T_TRIM_AMOUNT] if len(arr) > (2 * T_TRIM_AMOUNT) else []


def plot_latency(latency, name):
    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']

    plt.figure(figsize=(10, 6))

    for i, data in enumerate(latency):
        x = [point[0] for point in data]
        y = [point[1] for point in data]
        plt.plot(x, y, color=colors[i % len(colors)], label=f'Client {i+1}')

    plt.xlabel('Request Number')
    plt.ylabel('Latency')
    plt.title(f'Latency Plot for {name}')
    plt.legend()
    plt.grid(True)
    plt.ylim(LATENCY_MIN, LATENCY_MAX)
    plt.yticks(range(LATENCY_MIN, LATENCY_MAX + LATENCY_INCREMENT, LATENCY_INCREMENT))
    plt.savefig(os.path.join(PLOTS_DIR, f'{name}_latency.png'))


def plot_throughput(throughput, name):
    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']

    plt.figure(figsize=(10, 6))

    for i, data in enumerate(throughput):
        x = [point[0] for point in data]
        y = [point[1] for point in data]
        plt.plot(x, y, color=colors[i % len(colors)], label=f'Client {i+1}')

    plt.xlabel(f'Time (in units of {THROUGHPUT_INTERVAL} ms)')
    plt.ylabel('Throughput')
    plt.title(f'Throughput Plot for {name}')
    plt.legend()
    plt.grid(True)
    plt.ylim(THROUGHPUT_MIN, THROUGHPUT_MAX)
    plt.yticks(range(THROUGHPUT_MIN, THROUGHPUT_MAX + THROUGHPUT_INCREMENT, THROUGHPUT_INCREMENT))
    plt.savefig(os.path.join(PLOTS_DIR, f'{name}_throughput.png'))


def box_whiskers_plot_latency(throughput_trials, suffix):
    plt.figure(figsize=(20, 6))

    data = []
    labels = []

    for latency_name in throughput_trials:
        latency_values = throughput_trials[latency_name]
        for i in range(len(latency_values)):
            data.append(latency_values[i][1])
            labels.append(f'{latency_name} client {i + 1}')

    plt.boxplot(data, tick_labels = labels)
    plt.tight_layout()

    plt.title(f'Box and Whiskers Plot of Latency')
    plt.ylabel('Latencies')
    plt.savefig(os.path.join(PLOTS_DIR, f'latency_BWplot_{suffix}.png'), bbox_inches='tight')


def box_whiskers_plot_throughput(throughput_trials, suffix):
    plt.figure(figsize=(25, 10))

    data = []
    labels = []

    for throughput_name in throughput_trials:
        throughput_values = throughput_trials[throughput_name]
        for i in range(len(throughput_values)):
            data.append(throughput_values[i][1])
            labels.append(f'{throughput_name} client {i + 1}')

    plt.boxplot(data, tick_labels = labels)
    plt.tight_layout()

    plt.title(f'Box and Whiskers Plot of Throughput')
    plt.ylabel('Throughput')
    plt.savefig(os.path.join(PLOTS_DIR, f'throughput_BWplot_{suffix}.png'), bbox_inches='tight')


def box_whiskers_plot_throughput1(throughput_trials, suffix):
    grouped_data = {k: [[i[1] for i in j][50:200] for j in v] for k, v in throughput_trials.items()}

    # Some of the data is in the wrong order, so we need to swap them
    # grouped_data['multipaxos_slow'][1], grouped_data['multipaxos_slow'][2] = grouped_data['multipaxos_slow'][2], grouped_data['multipaxos_slow'][1]
    # grouped_data['robust_mencius_slow'][1], grouped_data['robust_mencius_slow'][2] = grouped_data['robust_mencius_slow'][2], grouped_data['robust_mencius_slow'][1]
    fig, ax = plt.subplots(figsize=(15, 8))

    # Define colors for each protocol
    colors = ['lightblue', 'lightgreen', 'lightcoral']

    # Create boxplots
    positions = []
    labels = []
    for i, (group, color) in enumerate(zip(grouped_data, colors)):
        pos = [i * 8 + j * 3 + 1 for j in range(len(grouped_data[group]))]  # Calculate positions with spacing
        positions.extend(pos)
        labels.extend([f'Client {j+1}' for j in range(len(grouped_data[group]))])
        box = ax.boxplot(grouped_data[group], positions=pos, widths=2, patch_artist=True)
        for patch in box['boxes']:
            patch.set_facecolor(color)

    # Customize the plot
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_title('Throughputs per Client per Protocol', fontsize=16)
    ax.set_xlabel('Protocols', fontsize=14)
    ax.set_ylabel('Throughput (Req/sec)', fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Add a legend
    handles = [plt.Line2D([0], [0], color=color, lw=4) for color in colors]
    ax.legend(handles, grouped_data.keys(), title='Protocols', loc='lower right', fontsize=12, title_fontsize='13')

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f'throughput_BWplot_{suffix}.png'))


def latency_dist_plot(latency_trials):
    plt.figure(figsize=(10, 6))
    palette = sns.color_palette("husl", len(latency_trials))

    for trial_name in latency_trials:
        trial = latency_trials[trial_name]
        trials_unified = np.concatenate(trial, axis=0)
        trials_second_col = trials_unified[:, 1:]
        trials_sorted = trials_second_col[trials_second_col[:, 0].argsort()]
        sns.lineplot(data=trials_sorted)

    plt.title("Latency Distributions")
    plt.xlabel("Index")
    plt.ylabel("Values")
    plt.legend()
    plt.savefig(os.path.join(PLOTS_DIR, f'latency_distribution_slowtrials.png'))


if __name__ == "__main__":
    main()

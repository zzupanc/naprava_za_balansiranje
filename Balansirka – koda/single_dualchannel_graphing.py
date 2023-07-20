import matplotlib.pyplot as plt
import csv


def channel_count():
    while True:
        options_dict = {'1': 1, '2': 2}
        while True:
            num_channels = input("Is the data logged single or dual channel ['1' or '2']?: ")
            if num_channels in options_dict:
                return options_dict[num_channels]
            print("Invalid response.")


def draw_graphs():

    no_of_channels = channel_count()

    y_channel0 = []
    y_channel1 = []

    with open('fotocelica_meritve.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        if no_of_channels == 2:
            for i, row in enumerate(csv_reader):
                if i % 2 == 0:
                    for value in row:
                        y_channel0.append(float(value))
                else:
                    for value in row:
                        y_channel1.append(float(value))

        elif no_of_channels == 1:
            for row in csv_reader:
                for value in row:
                    y_channel0.append(float(value))

    x = range(1, len(y_channel0) + 1)
    v_max = 5
    inverted_y = [v_max - measuremet for measuremet in y_channel0]

    plt.plot(x, inverted_y, label='Channel 0', c='b')
    if no_of_channels == 2:
        plt.plot(x, y_channel1, label='Channel 1', c='g')
    plt.xlabel('Sample')
    plt.ylabel('Sensitivity [mV/N]')
    plt.title('Data Plot')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    draw_graphs()

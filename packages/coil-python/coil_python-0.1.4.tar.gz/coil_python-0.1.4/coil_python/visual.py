import matplotlib.pyplot as plt

def show_charts(stats):
    labels = ["Original", "Encoded"]

    tokens = [
        stats["original"]["tokens"],
        stats["encoded"]["tokens"]
    ]

    bytes_ = [
        stats["original"]["bytes"],
        stats["encoded"]["bytes"]
    ]

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))

    ax[0].bar(labels, tokens)
    ax[0].set_title("Token Count")

    ax[1].bar(labels, bytes_)
    ax[1].set_title("Byte Size")

    plt.tight_layout()
    plt.show()

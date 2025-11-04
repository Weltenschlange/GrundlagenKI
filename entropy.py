import math

def entropy(counts):

    total = sum(counts)
    if total == 0:
        return 0.0

    entropy_value = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            entropy_value -= p * math.log2(p)
    return round(entropy_value, 3)


# Example usage
if __name__ == "__main__":
    dataset = [0, 1]


    print("Entropy (dataset):", entropy(dataset))


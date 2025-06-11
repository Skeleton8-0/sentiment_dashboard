import matplotlib.pyplot as plt

def display_text_analysis(results):
    for r in results:
        print(f"\nText: {r['text']}")
        if "error" in r:
            print(f"Error: {r['error']}")
        else:
            print(f"Sentiment:")
            for s in r['sentiment']:
                print(f"  {s['label'].capitalize()}: {s['score']:.2f}")
            print(f"Keywords: {', '.join(r['keywords'])}")

def plot_sentiment_bar(results):
    for r in results:
        if "sentiment" not in r:
            continue
        labels = [item['label'].capitalize() for item in r['sentiment']]
        scores = [item['score'] for item in r['sentiment']]
        plt.figure(figsize=(6, 3))
        plt.bar(labels, scores, color=['red', 'grey', 'green'])
        plt.title(f"Sentiment for: \"{r['text'][:30]}...\"")
        plt.ylabel("Score")
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.show()

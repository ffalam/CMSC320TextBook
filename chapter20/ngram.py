import marimo

__generated_with = "0.13.13-dev18"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import re
    from typing import List, Tuple


    def create_ngrams(text: str, n: int) -> List[str]:
        """Create n-grams from input text."""
        if not text.strip():
            return []

        # Clean and tokenize the text
        # Remove extra whitespace and split into words
        words = text.strip().split()

        if n > len(words):
            return []

        # Generate n-grams
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = " ".join(words[i : i + n])
            ngrams.append(ngram)

        return ngrams


    # Create the text input with default lorem ipsum
    text_input = mo.ui.text_area(
        value="Lorem ipsum dolor sit amet consectetur adipiscing elit sed do",
        label="Enter text for n-gram analysis:",
        placeholder="Type your text here...",
        rows=3,
    )

    # Create the slider for n-gram size (starting from 1 to avoid zero)
    ngram_slider = mo.ui.slider(
        start=1, stop=10, value=2, step=1, label="N-gram size:", show_value=True
    )

    mo.hstack(
        [
            mo.vstack([mo.md("text_input"), text_input]),
            mo.vstack([mo.md("ngram_slider"), ngram_slider]),
        ]
    )
    return create_ngrams, mo, ngram_slider, text_input


@app.cell(hide_code=True)
def _(create_ngrams, mo, ngram_slider, text_input):
    ngrams = create_ngrams(text_input.value, ngram_slider.value)

    # Create a formatted display of the n-grams
    ngram_list = mo.ui.table(
        data=[{"N-gram": ngram, "Index": i + 1} for i, ngram in enumerate(ngrams)],
        label=f"{ngram_slider.value}-grams from your text",
    )

    mo.md(
        f""""
    ## Results

    **Found {len(ngrams)} {ngram_slider.value}-grams:**

    {ngram_list}

    ### Summary:
    - **Text length:** {len(text_input.value.split())} words
    - **N-gram size:** {ngram_slider.value}
    - **Total {ngram_slider.value}-grams:** {len(ngrams)}
    """
    )
    return


if __name__ == "__main__":
    app.run()

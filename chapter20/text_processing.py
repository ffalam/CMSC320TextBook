import marimo

__generated_with = "0.13.13-dev18"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import re
    import string
    from typing import List

    # Sample text for demonstration
    default_text = "Hello World! This is a SAMPLE text with Numbers123, punctuation!!! And some Common words like 'the', 'and', 'is'. Running, jumped, and better words too."

    text_input = mo.ui.text_area(
        value=default_text,
        label="Enter text to preprocess:",
        placeholder="Type or paste your text here...",
        rows=3,
        full_width=True
    )

    text_input
    return mo, re, text_input


@app.cell(hide_code=True)
def _(mo, re, text_input):
    def preprocess_text(text: str) -> dict:
        """Apply each preprocessing step and return results"""

        # Original text
        original = text

        # Step 1: Text Cleaning (remove extra whitespace, normalize)
        cleaned = re.sub(r'\s+', ' ', text.strip())

        # Step 2: Tokenization
        tokens = cleaned.split()

        # Step 3: Lowercasing
        lowercased = cleaned.lower()
        lowercased_tokens = [token.lower() for token in tokens]

        # Step 4: Stop-word removal
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 
            'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 
            'were', 'will', 'with', 'this', 'that', 'these', 'those', 'i', 'me', 
            'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours'
        }

        no_stopwords = [token for token in lowercased_tokens if token.lower() not in stop_words]

        # Step 5: Stemming (simple rule-based stemming)
        def simple_stem(word):
            """Basic stemming rules"""
            if word.endswith('ing'):
                return word[:-3]
            elif word.endswith('ed'):
                return word[:-2]
            elif word.endswith('er'):
                return word[:-2]
            elif word.endswith('est'):
                return word[:-3]
            elif word.endswith('ly'):
                return word[:-2]
            elif word.endswith('s') and len(word) > 3:
                return word[:-1]
            return word

        stemmed = [simple_stem(token) for token in no_stopwords]

        # Step 6: Special Character Removal
        def remove_special_chars(token):
            # Remove punctuation and numbers, keep only alphabetic characters
            return re.sub(r'[^a-zA-Z]', '', token)

        no_special_chars = [remove_special_chars(token) for token in stemmed if remove_special_chars(token)]

        return {
            'original': original,
            'cleaned': cleaned,
            'tokens': tokens,
            'lowercased': lowercased,
            'lowercased_tokens': lowercased_tokens,
            'no_stopwords': no_stopwords,
            'stemmed': stemmed,
            'final': no_special_chars
        }

    def display_preprocessing_steps(text: str):
        """Display each preprocessing step with explanations"""

        if not text.strip():
            return mo.md("Please enter some text to see the preprocessing steps.")

        results = preprocess_text(text)

        return mo.vstack([
            mo.md("# NLP Text Preprocessing Steps"),

            mo.md("## Original Text"),
            mo.md(f"**Input:** `{results['original']}`"),

            mo.md("## Step 1: Text Cleaning"),
            mo.md("**Purpose:** Removing noise, unwanted symbols, and irrelevant data."),
            mo.md(f"**Result:** `{results['cleaned']}`"),
            mo.md("*Normalized whitespace and basic cleanup*"),

            mo.md("## Step 2: Tokenization"),
            mo.md("**Purpose:** Splitting text into words or tokens."),
            mo.md(f"**Tokens:** `{results['tokens']}`"),
            mo.md(f"*Split into {len(results['tokens'])} tokens*"),

            mo.md("## Step 3: Lowercasing"),
            mo.md("**Purpose:** Making all text lowercase to treat 'Apple' and 'apple' as the same word."),
            mo.md(f"**Result:** `{results['lowercased']}`"),
            mo.md(f"**Tokens:** `{results['lowercased_tokens']}`"),

            mo.md("## Step 4: Stop-word Removal"),
            mo.md("**Purpose:** Removing common, unimportant words like 'and', 'the', 'is', etc."),
            mo.md(f"**Result:** `{results['no_stopwords']}`"),
            mo.md(f"*Removed {len(results['lowercased_tokens']) - len(results['no_stopwords'])} stop words*"),

            mo.md("## Step 5: Stemming"),
            mo.md("**Purpose:** Reducing words to their root form (e.g., 'running' → 'run')."),
            mo.md(f"**Result:** `{results['stemmed']}`"),
            mo.md("*Applied basic stemming rules*"),

            mo.md("## Step 6: Special Character Removal"),
            mo.md("**Purpose:** Removing punctuation, numbers, and other non-alphabetic characters."),
            mo.md(f"**Final Result:** `{results['final']}`"),
            mo.md(f"*Final preprocessed tokens: {len(results['final'])} clean words*"),

            mo.md("---"),
            mo.md("### Summary"),
            mo.md(f"**Original:** {len(results['tokens'])} tokens → **Final:** {len(results['final'])} clean tokens"),
            mo.md("The text is now ready for NLP model training or analysis!")
        ])

    # Create the interactive display
    text_input
    display_preprocessing_steps(text_input.value)
    return


if __name__ == "__main__":
    app.run()

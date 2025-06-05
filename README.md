# CMSC320TextBook: CMSC 320: Intro to Data Science – Interactive Textbook Project


Welcome to the official repository for our free, interactive textbook for CMSC 320: Introduction to Data Science, created especially for Dr. Fardina Alam’s section at the University of Maryland.

## Project Goal: 
Our mission is to build a modern, accessible, and engaging textbook for CMSC 320 that goes beyond the traditional static format. This open resource will include:

* Interactive visualizations

* Step-by-step explanations

* Hands-on code examples

* Clean, student-friendly summaries

* Live, editable notebooks

This is a collaborative and evolving effort, aiming to support current and future students by making complex concepts more understandable and engaging.

## Who Is It For?: 
This resource is designed primarily for students in Dr. Fardina Alam's section of CMSC 320, but is open for use by anyone learning data science and seeking an interactive alternative to traditional textbooks.

## Proposed Features: 

* Visual Learning: Charts, graphs, and widgets to reinforce concepts

* Concept Highlights: Key points and takeaways per topic

* Live Demos: Code you can run and modify directly

* Note-Friendly Format: Easy to annotate and revise

## Topics Covered: 

Check https://cmsc320.github.io/ 

## Contributors: 
* Fardina Alam
* Gavin Hung

## Project Status: 
This textbook is a work in progress. We're actively adding content and improving interactivity with each contribution.

## Usage

### Step 1: Download the Jupyter Notebooks

```sh
chmod +x ./download_notebooks.sh
./download_notebooks.sh
```

### Step 2: Building the Jupyter Book

#### Option 1: jupyter-book CLI

```sh
pip install -U jupyter-book
jupyter-book build .
```

#### Option 2: Docker Compose

```sh
docker compose up
docker compose down --volumes --rmi local
```

#### Option 3: Docker

```sh
docker build -t textbook .
docker run --rm -v "$(pwd)":/usr/src/app textbook

docker stop textbook
docker rm textbook
docker rmi textbook
```

### Step 3: Open the Jupyter Book

Navigate to `_build/html/index.html`
